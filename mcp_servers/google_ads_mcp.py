#!/usr/bin/env python3
"""Google Ads MCP Server — connects Claude desktop to your Google Ads account.

Exposes 5 tools Claude can call:
  - list_campaigns         → all campaigns + status + daily budget
  - get_campaign_performance → clicks, impressions, CTR, spend, conversions
  - get_keywords           → keyword bids, match types, performance
  - get_account_summary    → total spend, clicks, conversions for any date range
  - get_search_terms       → actual search queries that triggered your ads
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load .env from project root (two levels up: mcp_servers/ → project root)
load_dotenv(Path(__file__).parent.parent / ".env")

TOKEN_URL = "https://oauth2.googleapis.com/token"
ADS_BASE = "https://googleads.googleapis.com/v19"

mcp = FastMCP("Google Ads")


# ── Auth helpers ───────────────────────────────────────────────────────────────

async def _access_token() -> str:
    missing = [k for k in [
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CUSTOMER_ID",
    ] if not os.getenv(k)]
    if missing:
        raise ValueError(f"Missing credentials in .env: {', '.join(missing)}")

    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(TOKEN_URL, data={
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "grant_type": "refresh_token",
        })
        data = r.json()
        if "access_token" not in data:
            raise ValueError(f"OAuth failed: {data.get('error_description', data)}")
        return data["access_token"]


def _customer_id() -> str:
    return re.sub(r"[^0-9]", "", os.getenv("GOOGLE_ADS_CUSTOMER_ID", ""))


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "developer-token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
        "Content-Type": "application/json",
    }


async def _query(gaql: str) -> list[dict]:
    token = await _access_token()
    cid = _customer_id()
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            f"{ADS_BASE}/customers/{cid}/googleAds:search",
            headers=_headers(token),
            json={"query": gaql},
        )
        data = r.json()
        if isinstance(data, dict) and "error" in data:
            raise ValueError(data["error"].get("message", str(data["error"])))
        return data.get("results", [])


def _micros(value) -> float:
    return round(int(value or 0) / 1_000_000, 2)


# ── Tools ──────────────────────────────────────────────────────────────────────

@mcp.tool()
async def list_campaigns(status: str = "ALL") -> str:
    """List all Google Ads campaigns with their status, type, and daily budget.

    Args:
        status: Filter by status — ENABLED, PAUSED, REMOVED, or ALL (default)
    """
    where = "" if status == "ALL" else f"WHERE campaign.status = '{status}'"
    results = await _query(f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign_budget.amount_micros
        FROM campaign
        {where}
        ORDER BY campaign.name
        LIMIT 50
    """)

    campaigns = []
    for r in results:
        c = r.get("campaign", {})
        b = r.get("campaignBudget", {})
        campaigns.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "status": c.get("status"),
            "type": c.get("advertisingChannelType"),
            "daily_budget_usd": _micros(b.get("amountMicros", 0)),
        })

    return json.dumps(campaigns, indent=2)


@mcp.tool()
async def get_campaign_performance(
    date_range: str = "LAST_30_DAYS",
    campaign_name: str = "",
) -> str:
    """Get performance metrics for campaigns: impressions, clicks, CTR, CPC, spend, conversions.

    Args:
        date_range: LAST_7_DAYS, LAST_30_DAYS, LAST_MONTH, THIS_MONTH, LAST_YEAR, THIS_YEAR
        campaign_name: Optional — filter to a specific campaign (partial name match)
    """
    where_parts = [f"segments.date DURING {date_range}"]
    if campaign_name:
        where_parts.append(f"campaign.name LIKE '%{campaign_name}%'")
    where = "WHERE " + " AND ".join(where_parts)

    results = await _query(f"""
        SELECT
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions,
            metrics.cost_per_conversion
        FROM campaign
        {where}
        ORDER BY metrics.cost_micros DESC
        LIMIT 25
    """)

    rows = []
    for r in results:
        c = r.get("campaign", {})
        m = r.get("metrics", {})
        rows.append({
            "campaign": c.get("name"),
            "status": c.get("status"),
            "impressions": int(m.get("impressions", 0)),
            "clicks": int(m.get("clicks", 0)),
            "ctr_pct": round(float(m.get("ctr", 0)) * 100, 2),
            "avg_cpc_usd": _micros(m.get("averageCpc", 0)),
            "spend_usd": _micros(m.get("costMicros", 0)),
            "conversions": round(float(m.get("conversions", 0)), 1),
            "cost_per_conversion_usd": _micros(m.get("costPerConversion", 0)),
        })

    return json.dumps({"date_range": date_range, "campaigns": rows}, indent=2)


