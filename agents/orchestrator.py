"""Campaign Orchestrator — coordinates all agents into a single pipeline.

Flow:
  Research → Strategy → Creatives (parallel) → Email/SMS → n8n Workflows → GHL Setup
  All outputs are written to output/campaigns/<campaign_slug>/
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from slugify import slugify

from agents.research_agent import run_research
from agents.strategy_agent import build_strategy
from agents.creative_agent import (
    generate_google_ads,
    generate_meta_ads,
    generate_tiktok_ads,
    generate_lead_magnet,
)
from agents.email_sms_agent import (
    generate_email_sequence,
    generate_sms_sequence,
    generate_retargeting_emails,
)
from agents.n8n_agent import generate_all_workflows
from agents.ghl_agent import setup_ghl_account


class CampaignOrchestrator:
    """Coordinates the full campaign generation pipeline."""

    def __init__(self, base_output_dir: str = "output/campaigns"):
        self.base_output_dir = Path(base_output_dir)

    async def generate_campaign(
        self,
        business: str,
        target_audience: str,
        campaign_goal: str,
        monthly_budget: int,
        competitor_keywords: list[str] | None = None,
        campaign_name: str | None = None,
        output_dir: str | None = None,
        on_progress: Any = None,
    ) -> dict[str, Any]:
        """Run the full campaign generation pipeline.

        Args:
            business: Description of the business/service
            target_audience: Who to target
            campaign_goal: What to achieve (leads, sales, etc.)
            monthly_budget: Monthly ad spend in USD
            competitor_keywords: Keywords to research competitors
            campaign_name: Optional name; auto-generated if not provided
            output_dir: Override output directory
            on_progress: Optional async callback(step: str, pct: int)
        """

        def _progress(step: str, pct: int):
            if on_progress:
                asyncio.create_task(on_progress(step, pct))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        slug = slugify(campaign_name or f"{business[:30]}-{timestamp}")
        campaign_dir = Path(output_dir or self.base_output_dir) / slug
        campaign_dir.mkdir(parents=True, exist_ok=True)

        results: dict[str, Any] = {
            "campaign_slug": slug,
            "output_dir": str(campaign_dir),
            "steps": {},
        }

        # ─── Step 1: Research ─────────────────────────────────────────────────
        _progress("research", 5)
        research_result = await run_research(
            business_description=business,
            target_audience=target_audience,
            competitor_keywords=competitor_keywords or [],
        )
        results["steps"]["research"] = research_result["success"]
        _save(campaign_dir / "01_research_report.md", research_result["report"])

        # ─── Step 2: Strategy ─────────────────────────────────────────────────
        _progress("strategy", 20)
        strategy_result = await build_strategy(
            business_description=business,
            target_audience=target_audience,
            campaign_goal=campaign_goal,
            monthly_budget=monthly_budget,
            research_report=research_result["report"],
        )
        results["steps"]["strategy"] = strategy_result["success"]
        _save(campaign_dir / "02_strategy.md", strategy_result["strategy"])

        strategy_text = strategy_result["strategy"]

        # ─── Step 3: Creatives (parallel) ─────────────────────────────────────
        _progress("creatives", 35)

        # Extract ICP and offer summaries from strategy
        icp_summary = _extract_section(strategy_text, "Ideal Customer Profile") or target_audience
        offer = _extract_section(strategy_text, "Unique Mechanism") or campaign_goal

        ads_dir = campaign_dir / "03_ads"
        ads_dir.mkdir(exist_ok=True)

        google_result, meta_result, tiktok_result, lm_result = await asyncio.gather(
            generate_google_ads(
                icp_summary=icp_summary,
                offer=offer,
                keywords=competitor_keywords or ["marketing agency", "lead generation"],
            ),
            generate_meta_ads(
                icp_summary=icp_summary,
                offer=offer,
                lead_magnet="Free Lead Generation Playbook",
            ),
            generate_tiktok_ads(
                icp_summary=icp_summary,
                offer=offer,
                lead_magnet="Free Lead Generation Playbook",
            ),
            generate_lead_magnet(
                icp_summary=icp_summary,
                pain_points="Not enough qualified leads, high CAC, unpredictable pipeline",
                desired_outcome="Consistent flow of qualified leads on autopilot",
            ),
        )

        _save_json(ads_dir / "google_ads.json", google_result.get("creatives", {}))
        _save_json(ads_dir / "meta_ads.json", meta_result.get("creatives", {}))
        _save_json(ads_dir / "tiktok_ads.json", tiktok_result.get("creatives", {}))
        _save_json(campaign_dir / "04_lead_magnet" / "lead_magnet.json", lm_result.get("lead_magnet", {}))

        results["steps"]["creatives"] = all([
            google_result["success"],
            meta_result["success"],
            tiktok_result["success"],
            lm_result["success"],
        ])

        lead_magnet_title = (
            lm_result.get("lead_magnet", {})
            .get("primary_lead_magnet", {})
            .get("title", "Free Marketing Playbook")
        )

        # ─── Step 4: Email & SMS (parallel) ───────────────────────────────────
        _progress("email_sms", 60)

        email_result, sms_result, retarget_email_result = await asyncio.gather(
            generate_email_sequence(
                business_description=business,
                icp_summary=icp_summary,
                lead_magnet_title=lead_magnet_title,
                offer=offer,
            ),
            generate_sms_sequence(
                business_description=business,
                icp_summary=icp_summary,
                lead_magnet_title=lead_magnet_title,
                offer=offer,
            ),
            generate_retargeting_emails(
                icp_summary=icp_summary,
                offer=offer,
                reason_they_didnt_convert=(
                    "No time, unsure of ROI, haven't finished the lead magnet, "
                    "comparing with competitors"
                ),
            ),
        )

        email_dir = campaign_dir / "05_email_sequences"
        sms_dir = campaign_dir / "06_sms_sequences"
        email_dir.mkdir(exist_ok=True)
        sms_dir.mkdir(exist_ok=True)

        _save_json(email_dir / "nurture_sequence.json", email_result.get("email_sequence", {}))
        _save_json(sms_dir / "sms_sequence.json", sms_result.get("sms_sequence", {}))
        _save_json(email_dir / "retargeting_emails.json", retarget_email_result.get("retargeting_emails", {}))

        results["steps"]["email_sms"] = all([
            email_result["success"],
            sms_result["success"],
            retarget_email_result["success"],
        ])

        # ─── Step 5: n8n Workflows ─────────────────────────────────────────────
        _progress("n8n_workflows", 78)

        n8n_dir = campaign_dir / "07_n8n_workflows"
        n8n_result = await generate_all_workflows(
            email_sequence=email_result.get("email_sequence", {}),
            output_dir=n8n_dir,
        )
        results["steps"]["n8n"] = n8n_result["success"]

        # ─── Step 6: GHL Setup ─────────────────────────────────────────────────
        _progress("ghl_setup", 88)

        ghl_result = await setup_ghl_account(
            pipeline_name=f"{business[:40]} — Lead Pipeline",
            email_sequence=email_result.get("email_sequence", {}),
            sms_sequence=sms_result.get("sms_sequence", {}),
            output_dir=campaign_dir,
        )
        results["steps"]["ghl"] = ghl_result["success"]

        # ─── Summary ──────────────────────────────────────────────────────────
        _progress("summary", 96)
        summary = _build_summary(
            slug, business, campaign_goal, monthly_budget, campaign_dir, results
        )
        _save(campaign_dir / "campaign_summary.md", summary)

        _progress("done", 100)

        results["success"] = all(results["steps"].values())
        results["output_path"] = str(campaign_dir)
        results["summary"] = summary

        return results


# ── Helpers ───────────────────────────────────────────────────────────────────

def _save(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content or "", encoding="utf-8")


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _extract_section(text: str, section_title: str) -> str:
    """Extract text under a markdown section heading."""
    lines = text.split("\n")
    capturing = False
    out = []
    for line in lines:
        if section_title.lower() in line.lower() and line.startswith("#"):
            capturing = True
            continue
        if capturing and line.startswith("#"):
            break
        if capturing:
            out.append(line)
    return "\n".join(out).strip()


def _build_summary(
    slug: str,
    business: str,
    goal: str,
    budget: int,
    output_dir: Path,
    results: dict,
) -> str:
    steps_status = "\n".join(
        f"- {'✅' if v else '❌'} {k.replace('_', ' ').title()}"
        for k, v in results.get("steps", {}).items()
    )

    return f"""# Campaign Package Summary

