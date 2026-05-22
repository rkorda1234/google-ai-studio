"""Slack Block Kit UI builders for the campaign bot."""

from __future__ import annotations


def campaign_modal(trigger_id: str | None = None) -> dict:
    """Modal form users fill out to generate a campaign."""
    return {
        "type": "modal",
        "callback_id": "campaign_modal_submit",
        "title": {"type": "plain_text", "text": "Generate Campaign"},
        "submit": {"type": "plain_text", "text": "Generate 🚀"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Fill in the details below.* Claude will research competitors, write your ads, email sequences, and set up n8n + GHL — usually takes 3–5 minutes.",
                },
            },
            {"type": "divider"},
            {
                "type": "input",
                "block_id": "business_block",
                "label": {"type": "plain_text", "text": "📋 Describe your business / service"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "business_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g. Marketing agency that helps local businesses get more leads with Facebook & Google Ads",
                    },
                },
            },
            {
                "type": "input",
                "block_id": "target_block",
                "label": {"type": "plain_text", "text": "🎯 Target audience"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "target_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g. Small business owners in the US, $5k–$50k/month revenue",
                    },
                },
            },
            {
                "type": "input",
                "block_id": "goal_block",
                "label": {"type": "plain_text", "text": "🏆 Campaign goal"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "goal_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g. Book discovery calls, generate qualified leads",
                    },
                },
                "hint": {
                    "type": "plain_text",
                    "text": "What action do you want leads to take?",
                },
            },
            {
                "type": "input",
                "block_id": "budget_block",
                "label": {"type": "plain_text", "text": "💰 Monthly ad budget (USD)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "budget_input",
                    "placeholder": {"type": "plain_text", "text": "e.g. 3000"},
                },
            },
            {
                "type": "input",
                "block_id": "keywords_block",
                "label": {
                    "type": "plain_text",
                    "text": "🔍 Competitor keywords (comma-separated)",
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "keywords_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g. marketing agency, lead gen, grow my business",
                    },
                },
                "optional": True,
            },
            {
                "type": "input",
                "block_id": "landing_page_block",
                "label": {"type": "plain_text", "text": "🔗 Landing page URL"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "landing_page_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g. https://yoursite.com/free-guide",
                    },
                },
                "optional": True,
                "hint": {
                    "type": "plain_text",
                    "text": "Used to auto-create your Meta & Google campaigns (paused for review)",
                },
            },
            {
                "type": "input",
                "block_id": "platforms_block",
                "label": {"type": "plain_text", "text": "📱 Ad platforms"},
                "element": {
                    "type": "checkboxes",
                    "action_id": "platforms_input",
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Meta (Facebook & Instagram)"},
                            "value": "meta",
                        },
                        {
                            "text": {"type": "plain_text", "text": "Google Ads"},
                            "value": "google",
                        },
                        {
                            "text": {"type": "plain_text", "text": "TikTok Ads"},
                            "value": "tiktok",
                        },
                    ],
                    "initial_options": [
                        {
                            "text": {"type": "plain_text", "text": "Meta (Facebook & Instagram)"},
                            "value": "meta",
                        },
                        {
                            "text": {"type": "plain_text", "text": "Google Ads"},
                            "value": "google",
                        },
                    ],
                },
                "optional": True,
            },
        ],
    }


def generating_message(business: str, user_id: str) -> list[dict]:
    """Posted immediately after form submit while generation runs."""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"⏳ *Campaign generation started!*\n<@{user_id}> — I'm working on your campaign for *{business}*.",
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "🔍 *Step 1:* Researching competitor ads"},
                {"type": "mrkdwn", "text": "📊 *Step 2:* Building funnel strategy"},
                {"type": "mrkdwn", "text": "✏️ *Step 3:* Writing ad creatives"},
                {"type": "mrkdwn", "text": "📧 *Step 4:* Creating email & SMS sequences"},
                {"type": "mrkdwn", "text": "⚙️ *Step 5:* Building n8n workflows"},
                {"type": "mrkdwn", "text": "🏗️ *Step 6:* Setting up GoHighLevel"},
            ],
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "This usually takes 3–5 minutes. I'll tag you when it's ready.",
                }
            ],
        },
    ]


