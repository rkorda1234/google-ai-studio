"""GHL Agent — sets up GoHighLevel pipeline, templates, and workflows.

Creates in GHL:
- Sales pipeline with funnel stages
- Email templates for each nurture email
- SMS templates
- Custom fields for lead tracking
- Tags for segmentation
- Setup guide (if GHL API not configured)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.ghl_client import GHLClient

ghl = GHLClient()


PIPELINE_STAGES = [
    {"name": "New Lead", "position": 0},
    {"name": "Lead Magnet Downloaded", "position": 1},
    {"name": "Email Sequence Active", "position": 2},
    {"name": "Engaged (Opened 3+)", "position": 3},
    {"name": "Clicked CTA", "position": 4},
    {"name": "Discovery Call Booked", "position": 5},
    {"name": "Proposal Sent", "position": 6},
    {"name": "Closed Won", "position": 7},
    {"name": "Closed Lost", "position": 8},
]

CUSTOM_FIELDS = [
    ("Lead Source", "lead_source", "TEXT"),
    ("Lead Magnet Downloaded", "lead_magnet", "TEXT"),
    ("Ad Platform", "ad_platform", "TEXT"),
    ("Campaign Name", "campaign_name", "TEXT"),
    ("UTM Source", "utm_source", "TEXT"),
    ("UTM Medium", "utm_medium", "TEXT"),
    ("UTM Campaign", "utm_campaign", "TEXT"),
    ("Last Email Opened", "last_email_opened", "DATE"),
    ("Emails Opened Count", "emails_opened_count", "NUMBER"),
    ("Score", "lead_score", "NUMBER"),
]

TAGS = [
    "new-lead", "lm-delivered", "email-sequence-active",
    "nurture-email-1", "nurture-email-7", "nurture-email-14",
    "clicked-book-call", "converted", "retarget-ad-audience",
    "no-convert-7d", "high-intent",
]


async def setup_ghl_account(
    pipeline_name: str,
    email_sequence: dict,
    sms_sequence: dict,
    output_dir: Path,
) -> dict[str, Any]:
    """Full GHL account setup: pipeline, custom fields, tags, templates."""

    results: dict[str, Any] = {
        "pipeline": None,
        "custom_fields": [],
        "tags": [],
        "email_templates": [],
        "sms_templates": [],
        "demo_mode": not bool(ghl.location_id),
    }

    # ── Pipeline ──────────────────────────────────────────────────────────────
    try:
        pipeline_result = await ghl.create_pipeline(
            name=pipeline_name,
            stages=PIPELINE_STAGES,
        )
        results["pipeline"] = pipeline_result
    except Exception as e:
        results["pipeline"] = {"error": str(e)}

    # ── Custom Fields ─────────────────────────────────────────────────────────
    for name, key, dtype in CUSTOM_FIELDS:
        try:
            r = await ghl.create_custom_field(name, key, dtype)
            results["custom_fields"].append({"name": name, "result": r})
        except Exception as e:
            results["custom_fields"].append({"name": name, "error": str(e)})

    # ── Tags ──────────────────────────────────────────────────────────────────
    for tag in TAGS:
        try:
            r = await ghl.create_tag(tag)
            results["tags"].append({"tag": tag, "result": r})
        except Exception as e:
            results["tags"].append({"tag": tag, "error": str(e)})

    # ── Email Templates ───────────────────────────────────────────────────────
    emails = _extract_emails(email_sequence)
    for email in emails[:5]:  # Upload first 5 to avoid rate limits
        try:
            r = await ghl.create_email_template(
                name=f"[Nurture] {email.get('subject', 'Email')}",
                subject=email.get("subject", ""),
                html_body=email.get("body_html", email.get("body_plain", "")),
            )
            results["email_templates"].append({"subject": email.get("subject"), "result": r})
        except Exception as e:
            results["email_templates"].append({"subject": email.get("subject"), "error": str(e)})

    # ── SMS Templates ─────────────────────────────────────────────────────────
    smses = _extract_sms(sms_sequence)
    for sms in smses:
        try:
            r = await ghl.create_sms_template(
                name=f"[SMS] Day {sms.get('day_or_delay', '?')}",
                body=sms.get("message", ""),
            )
            results["sms_templates"].append({"message": sms.get("message", "")[:50], "result": r})
        except Exception as e:
            results["sms_templates"].append({"error": str(e)})

    # ── Setup Guide ───────────────────────────────────────────────────────────
    guide = _generate_setup_guide(pipeline_name, results)
    guide_path = output_dir / "08_ghl_setup" / "setup_guide.md"
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    guide_path.write_text(guide, encoding="utf-8")
    results["setup_guide_path"] = str(guide_path)

    # Save raw config
    config_path = output_dir / "08_ghl_setup" / "ghl_config.json"
    config_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    return {"ghl_setup": results, "success": True}


def _extract_emails(email_sequence: dict) -> list[dict]:
    emails: list[dict] = []
    if not isinstance(email_sequence, dict):
        return emails
    sequences = email_sequence.get("email_sequence", email_sequence)
    if isinstance(sequences, dict):
        seq = sequences.get("sequences", {})
        for v in seq.get("welcome", {}).values():
            if isinstance(v, dict):
                emails.append(v)
        emails.extend(seq.get("nurture", []))
        emails.extend(seq.get("conversion", []))
    return emails


def _extract_sms(sms_sequence: dict) -> list[dict]:
    smses: list[dict] = []
    if not isinstance(sms_sequence, dict):
        return smses
    data = sms_sequence.get("sms_sequence", sms_sequence)
    if isinstance(data, dict):
        for item in data.get("immediate_sequence", []):
            smses.append({**item, "day_or_delay": f"D0+{item.get('delay_minutes', 0)}min"})
        for item in data.get("nurture_sequence", []):
            smses.append({**item, "day_or_delay": f"D{item.get('day', '?')}"})
    return smses


def _generate_setup_guide(pipeline_name: str, results: dict) -> str:
    demo = results.get("demo_mode", True)
    status = "DEMO MODE — GHL API not configured" if demo else "LIVE — connected to GHL"

    pipeline_rows = "".join(f"| {s['name']} | {s['position']} | |\n" for s in PIPELINE_STAGES)
    field_rows = "".join(f"| {name} | {key} | {dtype} |\n" for name, key, dtype in CUSTOM_FIELDS)
    tag_list = "\n".join(f"- {tag}" for tag in TAGS)
    pipeline_note = (
        "The pipeline was created automatically via API."
        if not demo
        else "Create this pipeline manually in GHL > CRM > Pipelines:"
    )

    return f"""# GoHighLevel Setup Guide

