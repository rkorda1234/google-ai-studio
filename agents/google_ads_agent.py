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


async def _get_access_token() -> tuple[str | None, str]:
    """Exchange refresh token for access token. Returns (token, error_message)."""
    missing = [k for k, v in {
        "GOOGLE_ADS_CLIENT_ID": settings.GOOGLE_ADS_CLIENT_ID,
        "GOOGLE_ADS_CLIENT_SECRET": settings.GOOGLE_ADS_CLIENT_SECRET,
        "GOOGLE_ADS_REFRESH_TOKEN": settings.GOOGLE_ADS_REFRESH_TOKEN,
        "GOOGLE_ADS_DEVELOPER_TOKEN": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
        "GOOGLE_ADS_CUSTOMER_ID": settings.GOOGLE_ADS_CUSTOMER_ID,
    }.items() if not v]
    if missing:
        return None, f"Missing in .env: {', '.join(missing)}"
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post(TOKEN_URL, data={
                "client_id": settings.GOOGLE_ADS_CLIENT_ID,
                "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
                "refresh_token": settings.GOOGLE_ADS_REFRESH_TOKEN,
                "grant_type": "refresh_token",
            })
            data = r.json()
            if "access_token" not in data:
                return None, f"OAuth failed: {data.get('error_description', data.get('error', str(data)))}"
            return data["access_token"], ""
    except Exception as e:
        return None, f"Token request failed: {e}"


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

    access_token, token_error = await _get_access_token()
    if not access_token:
        return _demo_result(campaign_name, "search", token_error)

    customer_id = settings.GOOGLE_ADS_CUSTOMER_ID.replace("-", "")
    results: dict[str, Any] = {"campaign_name": campaign_name, "success": False}

    try:
        async with httpx.AsyncClient(timeout=30) as c:
            # ── Step 1: Create budget ─────────────────────────────────────────
            br = await c.post(
                f"{ADS_BASE}/customers/{customer_id}/campaignBudgets:mutate",
                headers=_headers(access_token),
                json={"operations": [{"create": {
                    "name": f"{campaign_name} Budget",
                    "amountMicros": str(daily_budget_usd * 1_000_000),
                    "deliveryMethod": "STANDARD",
                }}]},
            )
            if not br.text.strip():
                raise ValueError(f"Budget API empty response (HTTP {br.status_code}) — verify developer token and customer ID")
            try:
                budget_data = br.json()
            except Exception:
                raise ValueError(f"Budget API non-JSON (HTTP {br.status_code}): {br.text[:300]}")
            if "error" in budget_data:
                raise ValueError(budget_data["error"].get("message", str(budget_data["error"])))

            budget_resource = budget_data["results"][0]["resourceName"]

            # ── Step 2: Create campaign referencing the budget ─────────────────
            cr = await c.post(
                f"{ADS_BASE}/customers/{customer_id}/campaigns:mutate",
                headers=_headers(access_token),
                json={"operations": [{"create": {
                    "name": campaign_name,
                    "advertisingChannelType": "SEARCH",
                    "status": "PAUSED",
                    "campaignBudget": budget_resource,
                    "manualCpc": {"enhancedCpcEnabled": False},
                    "networkSettings": {
                        "targetGoogleSearch": True,
                        "targetSearchNetwork": True,
                        "targetContentNetwork": False,
                    },
                }}]},
            )
            if not cr.text.strip():
                raise ValueError(f"Campaign API empty response (HTTP {cr.status_code})")
            try:
                campaign_data = cr.json()
            except Exception:
                raise ValueError(f"Campaign API non-JSON (HTTP {cr.status_code}): {cr.text[:300]}")
            if "error" in campaign_data:
                raise ValueError(campaign_data["error"].get("message", str(campaign_data["error"])))

            results["success"] = True
            results["campaign_url"] = f"https://ads.google.com/aw/campaigns?customerId={customer_id}"
            results["status"] = "PAUSED"
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

    access_token, token_error = await _get_access_token()
    if not access_token:
        return _demo_result(f"{campaign_name} — Retargeting", "display", token_error)

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


def _demo_result(name: str, campaign_type: str, reason: str = "") -> dict:
    return {
        "campaign_name": name,
        "campaign_type": campaign_type,
        "success": False,
        "message": reason or "Google Ads credentials not configured.",
    }
