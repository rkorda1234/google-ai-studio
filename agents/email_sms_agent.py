"""Email & SMS Agent — full nurture sequence generation.

Produces:
- Welcome / lead magnet delivery email
- 14-email nurture sequence (awareness → consideration → conversion)
- Post-conversion onboarding sequence
- SMS immediate follow-up + 7-day drip
- Retargeting email sequence for non-converters
"""

from __future__ import annotations

import json
from typing import Any
import anthropic
from config import settings

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

COPYWRITER_SYSTEM = (
    "You are a master email copywriter and conversion strategist. "
    "You write emails that feel personal, deliver value, and move people through a funnel "
    "without being pushy. Your emails have high open rates because of compelling subject lines, "
    "and high click rates because of crystal-clear CTAs. "
    "You understand GoHighLevel automation workflows. "
    "Return structured JSON where specified."
)


async def generate_email_sequence(
    business_description: str,
    icp_summary: str,
    lead_magnet_title: str,
    offer: str,
    sender_name: str = "Your Name",
    sender_company: str = "Your Company",
    landing_page_context: str = "",
) -> dict[str, Any]:
    """Generate a full 14-email nurture sequence."""

    lp_section = f"\n{landing_page_context}\n" if landing_page_context else ""

    prompt = f"""Create a complete 14-email nurture sequence for a marketing agency.

**Business:** {business_description}
**ICP:** {icp_summary}
**Lead Magnet:** {lead_magnet_title}
**Primary Offer:** {offer}
**Sender:** {sender_name} from {sender_company}
{lp_section}

Return ONLY valid JSON:
{{
  "sequences": {{
    "welcome": {{
      "email_1": {{
        "day": 0,
        "trigger": "lead magnet opt-in",
        "subject": "string",
        "preview_text": "string (45 chars)",
        "body_html": "string (full HTML email body)",
        "body_plain": "string",
        "cta_text": "string",
        "cta_url": "{{lead_magnet_url}}",
        "goal": "deliver lead magnet + set expectations",
        "ghl_tag_on_click": "lm-delivered"
      }}
    }},
    "nurture": [
      {{
        "email_number": 2,
        "day": 2,
        "subject": "string",
        "preview_text": "string",
        "email_type": "value | story | case_study | pain_agitate | soft_sell | hard_sell",
        "body_html": "string (full HTML)",
        "body_plain": "string",
        "cta_text": "string",
        "cta_url": "string",
        "goal": "string",
        "ghl_tag_on_click": "string"
      }}
    ],
    "conversion": [
      {{
        "email_number": 12,
        "day": 14,
        "subject": "string",
        "preview_text": "string",
        "email_type": "direct_offer | urgency | faq | testimonial",
        "body_html": "string",
        "body_plain": "string",
        "cta_text": "string",
        "cta_url": "{{booking_url}}",
        "goal": "book a call / purchase",
        "ghl_tag_on_click": "clicked-book-call"
      }}
    ]
  }},
  "subject_line_ab_tests": [
    {{"original": "string", "variant_a": "string", "variant_b": "string"}}
  ]
}}

Create emails 1-14. Days: 0, 2, 4, 7, 9, 11, 14, 17, 20, 23, 26, 28, 30, 32.
Mix: 6 value emails, 3 story/case studies, 2 soft sell, 3 direct conversion.
Make ALL body_html complete, properly formatted HTML emails."""

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=8000,
        system=COPYWRITER_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = ""
    for block in response.content:
        if hasattr(block, "text"):
            raw += block.text

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])
    except (json.JSONDecodeError, ValueError):
        data = {"raw": raw}

    return {"email_sequence": data, "success": True}


async def generate_sms_sequence(
    business_description: str,
    icp_summary: str,
    lead_magnet_title: str,
    offer: str,
    booking_url: str = "{{booking_url}}",
    landing_page_context: str = "",
) -> dict[str, Any]:
    """Generate SMS follow-up and nurture sequences."""

    lp_section = f"\n{landing_page_context}\n" if landing_page_context else ""

    prompt = f"""Create a complete SMS follow-up and nurture sequence for a marketing agency.

**Business:** {business_description}
**ICP:** {icp_summary}
**Lead Magnet:** {lead_magnet_title}
**Offer:** {offer}
**Booking URL:** {booking_url}
{lp_section}

IMPORTANT: SMS must be conversational, under 160 chars each, and feel personal — NOT spammy.
Include merge tags like {{{{first_name}}}}.

Return ONLY valid JSON:
{{
  "immediate_sequence": [
    {{
      "sms_number": 1,
      "send_at": "immediately after opt-in",
      "delay_minutes": 0,
      "message": "string (under 160 chars, includes {{first_name}})",
      "goal": "string",
      "ghl_tag_on_reply": "string"
    }}
  ],
  "nurture_sequence": [
    {{
      "sms_number": 4,
      "day": 3,
      "message": "string",
      "goal": "string",
      "type": "value | question | soft_sell | hard_sell"
    }}
  ],
  "retargeting_sms": [
    {{
      "sms_number": 1,
      "trigger": "no email open in 7 days",
      "message": "string",
      "goal": "re-engagement"
    }}
  ],
  "opt_out_handling": {{
    "auto_reply_on_stop": "string",
    "gdpr_note": "string"
  }}
}}

Immediate sequence: 3 SMS (day 0, day 1, day 3).
Nurture: 5 SMS over 14 days.
Retargeting: 2 SMS for non-openers."""

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=3000,
        system=COPYWRITER_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = ""
    for block in response.content:
        if hasattr(block, "text"):
            raw += block.text

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])
    except (json.JSONDecodeError, ValueError):
        data = {"raw": raw}

    return {"sms_sequence": data, "success": True}


async def generate_retargeting_emails(
    icp_summary: str,
    offer: str,
    reason_they_didnt_convert: str,
    landing_page_context: str = "",
) -> dict[str, Any]:
    """Generate 5-email retargeting sequence for non-converters."""

    lp_section = f"\n{landing_page_context}\n" if landing_page_context else ""

    prompt = f"""Create a 5-email retargeting sequence for leads who didn't convert.

**ICP:** {icp_summary}
**Offer:** {offer}
**Why they may not have converted:** {reason_they_didnt_convert}
{lp_section}

Focus: Address objections, create urgency, use social proof, make a fresh offer.

Return ONLY valid JSON:
{{
  "retargeting_emails": [
    {{
      "email_number": 1,
      "day_after_inactivity": 7,
      "subject": "string",
      "preview_text": "string",
      "angle": "we noticed | objection handling | social proof | new angle | final chance",
      "body_html": "string",
      "body_plain": "string",
      "cta_text": "string",
      "cta_url": "{{booking_url}}",
      "ps_line": "string (compelling PS)"
    }}
  ]
}}

Create all 5 emails. Days: 7, 10, 14, 18, 21 after last engagement."""

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=4000,
        system=COPYWRITER_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = ""
    for block in response.content:
        if hasattr(block, "text"):
            raw += block.text

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])
    except (json.JSONDecodeError, ValueError):
        data = {"raw": raw}

    return {"retargeting_emails": data, "success": True}
