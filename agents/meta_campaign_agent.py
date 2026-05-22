"""Meta Marketing API — auto-creates campaigns in PAUSED state.

Creates full campaign structure ready for review:
- Campaign (PAUSED)
- Ad Sets with audience targeting
- Ads with generated copy

Requires META_ACCESS_TOKEN and META_AD_ACCOUNT_ID in .env
"""

from __future__ import annotations

import httpx
from typing import Any
from config import settings

BASE = settings.META_GRAPH_BASE
ACCOUNT = settings.META_AD_ACCOUNT_ID


async def create_full_campaign(
    campaign_name: str,
    ad_creatives: dict,
    daily_budget_usd: int,
    landing_page_url: str,
    audience_targeting: dict | None = None,
) -> dict[str, Any]:
    """Create a complete paused Meta campaign from generated ad copy.

    Returns campaign URL and IDs for review.
    """
    if not settings.META_ACCESS_TOKEN or not settings.META_AD_ACCOUNT_ID:
        return _demo_result(campaign_name)

    results: dict[str, Any] = {"campaign_name": campaign_name, "ads": [], "success": False}

    try:
        # ── 1. Create Campaign ────────────────────────────────────────────────
        campaign = await _post(f"/act_{ACCOUNT}/campaigns", {
            "name": campaign_name,
            "objective": "OUTCOME_LEADS",
            "status": "PAUSED",
            "special_ad_categories": [],
        })
        campaign_id = campaign["id"]
        results["campaign_id"] = campaign_id
        results["campaign_url"] = (
            f"https://www.facebook.com/adsmanager/manage/campaigns?act={ACCOUNT.replace('act_','')}"
        )

        # ── 2. Build targeting ────────────────────────────────────────────────
        targeting = audience_targeting or _default_targeting()

        # ── 3. Create Ad Sets (one per funnel stage) ──────────────────────────
        ad_sets = [
            {"name": f"{campaign_name} — Top of Funnel", "budget_pct": 0.6},
            {"name": f"{campaign_name} — Retargeting", "budget_pct": 0.4},
        ]

        campaigns_data = ad_creatives.get("campaigns", [])
        ads_list = []
        if campaigns_data:
            for ad_set_info in ad_sets:
                daily_cents = int(daily_budget_usd * ad_set_info["budget_pct"] * 100)

                ad_set = await _post(f"/act_{ACCOUNT}/adsets", {
                    "name": ad_set_info["name"],
                    "campaign_id": campaign_id,
                    "daily_budget": max(daily_cents, 100),
                    "billing_event": "IMPRESSIONS",
                    "optimization_goal": "LEAD_GENERATION",
                    "targeting": targeting,
                    "status": "PAUSED",
                })
                ad_set_id = ad_set["id"]

                # ── 4. Create Ads from generated copy ─────────────────────────
                source_ads = (
                    campaigns_data[0].get("ad_sets", [{}])[0].get("ads", [])
                    if campaigns_data else []
                )

                for i, ad_copy in enumerate(source_ads[:2]):
                    creative = await _post(f"/act_{ACCOUNT}/adcreatives", {
                        "name": f"{ad_copy.get('ad_name', f'Ad {i+1}')}",
                        "object_story_spec": {
                            "page_id": await _get_page_id(),
                            "link_data": {
                                "message": ad_copy.get("primary_text", ""),
                                "link": landing_page_url,
                                "name": ad_copy.get("headline", ""),
                                "description": ad_copy.get("description", ""),
                                "call_to_action": {
                                    "type": ad_copy.get("cta_button", "LEARN_MORE"),
                                    "value": {"link": landing_page_url},
                                },
                            },
                        },
                    })

                    ad = await _post(f"/act_{ACCOUNT}/ads", {
                        "name": ad_copy.get("ad_name", f"Ad {i+1}"),
                        "adset_id": ad_set_id,
                        "creative": {"creative_id": creative["id"]},
                        "status": "PAUSED",
                    })

                    ads_list.append({
                        "ad_name": ad_copy.get("ad_name", f"Ad {i+1}"),
                        "ad_id": ad["id"],
                        "headline": ad_copy.get("headline", ""),
                        "status": "PAUSED",
                    })

        results["ads"] = ads_list
        results["total_ads_created"] = len(ads_list)
        results["success"] = True
        results["next_step"] = (
            f"Review your campaign at: {results['campaign_url']}\n"
            "Everything is PAUSED — activate when you're ready."
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

    try:
        campaign = await _post(f"/act_{ACCOUNT}/campaigns", {
            "name": f"{campaign_name} — Retargeting",
            "objective": "OUTCOME_LEADS",
            "status": "PAUSED",
            "special_ad_categories": [],
        })
        campaign_id = campaign["id"]

        ad_set = await _post(f"/act_{ACCOUNT}/adsets", {
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
            "next_step": "Add your retargeting ad creatives in Meta Ads Manager, then activate.",
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


async def _get_page_id() -> str:
    """Get the first Facebook page connected to the ad account."""
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(
                f"{BASE}/me/accounts",
                params={"access_token": settings.META_ACCESS_TOKEN},
            )
            data = r.json()
            pages = data.get("data", [])
            if pages:
                return pages[0]["id"]
    except Exception:
        pass
    return ""


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
        "next_step": "Add your Meta credentials to .env — see .env.example for the variable names.",
    }
