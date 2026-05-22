"""Landing page scraper — extracts marketing intelligence from a URL.

Crawls the landing page and extracts:
- Headline & subheadline
- Value proposition & offer
- Pain points & desired outcomes
- CTA button text
- Bullet points / features
- Testimonials & social proof
- Pricing (if visible)

This data is passed to all agents so ads, emails, and strategy
are perfectly aligned with the actual landing page messaging.
"""

from __future__ import annotations

import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

import anthropic
from config import settings

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


async def scrape_landing_page(url: str) -> dict[str, Any]:
    """Fetch and extract marketing elements from a landing page URL."""

    if not url or not url.startswith("http"):
        return {"success": False, "reason": "No valid URL provided"}

    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            },
        ) as client_http:
            resp = await client_http.get(url)
            if resp.status_code != 200:
                return {"success": False, "reason": f"Page returned {resp.status_code}"}
            html = resp.text
    except Exception as e:
        return {"success": False, "reason": str(e)}

    soup = BeautifulSoup(html, "html.parser")

    # ── Raw extraction ────────────────────────────────────────────────────────

    raw = {
        "title": _get_title(soup),
        "h1": _get_text(soup, "h1"),
        "h2s": _get_all_text(soup, "h2"),
        "h3s": _get_all_text(soup, "h3"),
        "bullets": _get_bullets(soup),
        "cta_buttons": _get_ctas(soup),
        "testimonials": _get_testimonials(soup),
        "paragraphs": _get_paragraphs(soup),
        "url": url,
    }

    # ── AI analysis — extract structured marketing intel ──────────────────────
    analysis = await _analyze_with_claude(raw)

    return {
        "success": True,
        "url": url,
        "raw": raw,
        "analysis": analysis,
    }


async def _analyze_with_claude(raw: dict) -> dict[str, Any]:
    """Use Claude to turn raw scraped text into structured marketing intelligence."""

    page_text = f"""
Title: {raw['title']}
H1: {raw['h1']}
H2s: {' | '.join(raw['h2s'][:5])}
H3s: {' | '.join(raw['h3s'][:5])}
CTAs: {' | '.join(raw['cta_buttons'][:5])}
Bullets: {chr(10).join(raw['bullets'][:10])}
Paragraphs: {chr(10).join(raw['paragraphs'][:5])}
Testimonials: {chr(10).join(raw['testimonials'][:3])}
"""

    prompt = f"""Analyze this landing page content and extract the key marketing elements.

LANDING PAGE CONTENT:
{page_text[:3000]}

Return a JSON object with these exact fields:
{{
  "main_headline": "the primary headline/value proposition",
  "offer": "what they are offering (product/service/lead magnet)",
  "target_audience": "who this page is targeting",
  "pain_points": ["pain point 1", "pain point 2", "pain point 3"],
  "desired_outcomes": ["outcome 1", "outcome 2", "outcome 3"],
  "key_benefits": ["benefit 1", "benefit 2", "benefit 3"],
  "social_proof": "testimonials or credibility indicators found",
  "cta": "the main call to action",
  "tone": "professional/casual/urgent/friendly etc",
  "unique_differentiators": ["what makes this different from competitors"],
  "ad_angles": ["3 ad angles that would resonate with this audience based on the page"]
}}

Return ONLY valid JSON, no other text."""

    try:
        response = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text
        start = text.find("{")
        end = text.rfind("}") + 1
        import json
        return json.loads(text[start:end])
    except Exception:
        return {
            "main_headline": raw.get("h1", ""),
            "offer": raw.get("title", ""),
            "cta": raw.get("cta_buttons", [""])[0] if raw.get("cta_buttons") else "",
        }


# ── HTML helpers ──────────────────────────────────────────────────────────────

def _get_title(soup: BeautifulSoup) -> str:
    tag = soup.find("title")
    return tag.get_text(strip=True) if tag else ""


def _get_text(soup: BeautifulSoup, tag: str) -> str:
    el = soup.find(tag)
    return el.get_text(strip=True) if el else ""


def _get_all_text(soup: BeautifulSoup, tag: str) -> list[str]:
    return [el.get_text(strip=True) for el in soup.find_all(tag) if el.get_text(strip=True)]


def _get_bullets(soup: BeautifulSoup) -> list[str]:
    items = []
    for el in soup.find_all(["li", "ul"]):
        text = el.get_text(strip=True)
        if text and len(text) > 5 and len(text) < 200:
            items.append(text)
    return list(dict.fromkeys(items))[:15]


def _get_ctas(soup: BeautifulSoup) -> list[str]:
    ctas = []
    for el in soup.find_all(["button", "a"]):
        text = el.get_text(strip=True)
        classes = " ".join(el.get("class", []))
        is_cta = any(k in classes.lower() for k in ["btn", "button", "cta", "submit"])
        if text and is_cta and len(text) < 60:
            ctas.append(text)
    return list(dict.fromkeys(ctas))[:8]


def _get_testimonials(soup: BeautifulSoup) -> list[str]:
    testimonials = []
    patterns = ["testimonial", "review", "quote", "social-proof", "feedback"]
    for pattern in patterns:
        for el in soup.find_all(class_=re.compile(pattern, re.I)):
            text = el.get_text(strip=True)
            if text and len(text) > 20:
                testimonials.append(text[:300])
    return list(dict.fromkeys(testimonials))[:5]


def _get_paragraphs(soup: BeautifulSoup) -> list[str]:
    paras = []
    for el in soup.find_all("p"):
        text = el.get_text(strip=True)
        if text and len(text) > 40:
            paras.append(text[:300])
    return paras[:8]
