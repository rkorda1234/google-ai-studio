"""Slack Bot — Campaign Generator.

Uses Slack Bolt with Socket Mode (no public URL needed).

Commands:
  /campaign   → Opens a form modal → generates full campaign package

Setup:
  See SLACK_SETUP.md for step-by-step instructions.
"""

from __future__ import annotations

import os
import sys

# Make sure we can import from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_bot.blocks import campaign_modal, generating_message
from slack_bot.campaign_job import run_campaign_in_background
from config import settings

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


# ── /campaign slash command ────────────────────────────────────────────────────

@app.command("/campaign")
def handle_campaign_command(ack, body, client):
    """Open the campaign generation modal."""
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view=campaign_modal(),
    )


# ── Modal submission ───────────────────────────────────────────────────────────

@app.view("campaign_modal_submit")
def handle_modal_submission(ack, body, client, view):
    """Handle form submit: acknowledge instantly, then kick off background job."""
    ack()

    user_id = body["user"]["id"]
    channel_id = _get_dm_channel(client, user_id)

    # Parse form values
    vals = view["state"]["values"]

    business = vals["business_block"]["business_input"]["value"]
    target = vals["target_block"]["target_input"]["value"]
    goal = vals["goal_block"]["goal_input"]["value"]
    budget_str = vals["budget_block"]["budget_input"]["value"]
    keywords_str = vals.get("keywords_block", {}).get("keywords_input", {}).get("value") or ""
    landing_page = vals.get("landing_page_block", {}).get("landing_page_input", {}).get("value") or ""

    try:
        budget = int(budget_str.replace("$", "").replace(",", "").strip())
    except ValueError:
        budget = 3000

    keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

    # Post the "generating" message immediately
    msg = client.chat_postMessage(
        channel=channel_id,
        blocks=generating_message(business, user_id),
        text=f"⏳ Generating campaign for {business}…",
    )

    # Start background generation (won't block)
    run_campaign_in_background(
        client=client,
        channel_id=channel_id,
        ts=msg["ts"],
        user_id=user_id,
        campaign_params={
            "business": business,
            "target": target,
            "goal": goal,
            "budget": budget,
            "keywords": keywords,
            "landing_page_url": landing_page,
        },
    )


# ── Help message ───────────────────────────────────────────────────────────────

@app.message("help")
def handle_help(message, say):
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "*🤖 Campaign Generator Bot — Help*\n\n"
                        "Type `/campaign` in any channel to open the campaign form.\n\n"
                        "*What gets generated:*\n"
                        "• 🔍 Competitor ad research (Facebook Ad Library + Instagram)\n"
                        "• 📊 Full funnel strategy + 90-day roadmap\n"
                        "• ✏️ Ad creatives for Google, Meta (FB/IG), and TikTok\n"
                        "• 📧 14-email nurture sequence + 5-email retargeting\n"
                        "• 💬 SMS follow-up drip sequence\n"
                        "• ⚙️ n8n automation workflows (importable JSON)\n"
                        "• 🏗️ GoHighLevel pipeline + templates + setup guide\n\n"
                        "Takes ~3–5 minutes. I'll DM you when it's ready!"
                    ),
                },
            }
        ],
        text="Type /campaign to start.",
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_dm_channel(client, user_id: str) -> str:
    """Open a DM channel with the user and return the channel ID."""
    result = client.conversations_open(users=user_id)
    return result["channel"]["id"]


# ── Entry point ────────────────────────────────────────────────────────────────

def start():
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        print("ERROR: SLACK_APP_TOKEN is not set.")
        sys.exit(1)
    if not settings.ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY is not set.")
        sys.exit(1)

    print("🤖 Campaign Generator Bot starting (Socket Mode)…")
    handler = SocketModeHandler(app, app_token)
    handler.start()


if __name__ == "__main__":
    start()
