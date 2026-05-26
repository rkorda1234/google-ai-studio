"""Meta Marketing API — auto-creates campaign shell in PAUSED state.

Creates:
- Campaign (PAUSED)
- Ad Sets with audience targeting (TOF + retargeting split)

Ad creatives are NOT created here — Meta requires real images/videos.
The generated copy (headlines, body text) is saved in 03_ads/meta_ads.json.
Copy it into Ads Manager manually when adding your images.

Requires META_ACCESS_TOKEN, META_AD_ACCOUNT_ID, and META_PAGE_ID in .env
"""

from __future__ import annotations

import os
import httpx
from typing import Any
from config import settings

BASE = settings.META_GRAPH_BASE


def _account_id() -> str:
    """Always read fresh from env, strip act_ prefix regardless of format."""
    raw = os.getenv("META_AD_ACCOUNT_ID", "")
    return raw.replace("act_", "").strip()


async def create_full_campaign(
    campaign_name: str,
    ad_creatives: dict,
    daily_budget_usd: int,
    landing_page_url: str,
    audience_targeting: dict | None = None,
) -> dict[str, Any]:
    """Create a paused Meta campaign shell (campaign + ad sets).

    Ad creatives are skipped — Meta requires images/videos you upload.
    The generated copy in meta_ads.json is your reference for Ads Manager.
    """
    if not settings.META_ACCESS_TOKEN or not settings.META_AD_ACCOUNT_ID:
        return _demo_result(campaign_name)

    account = _account_id()
    results: dict[str, Any] = {"campaign_name": campaign_name, "ad_sets": [], "success": False}

    try:
        # ── 1. Create Campaign ────────────────────────────────────────────────
        campaign = await _post(f"/act_{account}/campaigns", {
            "name": campaign_name,
            "objective": "OUTCOME_LEADS",
            "status": "PAUSED",
            "special_ad_categories": [],
        })
        campaign_id = campaign["id"]
        results["campaign_id"] = campaign_id
        results["campaign_url"] = (
            f"https://www.facebook.com/adsmanager/manage/campaigns?act={account}"
        )

        # ── 2. Build targeting ────────────────────────────────────────────────
        targeting = audience_targeting or _default_targeting()

        # ── 3. Create Ad Sets ─────────────────────────────────────────────────
        ad_set_configs = [
            {"name": f"{campaign_name} — Top of Funnel", "budget_pct": 0.6},
            {"name": f"{campaign_name} — Retargeting",   "budget_pct": 0.4},
        ]

        ad_sets_created = []
        for cfg in ad_set_configs:
            daily_cents = max(int(daily_budget_usd * cfg["budget_pct"] * 100), 100)
            ad_set = await _post(f"/act_{account}/adsets", {
                "name": cfg["name"],
                "campaign_id": campaign_id,
                "daily_budget": daily_cents,
                "billing_event": "IMPRESSIONS",
                "optimization_goal": "LEAD_GENERATION",
                "targeting": targeting,
                "status": "PAUSED",
            })
            ad_sets_created.append({"name": cfg["name"], "id": ad_set["id"]})

        results["ad_sets"] = ad_sets_created
        results["success"] = True
        results["next_step"] = (
            "Your campaign shell is live in Meta Ads Manager (PAUSED).\n"
            "Open the campaign, go into each Ad Set, and create ads using the "
            "copy from meta_ads.json. Add your images/videos, then activate."
        )

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False

    return results


async def create_retargeting_campaign(
    campaign_name: str,
    retargeting_ads: list[dict],
    custom_audience_id: str,
    daily_budget_usd: int,
    landing_page_url: str,
) -> dict[str, Any]:
    """Create a retargeting campaign targeting the GHL Non-Converters audience."""
    if not settings.META_ACCESS_TOKEN or not settings.META_AD_ACCOUNT_ID:
        return _demo_result(f"{campaign_name} — Retargeting")

    account = _account_id()
    try:
        campaign = await _post(f"/act_{account}/campaigns", {
            "name": f"{campaign_name} — Retargeting",
            "objective": "OUTCOME_LEADS",
            "status": "PAUSED",
            "special_ad_categories": [],
        })
        campaign_id = campaign["id"]

        ad_set = await _post(f"/act_{account}/adsets", {
            "name": "GHL Non-Converters",
            "campaign_id": campaign_id,
            "daily_budget": daily_budget_usd * 100,
            "billing_event": "IMPRESSIONS",
            "optimization_goal": "LEAD_GENERATION",
            "targeting": {
                "custom_audiences": [{"id": custom_audience_id}],
                "geo_locations": {"countries": [settings.DEFAULT_COUNTRY]},
            },
            "status": "PAUSED",
        })

        return {
            "success": True,
            "campaign_id": campaign_id,
            "ad_set_id": ad_set["id"],
            "status": "PAUSED",
            "campaign_url": f"https://www.facebook.com/adsmanager/manage/campaigns?act={account}",
            "next_step": "Add retargeting ad creatives in Ads Manager, then activate.",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _default_targeting() -> dict:
    return {
        "geo_locations": {"countries": [settings.DEFAULT_COUNTRY]},
        "age_min": 25,
        "age_max": 55,
        "interests": [
            {"id": "6003107902433", "name": "Business"},
            {"id": "6003348604961", "name": "Entrepreneurship"},
            {"id": "6012286594139", "name": "Digital marketing"},
            {"id": "6003139266461", "name": "Marketing"},
        ],
        "publisher_platforms": ["facebook", "instagram"],
        "facebook_positions": ["feed", "story"],
        "instagram_positions": ["stream", "story"],
    }


async def _post(path: str, payload: dict) -> dict:
    payload["access_token"] = settings.META_ACCESS_TOKEN
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{BASE}{path}", json=payload)
        data = r.json()
        if "error" in data:
            raise ValueError(data["error"].get("message", str(data["error"])))
        return data


def _demo_result(name: str) -> dict:
    return {
        "campaign_name": name,
        "success": False,
        "demo_mode": True,
        "message": "Add META_ACCESS_TOKEN and META_AD_ACCOUNT_ID to .env to auto-create campaigns.",
        "next_step": "Add your Meta credentials to .env — see .env.example for variable names.",
    }