**Status:** {status}
**Pipeline:** {pipeline_name}

---

## Step 1: Pipeline Configuration

{pipeline_note}

| Stage | Position | Notes |
|-------|----------|-------|
{pipeline_rows}
---

## Step 2: Custom Fields

Go to **Settings > Custom Fields** and create:

| Field Name | Key | Type |
|-----------|-----|------|
{field_rows}
---

## Step 3: Tags

Go to **Settings > Tags** and create these tags:

```
{tag_list}
```

---

## Step 4: Automation Workflow

Create a new workflow triggered by **"Contact Tag Added: new-lead"**:

1. **Trigger:** Tag Added = `new-lead`
2. **Action 1:** Send Email → Welcome email (lead magnet delivery)
3. **Action 2:** Send SMS → Immediate follow-up SMS
4. **Action 3:** Wait 2 days
5. **Action 4:** Send Email → Nurture Email 2
6. *(Continue for full sequence — see `/email_sequences/` folder)*
7. **Final:** After 32 days with no conversion → Tag `retarget-ad-audience`

---

## Step 5: Connect n8n Webhooks

In your landing page form, set the POST URL to your n8n webhook:

```
POST https://your-n8n-instance.com/webhook/lead-capture
Body:
  firstName, lastName, email, phone, source, leadMagnet
```

---

## Step 6: UTM Tracking

Add these UTM parameters to all ad links:

```
?utm_source={{PLATFORM}}&utm_medium=paid&utm_campaign={{CAMPAIGN_NAME}}&utm_content={{AD_NAME}}
```

Map to GHL custom fields via workflow action **"Update Contact Field"**.

---

## Step 7: Retargeting Pixel Setup

1. Add Facebook Pixel to your landing page
2. Create custom audiences in Meta Ads:
   - **Visitors** (all page visitors, 30 days)
   - **Lead Magnet Openers** (visited /thank-you, 30 days)
   - **Non-Converters** (visitors who did NOT visit /booked, 30 days)
3. Import `07_n8n_workflows/03_retargeting.json` — this auto-tags non-converters in GHL