**Campaign:** {slug}
**Business:** {business}
**Goal:** {goal}
**Monthly Budget:** ${budget:,}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Generation Status
{steps_status}

---

## Package Contents

| Folder | Contents |
|--------|----------|
| `01_research_report.md` | Competitor ad analysis & market insights |
| `02_strategy.md` | Full-funnel strategy & 90-day roadmap |
| `03_ads/google_ads.json` | Google RSAs + PMax assets |
| `03_ads/meta_ads.json` | Facebook/Instagram ads + video scripts |
| `03_ads/tiktok_ads.json` | TikTok ad scripts |
| `04_lead_magnet/` | Lead magnet concept + landing page copy |
| `05_email_sequences/` | 14-email nurture + 5-email retargeting |
| `06_sms_sequences/` | Immediate + 7-day SMS drip |
| `07_n8n_workflows/` | Importable n8n workflow JSONs |
| `08_ghl_setup/` | GHL pipeline config + setup guide |

---

## Quick Start

1. **Review** `02_strategy.md` to confirm the positioning and funnel
2. **Import** n8n workflows from `07_n8n_workflows/` (see `00_import_manifest.json`)
3. **Follow** `08_ghl_setup/setup_guide.md` to configure GoHighLevel
4. **Upload** ad creatives from `03_ads/` to each platform
5. **Set up** the lead magnet from `04_lead_magnet/`
6. **Test** the full funnel with a real form submission before scaling

---

## Next Steps for Optimization
- A/B test 3 ad angles simultaneously; pause losers after 1,000 impressions each
- Monitor email open rates — aim for >30% on first 3 emails
- Add video testimonials to retargeting ads after week 2
- Review and adjust email sequence based on click-through data at day 14
"""
