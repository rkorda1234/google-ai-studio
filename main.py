#!/usr/bin/env python3
"""Digital Marketing Campaign Generator — CLI entry point.

Usage:
  python main.py generate          # Interactive full campaign generation
  python main.py research          # Research only
  python main.py creative          # Generate creatives only

Run `python main.py --help` for all options.
"""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich import print as rprint

from config import settings

console = Console()


def _check_env():
    missing = settings.validate()
    if missing:
        console.print(
            f"[bold red]Missing required environment variables: {', '.join(missing)}[/bold red]\n"
            "Copy .env.example to .env and fill in your credentials."
        )
        sys.exit(1)


@click.group()
def cli():
    """
    \b
    ╔══════════════════════════════════════════════════════╗
    ║  Digital Marketing Campaign Generator                ║
    ║  Powered by Claude AI                               ║
    ╚══════════════════════════════════════════════════════╝

    Generates full-funnel campaigns: research → strategy → ads
    → email/SMS sequences → n8n workflows → GHL setup.
    """
    pass


@cli.command()
@click.option(
    "--business",
    prompt="📋 Describe your business/service",
    help="What your agency offers",
)
@click.option(
    "--target",
    prompt="🎯 Target audience",
    help="Who you want to reach (e.g. 'B2B SaaS founders with 10-50 employees')",
)
@click.option(
    "--goal",
    prompt="🏆 Campaign goal",
    default="book discovery calls and generate qualified leads",
    help="What you want to achieve",
)
@click.option(
    "--budget",
    prompt="💰 Monthly ad budget (USD)",
    type=int,
    default=3000,
    help="Total monthly spend across all platforms",
)
@click.option(
    "--keywords",
    prompt="🔍 Competitor keywords (comma-separated, or press Enter to skip)",
    default="",
    help="Keywords to research competitors with",
)
@click.option(
    "--name",
    default=None,
    help="Campaign name (auto-generated if not set)",
)
@click.option(
    "--output",
    default="output/campaigns",
    help="Output directory",
)
def generate(business, target, goal, budget, keywords, name, output):
    """Generate a complete full-funnel campaign package.

    Runs all agents: research → strategy → ads → email/SMS → n8n → GHL setup.
    """
    _check_env()

    console.print(Panel.fit(
        f"[bold green]Campaign Generation Started[/bold green]\n\n"
        f"[cyan]Business:[/cyan] {business}\n"
        f"[cyan]Target:[/cyan] {target}\n"
        f"[cyan]Goal:[/cyan] {goal}\n"
        f"[cyan]Budget:[/cyan] ${budget:,}/month",
        title="🚀 Marketing Campaign Generator",
    ))

    kw_list = [k.strip() for k in keywords.split(",") if k.strip()]

    progress_steps = {
        "research": ("🔍 Researching competitor ads...", 0),
        "strategy": ("📊 Building campaign strategy...", 20),
        "creatives": ("✏️  Generating ad creatives (Google, Meta, TikTok)...", 35),
        "email_sms": ("📧 Writing email & SMS sequences...", 60),
        "n8n_workflows": ("⚙️  Building n8n workflows...", 78),
        "ghl_setup": ("🏗️  Setting up GoHighLevel...", 88),
        "summary": ("📝 Writing campaign summary...", 96),
        "done": ("✅ Complete!", 100),
    }

    current_task = None

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Starting...", total=100)

        async def on_progress(step: str, pct: int):
            desc, _ = progress_steps.get(step, (step, pct))
            progress.update(task, description=desc, completed=pct)

        async def run():
            from agents.orchestrator import CampaignOrchestrator
            orch = CampaignOrchestrator(base_output_dir=output)
            return await orch.generate_campaign(
                business=business,
                target_audience=target,
                campaign_goal=goal,
                monthly_budget=budget,
                competitor_keywords=kw_list,
                campaign_name=name,
                on_progress=on_progress,
            )

        result = asyncio.run(run())

    if result["success"]:
        _print_success(result)
    else:
        console.print(f"\n[bold yellow]Campaign generated with some warnings.[/bold yellow]")
        _print_success(result)


