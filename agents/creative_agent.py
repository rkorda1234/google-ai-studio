"""Creative Agent — platform-specific ad copy generation.

Generates complete ad sets for:
- Google Ads (Responsive Search Ads + Performance Max)
- Meta Ads (Facebook/Instagram — static, carousel, video script)
- TikTok Ads (video scripts with hooks)
- Lead magnet landing page copy

Each platform output includes multiple variants for A/B testing.
"""

from __future__ import annotations

import json
from typing import Any
import anthropic
from config import settings

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

CREATIVE_SYSTEM = (
    "You are a world-class direct-response copywriter and creative director specializing in "
    "digital advertising for marketing agencies. Your copy is known for stopping the scroll, "
    "creating emotional resonance, and driving action. You understand platform-specific "
    "best practices deeply — character limits, creative formats, algorithm preferences. "
    "Always write copy that speaks directly to the ICP's pain and desired transformation. "
    "Return structured JSON where specified."
)


async def generate_google_ads(
    icp_summary: str,
    offer: str,
    keywords: list[str],
    landing_page_url: str = "https://yourdomain.com",
) -> dict[str, Any]:
    """Generate Google RSAs and display ad copy."""

    prompt = f"""Create complete Google Ads campaigns for a marketing agency.

**ICP:** {icp_summary}
**Offer/CTA:** {offer}
**Target Keywords:** {', '.join(keywords)}
**Landing Page:** {landing_page_url}

Return ONLY valid JSON in this exact structure:
{{
  "responsive_search_ads": [
    {{
      "campaign_name": "string",
      "ad_group": "string",
      "headlines": ["string x15 — max 30 chars each"],
      "descriptions": ["string x4 — max 90 chars each"],
      "final_url": "string",
      "path1": "string (max 15 chars)",
      "path2": "string (max 15 chars)",
      "ad_strength_notes": "string"
    }}
  ],
  "performance_max_assets": {{
    "headlines": ["string x15"],
    "long_headlines": ["string x5 — max 90 chars"],
    "descriptions": ["string x5 — max 90 chars"],
    "business_name": "string",
    "call_to_action": "string"
  }},
  "keywords": {{
    "exact_match": ["[keyword]"],
    "phrase_match": ["\\"keyword\\""],
    "broad_match_modifier": ["keyword"],
    "negative_keywords": ["string x10"]
  }}
}}

Create 3 RSA variants with different angles: (1) pain-focused, (2) outcome-focused, (3) social-proof-focused."""

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=4000,
        system=CREATIVE_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = ""
    for block in response.content:
        if hasattr(block, "text"):
            raw += block.text

    try:
        # Extract JSON from response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])
    except (json.JSONDecodeError, ValueError):
        data = {"raw": raw}

    return {"platform": "google_ads", "creatives": data, "success": True}


async def generate_meta_ads(
    icp_summary: str,
    offer: str,
    lead_magnet: str,
    campaign_objective: str = "LEAD_GENERATION",
) -> dict[str, Any]:
    """Generate Facebook/Instagram ad creatives: static, carousel, and video scripts."""

    prompt = f"""Create a complete Meta (Facebook/Instagram) ad campaign for a marketing agency.

**ICP:** {icp_summary}
**Primary Offer:** {offer}
**Lead Magnet:** {lead_magnet}
**Campaign Objective:** {campaign_objective}

Return ONLY valid JSON:
{{
  "campaigns": [
    {{
      "campaign_name": "string",
      "objective": "string",
      "audience": {{
        "age_range": "string",
        "interests": ["string x5"],
        "behaviors": ["string x3"],
        "custom_audiences": ["string x3"],
        "lookalike_source": "string"
      }},
      "ad_sets": [
        {{
          "ad_set_name": "string",
          "placement": "feed | stories | reels | all",
          "ads": [
            {{
              "ad_name": "string",
              "format": "single_image | carousel | video",
              "primary_text": "string (125 chars for feed, up to 2200 for article style)",
              "headline": "string (max 27 chars)",
              "description": "string (max 30 chars)",
              "cta_button": "LEARN_MORE | SIGN_UP | DOWNLOAD | GET_QUOTE",
              "hook_type": "question | statement | statistic | story | pain",
              "angle": "string",
              "creative_direction": "string (what the image/video should show)",
              "carousel_cards": null
            }}
          ]
        }}
      ]
    }}
  ],
  "video_scripts": [
    {{
      "script_name": "string",
      "platform": "facebook_feed | instagram_reel | instagram_story",
      "duration_seconds": 30,
      "hook": "string (first 3 seconds — must stop the scroll)",
      "problem": "string (seconds 3-8)",
      "agitation": "string (seconds 8-15)",
      "solution": "string (seconds 15-22)",
      "proof": "string (seconds 22-27)",
      "cta": "string (seconds 27-30)",
      "visual_notes": "string"
    }}
  ],
  "retargeting_ads": [
    {{
      "audience": "website visitors | video viewers | lead magnet openers",
      "ad_name": "string",
      "primary_text": "string",
      "headline": "string",
      "angle": "urgency | social_proof | objection_handling | new_angle"
    }}
  ]
}}

Create 3 top-of-funnel ads and 2 retargeting ads. Include 2 video scripts (30s each)."""

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=6000,
        system=CREATIVE_SYSTEM,
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

    return {"platform": "meta_ads", "creatives": data, "success": True}