def progress_update(step: str, pct: int, user_id: str) -> list[dict]:
    """Live progress update block."""
    bar = _progress_bar(pct)
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"⚙️ *{step}* {bar} `{pct}%`\n<@{user_id}> — campaign generation in progress…",
            },
        }
    ]


def results_message(result: dict, user_id: str) -> list[dict]:
    """Rich results message posted when generation is complete."""
    out_dir = result.get("output_path", "output/campaigns/")
    slug = result.get("campaign_slug", "campaign")
    steps = result.get("steps", {})

    # Extract highlights from the summary
    summary_preview = result.get("summary", "")[:800]

    # Pull top ad copy if available
    ad_preview = _extract_ad_preview(result)
    email_preview = _extract_email_preview(result)

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "✅ Your Campaign Package is Ready!"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<@{user_id}> — your full-funnel campaign *`{slug}`* has been generated.",
            },
        },
        {"type": "divider"},
        # Status of each component
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*📦 What was generated:*"},
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"{'✅' if steps.get('research') else '⚠️'} *Research Report*\nCompetitor ads & market insights",
                },
                {
                    "type": "mrkdwn",
                    "text": f"{'✅' if steps.get('strategy') else '⚠️'} *Campaign Strategy*\nICP, funnel map, 90-day plan",
                },
                {
                    "type": "mrkdwn",
                    "text": f"{'✅' if steps.get('creatives') else '⚠️'} *Ad Creatives*\nGoogle, Meta & TikTok copy",
                },
                {
                    "type": "mrkdwn",
                    "text": f"{'✅' if steps.get('email_sms') else '⚠️'} *Email & SMS*\n14 emails + SMS drip",
                },
                {
                    "type": "mrkdwn",
                    "text": f"{'✅' if steps.get('n8n') else '⚠️'} *n8n Workflows*\n3 importable JSONs",
                },
                {
                    "type": "mrkdwn",
                    "text": f"{'✅' if steps.get('ghl') else '⚠️'} *GHL Setup*\nPipeline + templates + guide",
                },
            ],
        },
        {"type": "divider"},
    ]

    if ad_preview:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*✏️ Sample Ad Headline (Meta):*\n```{ad_preview}```",
            },
        })

    if email_preview:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📧 Sample Email Subject:*\n```{email_preview}```",
            },
        })

    blocks += [
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🚀 Your next steps:*\n1. Review `02_strategy.md` to confirm positioning\n2. Import `07_n8n_workflows/` into n8n\n3. Follow `08_ghl_setup/setup_guide.md` for GHL\n4. Upload `03_ads/` creatives to your ad platforms",
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📁 Saved to: `{out_dir}` | Run `/campaign` again any time to create a new one.",
                }
            ],
        },
    ]

    return blocks


def error_message(error: str, user_id: str) -> list[dict]:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"❌ <@{user_id}> — campaign generation failed.\n*Error:* `{error}`\n\nCheck that your `ANTHROPIC_API_KEY` is set and try `/campaign` again.",
            },
        }
    ]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _progress_bar(pct: int, width: int = 10) -> str:
    filled = int(width * pct / 100)
    return "█" * filled + "░" * (width - filled)


def _extract_ad_preview(result: dict) -> str:
    """Try to pull a headline from the meta ads output."""
    try:
        import json
        from pathlib import Path
        out = Path(result["output_path"])
        meta_file = out / "03_ads" / "meta_ads.json"
        if meta_file.exists():
            data = json.loads(meta_file.read_text())
            campaigns = data.get("campaigns", [])
            if campaigns:
                ads = campaigns[0].get("ad_sets", [{}])[0].get("ads", [{}])
                if ads:
                    return ads[0].get("headline", "")
    except Exception:
        pass
    return ""


def _extract_email_preview(result: dict) -> str:
    """Try to pull the first email subject from the nurture sequence."""
    try:
        import json
        from pathlib import Path
        out = Path(result["output_path"])
        email_file = out / "05_email_sequences" / "nurture_sequence.json"
        if email_file.exists():
            data = json.loads(email_file.read_text())
            seqs = data.get("sequences", {})
            welcome = seqs.get("welcome", {})
            for v in welcome.values():
                if isinstance(v, dict) and v.get("subject"):
                    return v["subject"]
            nurture = seqs.get("nurture", [])
            if nurture:
                return nurture[0].get("subject", "")
    except Exception:
        pass
    return ""