@cli.command()
@click.option("--keywords", prompt="🔍 Keywords to research", help="Comma-separated")
@click.option("--business", prompt="📋 Business description", help="Your agency")
@click.option("--output", default="output/research", help="Output directory")
def research(keywords, business, output):
    """Research competitor ads only — no full campaign generation."""
    _check_env()

    kw_list = [k.strip() for k in keywords.split(",") if k.strip()]

    with console.status("[bold green]Researching competitor ads..."):
        async def run():
            from agents.research_agent import run_research
            return await run_research(
                business_description=business,
                target_audience="marketing agency owners and entrepreneurs",
                competitor_keywords=kw_list,
            )
        result = asyncio.run(run())

    if result["success"]:
        out = Path(output)
        out.mkdir(parents=True, exist_ok=True)
        report_path = out / "research_report.md"
        report_path.write_text(result["report"], encoding="utf-8")
        console.print(f"[bold green]Research saved to:[/bold green] {report_path}")
        console.print("\n" + "─" * 60)
        console.print(result["report"][:2000])
        if len(result["report"]) > 2000:
            console.print(f"\n[dim]... (see {report_path} for full report)[/dim]")
    else:
        console.print("[bold red]Research failed.[/bold red]")


@cli.command()
@click.option("--business", prompt="📋 Business description")
@click.option("--target", prompt="🎯 Target audience")
@click.option("--offer", prompt="🎁 Your offer / CTA")
@click.option(
    "--platform",
    type=click.Choice(["google", "meta", "tiktok", "all"]),
    default="all",
    prompt="📱 Platform",
)
@click.option("--output", default="output/creatives")
def creative(business, target, offer, platform, output):
    """Generate ad creatives for specific platforms."""
    _check_env()

    out_dir = Path(output)
    out_dir.mkdir(parents=True, exist_ok=True)

    async def run():
        import json
        from agents.creative_agent import (
            generate_google_ads, generate_meta_ads, generate_tiktok_ads
        )
        tasks = {}
        if platform in ("google", "all"):
            tasks["google"] = generate_google_ads(target, offer, ["marketing agency"])
        if platform in ("meta", "all"):
            tasks["meta"] = generate_meta_ads(target, offer, "Free Playbook")
        if platform in ("tiktok", "all"):
            tasks["tiktok"] = generate_tiktok_ads(target, offer, "Free Playbook")

        results = {}
        for name, coro in tasks.items():
            with console.status(f"[bold green]Generating {name} ads..."):
                r = await coro
                results[name] = r
                path = out_dir / f"{name}_ads.json"
                path.write_text(json.dumps(r.get("creatives", {}), indent=2))
                console.print(f"[green]✓[/green] {name} ads → {path}")

        return results

    asyncio.run(run())
    console.print(f"\n[bold green]Creatives saved to:[/bold green] {out_dir}")


def _print_success(result: dict):
    out = result.get("output_path", "output/")

    table = Table(title="📦 Campaign Package", show_header=True, header_style="bold cyan")
    table.add_column("Component", style="green")
    table.add_column("Status")
    table.add_column("File")

    file_map = {
        "research": ("Research Report", "01_research_report.md"),
        "strategy": ("Campaign Strategy", "02_strategy.md"),
        "creatives": ("Ad Creatives", "03_ads/"),
        "email_sms": ("Email & SMS", "05_email_sequences/ + 06_sms_sequences/"),
        "n8n": ("n8n Workflows", "07_n8n_workflows/"),
        "ghl": ("GHL Setup", "08_ghl_setup/setup_guide.md"),
    }

    for key, (label, file_hint) in file_map.items():
        status = "✅" if result.get("steps", {}).get(key) else "⚠️"
        table.add_row(label, status, file_hint)

    console.print(table)
    console.print(f"\n[bold green]Output directory:[/bold green] {out}")
    console.print("\n[bold]Quick start:[/bold]")
    console.print(f"  1. Review strategy: [cyan]{out}/02_strategy.md[/cyan]")
    console.print(f"  2. Import n8n workflows: [cyan]{out}/07_n8n_workflows/[/cyan]")
    console.print(f"  3. Follow GHL guide: [cyan]{out}/08_ghl_setup/setup_guide.md[/cyan]")
    console.print(f"  4. Upload ads to platforms: [cyan]{out}/03_ads/[/cyan]")


if __name__ == "__main__":
    cli()
