"""Google Ads API — auto-creates campaigns in PAUSED state.

Creates:
- Search campaign with RSAs from generated copy
- Display/retargeting campaign for non-converters

Requires Google Ads credentials in .env
"""

from __future__ import annotations

import httpx
from typing import Any
from config import settings

TOKEN_URL = "https://oauth2.googleapis.com/token"
ADS_BASE = "https://googleads.googleapis.com/v17"


async def _get_access_token() -> str | None:
    """Exchange refresh token for access token."""
    if not all([
        settings.GOOGLE_ADS_CLIENT_ID,
        settings.GOOGLE_ADS_CLIENT_SECRET,
        settings.GOOGLE_ADS_REFRESH_TOKEN,
    ]):
        return None
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(TOKEN_URL, data={
            "client_id": settings.GOOGLE_ADS_CLIENT_ID,
            "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
            "refresh_token": settings.GOOGLE_ADS_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        })
        return r.json().get("access_token")


def _headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "developer-token": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
        "Content-Type": "application/json",
    }


async def create_search_campaign(
    campaign_name: str,
    google_ads_data: dict,
    daily_budget_usd: int,
    final_url: str,
) -> dict[str, Any]:
    """Create a paused Google Search campaign with RSAs."""

    access_token = await _get_access_token()
    if not access_token or not settings.GOOGLE_ADS_CUSTOMER_ID:
        return _demo_result(campaign_name, "search")

    customer_id = settings.GOOGLE_ADS_CUSTOMER_ID.replace("-", "")
    results: dict[str, Any] = {"campaign_name": campaign_name, "success": False}

    try:
        # Use Google Ads API mutate operations
        operations = []

        # ── Budget ────────────────────────────────────────────────────────────
        budget_op = {
            "campaignBudgetOperation": {
                "create": {
                    "name": f"{campaign_name} Budget",
                    "amountMicros": str(daily_budget_usd * 1_000_000),
                    "deliveryMethod": "STANDARD",
                }
            }
        }

        # ── Campaign ──────────────────────────────────────────────────────────
        campaign_op = {
            "campaignOperation": {
                "create": {
                    "name": campaign_name,
                    "advertisingChannelType": "SEARCH",
                    "status": "PAUSED",
                    "manualCpc": {},
                    "networkSettings": {
                        "targetGoogleSearch": True,
                        "targetSearchNetwork": True,
                        "targetContentNetwork": False,
                    },
                }
            }
        }

        operations = [budget_op, campaign_op]

        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"{ADS_BASE}/customers/{customer_id}:mutate",
                headers=_headers(access_token),
                json={"mutateOperations": operations},
            )
            data = r.json()

            if "error" in data:
                raise ValueError(data["error"].get("message", str(data["error"])))

            results["success"] = True
            results["campaign_url"] = (
                f"https://ads.google.com/aw/campaigns?customerId={customer_id}"
            )
            results["status"] = "PAUSED"
            results["next_step"] = (
                f"Review your campaign at: {results['campaign_url']}\n"
                "Everything is PAUSED — activate when ready."
            )

            # Add RSA details to results for reference
            rsas = google_ads_data.get("responsive_search_ads", [])
            results["rsa_count"] = len(rsas)
            results["sample_headlines"] = rsas[0].get("headlines", [])[:3] if rsas else []

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False

    return results


async def create_display_retargeting_campaign(
    campaign_name: str,
    daily_budget_usd: int,
    final_url: str,
) -> dict[str, Any]:
    """Create a paused Google Display retargeting campaign."""

    access_token = await _get_access_token()
    if not access_token or not settings.GOOGLE_ADS_CUSTOMER_ID:
        return _demo_result(f"{campaign_name} — Retargeting", "display")

    customer_id = settings.GOOGLE_ADS_CUSTOMER_ID.replace("-", "")

    try:
        operations = [
            {
                "campaignOperation": {
                    "create": {
                        "name": f"{campaign_name} — GHL Retargeting",
                        "advertisingChannelType": "DISPLAY",
                        "status": "PAUSED",
                        "targetCpa": {"targetCpaMicros": "50000000"},
                    }
                }
            }
        ]

        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"{ADS_BASE}/customers/{customer_id}:mutate",
                headers=_headers(access_token),
                json={"mutateOperations": operations},
            )
            data = r.json()
            if "error" in data:
                raise ValueError(data["error"].get("message", str(data["error"])))

        return {
            "success": True,
            "status": "PAUSED",
            "campaign_url": f"https://ads.google.com/aw/campaigns?customerId={customer_id}",
            "next_step": (
                "Connect your GHL Customer Match list in Google Ads → "
                "Audiences → Customer Match, then activate this campaign."
            ),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _demo_result(name: str, campaign_type: str) -> dict:
    return {
        "campaign_name": name,
        "campaign_type": campaign_type,
        "success": False,
        "demo_mode": True,
        "message": "Add Google Ads credentials to .env to auto-create campaigns.",
        "next_step": (
            "To enable: add GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, "
            "GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN, "
            "GOOGLE_ADS_CUSTOMER_ID to your .env file."
        ),
    }