async def generate_tiktok_ads(
    icp_summary: str,
    offer: str,
    lead_magnet: str,
) -> dict[str, Any]:
    """Generate TikTok ad scripts optimized for native-feel performance."""

    prompt = f"""Create TikTok ad scripts for a marketing agency targeting:

**ICP:** {icp_summary}
**Offer:** {offer}
**Lead Magnet:** {lead_magnet}

Return ONLY valid JSON:
{{
  "ad_scripts": [
    {{
      "script_name": "string",
      "style": "ugc_style | talking_head | screen_record | text_overlay",
      "duration_seconds": 30,
      "hook_text": "string (on-screen text first 2s)",
      "hook_spoken": "string (what creator says first 2s)",
      "body": [
        {{"second": 0, "action": "string", "spoken": "string", "on_screen_text": "string"}}
      ],
      "cta": "string",
      "caption": "string (TikTok caption with hashtags)",
      "hashtags": ["string x8"],
      "trend_to_leverage": "string",
      "music_suggestion": "string",
      "performance_hook_type": "before_after | secret_reveal | controversial | tutorial | story"
    }}
  ],
  "spark_ads_strategy": {{
    "content_types_to_boost": ["string"],
    "creator_brief": "string",
    "budget_guidance": "string"
  }}
}}

Create 3 scripts: (1) educational/value, (2) before-after story, (3) controversial hook."""

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=4000,
        system=CREATIVE_SYSTEM,
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

    return {"platform": "tiktok_ads", "creatives": data, "success": True}


async def generate_lead_magnet(
    icp_summary: str,
    pain_points: str,
    desired_outcome: str,
    niche: str = "marketing agency",
) -> dict[str, Any]:
    """Generate lead magnet concept, title, outline, and landing page copy."""

    prompt = f"""Create a high-converting lead magnet strategy for a marketing agency.

**ICP:** {icp_summary}
**Pain Points:** {pain_points}
**Desired Outcome:** {desired_outcome}
**Niche:** {niche}

Return ONLY valid JSON:
{{
  "primary_lead_magnet": {{
    "title": "string (irresistible, specific)",
    "subtitle": "string",
    "format": "checklist | guide | template | video_training | mini_course | swipe_file | calculator",
    "value_proposition": "string (what they get and how fast)",
    "outline": ["string — section titles x5-8"],
    "key_takeaways": ["string x5"],
    "why_they_need_it": "string"
  }},
  "secondary_lead_magnet": {{
    "title": "string",
    "format": "string",
    "use_case": "retargeting non-openers or upsell path"
  }},
  "landing_page_copy": {{
    "headline": "string",
    "subheadline": "string",
    "bullet_points": ["string x5 — outcome-focused"],
    "cta_button_text": "string",
    "social_proof_placeholder": "string",
    "urgency_element": "string",
    "opt_in_field_label": "string"
  }},
  "thank_you_page": {{
    "headline": "string",
    "body": "string",
    "next_step_cta": "string",
    "tripwire_offer": "string (optional low-ticket offer)"
  }}
}}"""

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=3000,
        system=CREATIVE_SYSTEM,
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

    return {"lead_magnet": data, "success": True}
