"""Facebook Ad Library API client.

Requires a Meta user access token with ads_read permission.
Docs: https://www.facebook.com/ads/library/api/
"""

from __future__ import annotations

import httpx
from typing import Any
from config import settings


AD_LIBRARY_ENDPOINT = f"{settings.META_GRAPH_BASE}/ads_archive"

AD_FIELDS = ",".join([
    "id",
    "ad_creation_time",
    "ad_creative_bodies",
    "ad_creative_link_captions",
    "ad_creative_link_descriptions",
    "ad_creative_link_titles",
    "ad_delivery_start_time",
    "ad_delivery_stop_time",
    "ad_snapshot_url",
    "currency",
    "spend",
    "impressions",
    "page_name",
    "page_id",
    "languages",
    "publisher_platforms",
    "target_ages",
    "target_gender",
    "bylines",
])


async def search_ads(
    search_terms: str,
    countries: list[str] | None = None,
    ad_type: str = "ALL",
    limit: int = 20,
) -> dict[str, Any]:
    """Search the Facebook Ad Library for ads matching search_terms.

    Returns raw API response dict with 'data' list of ad objects.
    Falls back to a stub response if no token is configured so the rest
    of the pipeline can still run in demo mode.
    """
    if not settings.META_ACCESS_TOKEN:
        return _demo_response(search_terms)

    params: dict[str, Any] = {
        "access_token": settings.META_ACCESS_TOKEN,
        "ad_type": ad_type,
        "ad_reached_countries": countries or [settings.DEFAULT_COUNTRY],
        "search_terms": search_terms,
        "fields": AD_FIELDS,
        "limit": limit,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(AD_LIBRARY_ENDPOINT, params=params)
            if resp.status_code != 200:
                return _demo_response(search_terms)
            return resp.json()
    except Exception:
        return _demo_response(search_terms)


async def get_page_ads(page_id: str, limit: int = 10) -> dict[str, Any]:
    """Fetch all active ads for a specific Facebook page."""
    if not settings.META_ACCESS_TOKEN:
        return _demo_response(f"page:{page_id}")

    params: dict[str, Any] = {
        "access_token": settings.META_ACCESS_TOKEN,
        "ad_type": "ALL",
        "ad_reached_countries": [settings.DEFAULT_COUNTRY],
        "search_page_ids": page_id,
        "fields": AD_FIELDS,
        "limit": limit,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(AD_LIBRARY_ENDPOINT, params=params)
            if resp.status_code != 200:
                return _demo_response(f"page:{page_id}")
            return resp.json()
    except Exception:
        return _demo_response(f"page:{page_id}")


def summarize_ads(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract the key fields from a raw API response into a clean list."""
    ads = raw.get("data", [])
    summaries = []
    for ad in ads:
        summaries.append({
            "page": ad.get("page_name", "Unknown"),
            "created": ad.get("ad_creation_time", ""),
            "platforms": ad.get("publisher_platforms", []),
            "headline": _first(ad.get("ad_creative_link_titles", [])),
            "body": _first(ad.get("ad_creative_bodies", [])),
            "description": _first(ad.get("ad_creative_link_descriptions", [])),
            "cta_caption": _first(ad.get("ad_creative_link_captions", [])),
            "spend": ad.get("spend", {}),
            "impressions": ad.get("impressions", {}),
            "snapshot_url": ad.get("ad_snapshot_url", ""),
        })
    return summaries


def _first(lst: list) -> str:
    return lst[0] if lst else ""


def _demo_response(term: str) -> dict[str, Any]:
    """Stub response used when no Meta token is set (demo / test mode)."""
    return {
        "data": [
            {
                "id": "demo_001",
                "page_name": "MarketingPro Agency",
                "ad_creation_time": "2024-11-01T00:00:00+0000",
                "ad_creative_bodies": [
                    f"Struggling to get leads for your {term} business? "
                    "We help agencies 3x their pipeline in 90 days. "
                    "Book a free strategy call today."
                ],
                "ad_creative_link_titles": ["Free Strategy Call — Limited Spots"],
                "ad_creative_link_descriptions": [
                    "See exactly how we generated 847 qualified leads last month."
                ],
                "ad_creative_link_captions": ["Book Now →"],
                "publisher_platforms": ["facebook", "instagram"],
                "spend": {"lower_bound": "1000", "upper_bound": "5000"},
                "impressions": {"lower_bound": "50000", "upper_bound": "100000"},
                "ad_snapshot_url": "https://www.facebook.com/ads/library/",
            },
            {
                "id": "demo_002",
                "page_name": "ScaleUp Digital",
                "ad_creation_time": "2024-10-15T00:00:00+0000",
                "ad_creative_bodies": [
                    "WARNING: Most agencies are leaving 70% of their revenue on the table. "
                    "Our proven system fills your calendar with ready-to-buy clients. "
                    "Download the FREE playbook."
                ],
                "ad_creative_link_titles": ["The Agency Growth Playbook (FREE)"],
                "ad_creative_link_descriptions": [
                    "Download instantly. No credit card required."
                ],
                "ad_creative_link_captions": ["Get Free Playbook"],
                "publisher_platforms": ["facebook"],
                "spend": {"lower_bound": "5000", "upper_bound": "10000"},
                "impressions": {"lower_bound": "200000", "upper_bound": "500000"},
                "ad_snapshot_url": "https://www.facebook.com/ads/library/",
            },
        ],
        "_demo": True,
    }