@mcp.tool()
async def get_account_summary(date_range: str = "LAST_30_DAYS") -> str:
    """Get overall account totals: spend, clicks, impressions, conversions.

    Args:
        date_range: LAST_7_DAYS, LAST_30_DAYS, LAST_MONTH, THIS_MONTH, LAST_YEAR
    """
    results = await _query(f"""
        SELECT
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions,
            metrics.cost_per_conversion
        FROM customer
        WHERE segments.date DURING {date_range}
    """)

    if not results:
        return json.dumps({"message": "No data found for this date range."})

    m = results[0].get("metrics", {})
    return json.dumps({
        "date_range": date_range,
        "total_impressions": int(m.get("impressions", 0)),
        "total_clicks": int(m.get("clicks", 0)),
        "avg_ctr_pct": round(float(m.get("ctr", 0)) * 100, 2),
        "avg_cpc_usd": _micros(m.get("averageCpc", 0)),
        "total_spend_usd": _micros(m.get("costMicros", 0)),
        "total_conversions": round(float(m.get("conversions", 0)), 1),
        "cost_per_conversion_usd": _micros(m.get("costPerConversion", 0)),
    }, indent=2)


@mcp.tool()
async def get_keywords(
    date_range: str = "LAST_30_DAYS",
    campaign_name: str = "",
) -> str:
    """Get keywords with bids, match types, and performance metrics.

    Args:
        date_range: LAST_7_DAYS, LAST_30_DAYS (default)
        campaign_name: Optional — filter to a specific campaign
    """
    where_parts = [f"segments.date DURING {date_range}"]
    if campaign_name:
        where_parts.append(f"campaign.name LIKE '%{campaign_name}%'")
    where = "WHERE " + " AND ".join(where_parts)

    results = await _query(f"""
        SELECT
            campaign.name,
            ad_group.name,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.cpc_bid_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions
        FROM keyword_view
        {where}
        ORDER BY metrics.cost_micros DESC
        LIMIT 50
    """)

    rows = []
    for r in results:
        kw = r.get("adGroupCriterion", {}).get("keyword", {})
        m = r.get("metrics", {})
        rows.append({
            "keyword": kw.get("text"),
            "match_type": kw.get("matchType"),
            "campaign": r.get("campaign", {}).get("name"),
            "ad_group": r.get("adGroup", {}).get("name"),
            "bid_usd": _micros(r.get("adGroupCriterion", {}).get("cpcBidMicros", 0)),
            "impressions": int(m.get("impressions", 0)),
            "clicks": int(m.get("clicks", 0)),
            "ctr_pct": round(float(m.get("ctr", 0)) * 100, 2),
            "avg_cpc_usd": _micros(m.get("averageCpc", 0)),
            "spend_usd": _micros(m.get("costMicros", 0)),
            "conversions": round(float(m.get("conversions", 0)), 1),
        })

    return json.dumps({"date_range": date_range, "keywords": rows}, indent=2)


@mcp.tool()
async def get_search_terms(
    date_range: str = "LAST_7_DAYS",
    min_clicks: int = 3,
) -> str:
    """Get the actual search queries that triggered your ads — great for finding negative keywords.

    Args:
        date_range: LAST_7_DAYS (default), LAST_30_DAYS
        min_clicks: Minimum clicks to include (default 3)
    """
    results = await _query(f"""
        SELECT
            search_term_view.search_term,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions
        FROM search_term_view
        WHERE segments.date DURING {date_range}
            AND metrics.clicks >= {min_clicks}
        ORDER BY metrics.clicks DESC
        LIMIT 50
    """)

    rows = []
    for r in results:
        m = r.get("metrics", {})
        rows.append({
            "search_term": r.get("searchTermView", {}).get("searchTerm"),
            "campaign": r.get("campaign", {}).get("name"),
            "impressions": int(m.get("impressions", 0)),
            "clicks": int(m.get("clicks", 0)),
            "ctr_pct": round(float(m.get("ctr", 0)) * 100, 2),
            "avg_cpc_usd": _micros(m.get("averageCpc", 0)),
            "spend_usd": _micros(m.get("costMicros", 0)),
            "conversions": round(float(m.get("conversions", 0)), 1),
        })

    return json.dumps({"date_range": date_range, "search_terms": rows}, indent=2)


if __name__ == "__main__":
    mcp.run()