---

## Step 8: Connect Meta (Facebook/Instagram) Retargeting — DO THIS ONCE

This is a one-time setup. After this, every lead tagged `retarget-ad-audience` in GHL
will **automatically** start seeing your Facebook & Instagram retargeting ads.

### 8a — Connect Meta to GHL
1. In GHL go to **Settings → Integrations → Facebook**
2. Click **Connect** → log in with your Facebook account
3. Select your **Ad Account** and **Facebook Page** → click Save

### 8b — Create the Retargeting Audience in Meta
1. Go to **Meta Ads Manager → Audiences**
2. Click **Create Audience → Custom Audience → CRM / Customer List**
3. Choose **"Import from CRM"** or **"GoHighLevel"** if available, OR:
   - Export GHL contacts tagged `retarget-ad-audience` as CSV
   - Upload to Meta → name it **"GHL Non-Converters"**
4. Meta will match emails/phones to Facebook profiles (usually 60-80% match rate)

### 8c — Create a Lookalike Audience (bonus)
1. In Meta Audiences → **Create Audience → Lookalike Audience**
2. Source: **"GHL Non-Converters"** audience you just created
3. Country: US (or your target country)
4. Size: 1% (most similar) → click Create
5. Name it **"Lookalike — Agency Leads"**
   This finds millions of people who look like your leads — great for top-of-funnel ads.

### 8d — Set Up the Retargeting Ad Campaign (one time)
1. In Meta Ads Manager → **Create Campaign → Retargeting**
2. Objective: **Leads** or **Conversions**
3. Audience: select **"GHL Non-Converters"**
4. Upload the retargeting ad creatives from `03_ads/meta_ads.json` (retargeting_ads section)
5. Set daily budget: $10-20/day
6. Turn campaign **ON and leave it running**

From now on: every time n8n tags a contact `retarget-ad-audience` in GHL,
that contact syncs to Meta and automatically starts seeing your ads. ✅

---

## Step 9: Connect Google Ads Retargeting — DO THIS ONCE

### 9a — Connect Google Ads to GHL
1. In GHL go to **Settings → Integrations → Google Ads**
2. Click **Connect** → sign in with your Google account
3. Select your **Google Ads Customer ID** → Save

### 9b — Create a Customer Match Audience
1. In Google Ads → **Tools → Audience Manager → Customer Lists**
2. Click **+ → Customer list**
3. Select **"Emails, phones and mailing addresses"**
4. Upload a CSV of contacts tagged `retarget-ad-audience` from GHL
5. Name it **"GHL Non-Converters"** → Upload
6. Google takes 24-48 hours to process and match (usually 30-50% match rate)

### 9c — Set Up the Google Retargeting Campaign (one time)
1. Create a new campaign → **Display or Search**
2. Audience: **"GHL Non-Converters"** customer list
3. For Display: upload banner creatives (from your brand assets)
4. For Search: use the Google Ads copy from `03_ads/google_ads.json`
5. Set daily budget and turn **ON**

### 9d — Auto-sync going forward
1. In GHL go to **Settings → Integrations → Google Ads**
2. Enable **"Sync contacts to Google Audience"**
3. Filter: Tag = `retarget-ad-audience`
4. Google Ads will automatically update the customer list as new contacts get tagged ✅

---

## How It All Works Automatically (Summary)

```
Lead clicks your ad
       ↓
Fills landing page form
       ↓
n8n creates contact in GHL + tags "new-lead"
       ↓
GHL sends welcome email + SMS immediately
       ↓
14 emails sent over 32 days automatically
       ↓
Still no conversion after 7 days of inactivity?
       ↓
n8n tags contact "retarget-ad-audience"
       ↓
GHL syncs to Meta → Facebook/Instagram retargeting ads start showing ✅
GHL syncs to Google → Google Display/Search retargeting ads start showing ✅
GHL sends 5-email retargeting sequence ✅
GHL sends 2 re-engagement SMS ✅
       ↓
Lead converts → tag "converted" → all retargeting stops ✅
```

You set this up once. Every lead after that goes through the full funnel automatically.

---

## Troubleshooting

- **Emails not sending:** Check GHL SMTP settings under Settings > Email Services
- **Webhooks failing:** Verify n8n workflow is active and URL matches form action
- **Tags not applying:** Ensure workflow trigger condition matches exact tag name (case-sensitive)
"""
