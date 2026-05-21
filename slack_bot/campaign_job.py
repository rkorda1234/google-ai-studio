"""Background campaign generation job.

Runs the orchestrator in a thread so Slack's 3-second timeout is never hit.
Posts progress updates and final results back to the channel.
"""

from __future__ import annotations

import asyncio
import threading
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


def _run(
    client: WebClient,
    channel_id: str,
    ts: str,
    user_id: str,
    params: dict[str, Any],
) -> None:
    """Runs in a background thread — calls async orchestrator via asyncio."""
    asyncio.run(_async_run(client, channel_id, ts, user_id, params))


async def _async_run(
    client: WebClient,
    channel_id: str,
    ts: str,
    user_id: str,
    params: dict[str, Any],
) -> None:
    from agents.orchestrator import CampaignOrchestrator

    last_pct = [0]

    async def on_progress(step: str, pct: int):
        # Only post an update every ~20% to avoid Slack rate limits
        if pct - last_pct[0] >= 20 or pct == 100:
            last_pct[0] = pct
            step_labels = {
                "research": "🔍 Researching competitor ads",
                "strategy": "📊 Building strategy",
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
                pass  # don't crash the job on a Slack API hiccup

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

        # Post final results as a new message (thread under the progress msg)
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=ts,
            blocks=results_message(result, user_id),
            text=f"✅ Campaign ready for {params['business']}",
        )

        # Update the original progress message to show complete
        client.chat_update(
            channel=channel_id,
            ts=ts,
            blocks=progress_update("✅ Campaign package complete!", 100, user_id),
            text="Campaign generation complete!",
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
