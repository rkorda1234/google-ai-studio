"""Background campaign generation job.

Runs the orchestrator in a thread so Slack's 3-second timeout is never hit.
After generation: auto-imports n8n workflows, triggers GHL setup,
and posts all campaign files directly into the Slack thread.
"""

from __future__ import annotations

import asyncio
import json
import threading
from pathlib import Path
from typing import Any

from slack_sdk import WebClient

from slack_bot.blocks import progress_update, results_message, error_message


def run_campaign_in_background(
    client: WebClient,
    channel_id: str,
    ts: str,
    user_id: str,
    campaign_params: dict[str, Any],
) -> None:
    """Kick off campaign generation in a daemon thread."""
    thread = threading.Thread(
        target=_run,
        args=(client, channel_id, ts, user_id, campaign_params),
        daemon=True,
    )
    thread.start()


def _run(client, channel_id, ts, user_id, params):
    asyncio.run(_async_run(client, channel_id, ts, user_id, params))


async def _async_run(
    client: WebClient,
    channel_id: str,
    ts: str,
    user_id: str,
    params: dict[str, Any],
) -> None:
    from agents.orchestrator import CampaignOrchestrator
    from agents.n8n_agent import upload_workflows_to_n8n

    last_pct = [0]

    async def on_progress(step: str, pct: int):
        if pct - last_pct[0] >= 20 or pct == 100:
            last_pct[0] = pct
            step_labels = {
                "research": "🔍 Researching competitor ads",
                "strategy": "📊 Building campaign strategy",
                "creatives": "✏️ Generating ad creatives",
                "email_sms": "📧 Writing email & SMS sequences",
                "n8n_workflows": "⚙️ Building n8n workflows",
                "ghl_setup": "🏗️ Setting up GoHighLevel",
                "summary": "📝 Finalizing campaign package",
                "done": "✅ Done!",
            }
            label = step_labels.get(step, step)
            try:
                client.chat_update(
                    channel=channel_id,
                    ts=ts,
                    blocks=progress_update(label, pct, user_id),
                    text=f"{label} — {pct}%",
                )
            except Exception:
                pass

    try:
        orch = CampaignOrchestrator()
        result = await orch.generate_campaign(
            business=params["business"],
            target_audience=params["target"],
            campaign_goal=params["goal"],
            monthly_budget=params["budget"],
            competitor_keywords=params.get("keywords", []),
            on_progress=on_progress,
        )

        out_dir = Path(result["output_path"])

        # ── Auto-import n8n workflows ──────────────────────────────────────
        _update(client, channel_id, ts, user_id, "⚙️ Auto-importing n8n workflows…", 92)
        n8n_files = list((out_dir / "07_n8n_workflows").glob("0[1-9]*.json"))
        if n8n_files:
            await upload_workflows_to_n8n([str(f) for f in n8n_files])

        # ── Post summary message ───────────────────────────────────────────
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=ts,
            blocks=results_message(result, user_id),
            text=f"✅ Campaign ready for {params['business']}",
        )

        # ── Post campaign files to Slack ───────────────────────────────────
        _update(client, channel_id, ts, user_id, "📎 Uploading files to Slack…", 96)
        await _post_files_to_slack(client, channel_id, ts, out_dir)

        # ── Final update ──────────────────────────────────────────────────
        client.chat_update(
            channel=channel_id,
            ts=ts,
            blocks=progress_update("✅ Everything is ready!", 100, user_id),
            text="Campaign complete!",
        )

    except Exception as exc:
        try:
            client.chat_update(
                channel=channel_id,
                ts=ts,
                blocks=error_message(str(exc), user_id),
                text=f"Campaign generation failed: {exc}",
            )
        except Exception:
            pass


async def _post_files_to_slack(
    client: WebClient,
    channel_id: str,
    thread_ts: str,
    out_dir: Path,
) -> None:
    """Upload key campaign files directly into the Slack thread."""

    files_to_upload = [
        # (path, title, description)
        (
            out_dir / "02_strategy.md",
            "📊 Campaign Strategy",
            "Full funnel strategy, ICP, budget split & 90-day roadmap",
        ),
        (
            out_dir / "03_ads" / "meta_ads.json",
            "📱 Meta Ads (Facebook & Instagram)",
            "Ad copy, video scripts & retargeting ads",
        ),
        (
            out_dir / "03_ads" / "google_ads.json",
            "🔍 Google Ads",
            "RSAs, PMax assets & keywords",
        ),
        (
            out_dir / "03_ads" / "tiktok_ads.json",
            "🎵 TikTok Ads",
            "Video scripts with hooks",
        ),
        (
            out_dir / "04_lead_magnet" / "lead_magnet.json",
            "🎁 Lead Magnet",
            "Concept, outline & landing page copy",
        ),
        (
            out_dir / "05_email_sequences" / "nurture_sequence.json",
            "📧 14-Email Nurture Sequence",
            "Full email sequence with subject lines & body copy",
        ),
        (
            out_dir / "06_sms_sequences" / "sms_sequence.json",
            "💬 SMS Sequence",
            "Immediate follow-up + 7-day SMS drip",
        ),
        (
            out_dir / "08_ghl_setup" / "setup_guide.md",
            "🏗️ GoHighLevel Setup Guide",
            "Pipeline, tags, custom fields & automation steps",
        ),
        (
            out_dir / "07_n8n_workflows" / "00_import_manifest.json",
            "⚙️ n8n Workflows — Import Guide",
            "Instructions + all 3 workflow files",
        ),
    ]

    # Post a header message first
    client.chat_postMessage(
        channel=channel_id,
        thread_ts=thread_ts,
        text=(
            "📁 *Your campaign files are attached below.* "
            "Everything is here in Slack — no folders to dig through."
        ),
    )

    for file_path, title, description in files_to_upload:
        if not file_path.exists():
            continue
        try:
            content = file_path.read_bytes()
            filename = file_path.name

            # Convert JSON files to readable text for Slack preview
            if filename.endswith(".json"):
                try:
                    data = json.loads(content)
                    content = json.dumps(data, indent=2).encode()
                except Exception:
                    pass

            client.files_upload_v2(
                channel=channel_id,
                thread_ts=thread_ts,
                content=content,
                filename=filename,
                title=title,
                initial_comment=f"_{description}_",
            )
        except Exception:
            pass  # skip files that fail to upload — don't crash the whole job


def _update(client, channel_id, ts, user_id, label, pct):
    try:
        client.chat_update(
            channel=channel_id,
            ts=ts,
            blocks=progress_update(label, pct, user_id),
            text=label,
        )
    except Exception:
        pass
