"""Campaign Orchestrator — coordinates all agents into a single pipeline.

Flow:
  Research → Strategy → Creatives (parallel) → Email/SMS → GHL Setup
  → Meta Campaign (paused) → Google Campaign (paused)
  All outputs written to output/campaigns/<campaign_slug>/
  n8n is skipped — GHL handles all lead capture, nurture, and tagging.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from slugify import slugify

from agents.research_agent import run_research
from agents.strategy_agent import build_strategy
from agents.creative_agent import (
    generate_google_ads,
    generate_meta_ads,
    generate_tiktok_ads,
    generate_lead_magnet,
)
from agents.email_sms_agent import (
    generate_email_sequence,
    generate_sms_sequence,
    generate_retargeting_emails,
)
from agents.ghl_agent import setup_ghl_account
from agents.meta_campaign_agent import create_full_campaign as create_meta_campaign
from agents.google_ads_agent import create_search_campaign as create_google_campaign


class CampaignOrchestrator:
    """Coordinates the full campaign generation pipeline."""

    def __init__(self, base_output_dir: str = "output/campaigns"):
        self.base_output_dir = Path(base_output_dir)

    async def generate_campaign(
        self,
        business: str,
        target_audience: str,
        campaign_goal: str,
        monthly_budget: int,
        competitor_keywords: list[str] | None = None,
        landing_page_url: str = "",
        campaign_name: str | None = None,
        output_dir: str | None = None,
        on_progress: Any = None,
    ) -> dict[str, Any]:
        """Run the full campaign generation pipeline."""

        def _progress(step: str, pct: int):
            if on_progress:
                asyncio.create_task(on_progress(step, pct))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        slug = slugify(campaign_name or f"{business[:30]}-{timestamp}")
        campaign_dir = Path(output_dir or self.base_output_dir) / slug
        campaign_dir.mkdir(parents=True, exist_ok=True)

        results: dict[str, Any] = {
            "campaign_slug": slug,
            "output_dir": str(campaign_dir),
            "steps": {},
        }

        # ─── Step 1: Research ─────────────────────────────────────────────────
        _progress("research", 5)
        research_result = await run_research(
            business_description=business,
            target_audience=target_audience,
            competitor_keywords=competitor_keywords or [],
        )
        results["steps"]["research"] = research_result["success"]
        _save(campaign_dir / "01_research_report.md", research_result["report"])

        # ─── Step 2: Strategy ─────────────────────────────────────────────────
        _progress("strategy", 18)
        strategy_result = await build_strategy(
            business_description=business,
            target_audience=target_audience,
            campaign_goal=campaign_goal,
            monthly_budget=monthly_budget,
            research_report=research_result["report"],
        )
        results["steps"]["strategy"] = strategy_result["success"]
        _save(campaign_dir / "02_strategy.md", strategy_result["strategy"])

        strategy_text = strategy_result["strategy"]
        icp_summary = _extract_section(strategy_text, "Ideal Customer Profile") or target_audience
        offer = _extract_section(strategy_text, "Unique Mechanism") or campaign_goal

        # ─── Step 3: Creatives (parallel) ─────────────────────────────────────
        _progress("creatives", 32)

        ads_dir = campaign_dir / "03_ads"
        ads_dir.mkdir(exist_ok=True)

        google_result, meta_result, tiktok_result, lm_result = await asyncio.gather(
            generate_google_ads(
                icp_summary=icp_summary,
                offer=offer,
                keywords=competitor_keywords or ["marketing agency", "lead generation"],
                landing_page_url=landing_page_url or "{{your_landing_page_url}}",
            ),
            generate_meta_ads(
                icp_summary=icp_summary,
                offer=offer,
                lead_magnet="Free Lead Generation Playbook",
            ),
            generate_tiktok_ads(
                icp_summary=icp_summary,
                offer=offer,
                lead_magnet="Free Lead Generation Playbook",
            ),
            generate_lead_magnet(
                icp_summary=icp_summary,
                pain_points="Not enough qualified leads, high CAC, unpredictable pipeline",
                desired_outcome="Consistent flow of qualified leads on autopilot",
            ),
        )

        _save_json(ads_dir / "google_ads.json", google_result.get("creatives", {}))
        _save_json(ads_dir / "meta_ads.json", meta_result.get("creatives", {}))
        _save_json(ads_dir / "tiktok_ads.json", tiktok_result.get("creatives", {}))
        _save_json(campaign_dir / "04_lead_magnet" / "lead_magnet.json", lm_result.get("lead_magnet", {}))

        results["steps"]["creatives"] = all([
            google_result["success"],
            meta_result["success"],
            tiktok_result["success"],
            lm_result["success"],
        ])

        lead_magnet_title = (
            lm_result.get("lead_magnet", {})
            .get("primary_lead_magnet", {})
            .get("title", "Free Marketing Playbook")
        )

        # ─── Step 4: Email & SMS (parallel) ───────────────────────────────────
        _progress("email_sms", 52)

        email_result, sms_result, retarget_email_result = await asyncio.gather(
            generate_email_sequence(
                business_description=business,
                icp_summary=icp_summary,
                lead_magnet_title=lead_magnet_title,
                offer=offer,
            ),
            generate_sms_sequence(
                business_description=business,
                icp_summary=icp_summary,
                lead_magnet_title=lead_magnet_title,
                offer=offer,
            ),
            generate_retargeting_emails(
                icp_summary=icp_summary,
                offer=offer,
                reason_they_didnt_convert=(
                    "No time, unsure of ROI, haven't finished the lead magnet, "
                    "comparing with competitors"
                ),
            ),
        )

        email_dir = campaign_dir / "05_email_sequences"
        sms_dir = campaign_dir / "06_sms_sequences"
        email_dir.mkdir(exist_ok=True)
        sms_dir.mkdir(exist_ok=True)

        _save_json(email_dir / "nurture_sequence.json", email_result.get("email_sequence", {}))
        _save_json(sms_dir / "sms_sequence.json", sms_result.get("sms_sequence", {}))
        _save_json(email_dir / "retargeting_emails.json", retarget_email_result.get("retargeting_emails", {}))

        results["steps"]["email_sms"] = all([
            email_result["success"],
            sms_result["success"],
            retarget_email_result["success"],
        ])

        # ─── Step 5: GHL Setup ─────────────────────────────────────────────────
        _progress("ghl_setup", 68)

        ghl_result = await setup_ghl_account(
            pipeline_name=f"{business[:40]} — Lead Pipeline",
            email_sequence=email_result.get("email_sequence", {}),
            sms_sequence=sms_result.get("sms_sequence", {}),
            output_dir=campaign_dir,
        )
        results["steps"]["ghl"] = ghl_result["success"]

        # ─── Step 6: Meta Campaign (paused) ───────────────────────────────────
        _progress("meta_campaign", 78)

        meta_budget = int(monthly_budget * 0.5 / 30)  # 50% of budget, daily
        meta_campaign_result = await create_meta_campaign(
            campaign_name=slug,
            ad_creatives=meta_result.get("creatives", {}),
            daily_budget_usd=meta_budget,
            landing_page_url=landing_page_url or "{{your_landing_page_url}}",
        )
        _save_json(campaign_dir / "03_ads" / "meta_campaign_result.json", meta_campaign_result)
        results["steps"]["meta_campaign"] = meta_campaign_result.get("success", False)
        results["meta_campaign_url"] = meta_campaign_result.get("campaign_url", "")

        # ─── Step 7: Google Campaign (paused) ─────────────────────────────────
        _progress("google_campaign", 88)

        google_budget = int(monthly_budget * 0.4 / 30)  # 40% of budget, daily
        google_campaign_result = await create_google_campaign(
            campaign_name=slug,
            google_ads_data=google_result.get("creatives", {}),
            daily_budget_usd=google_budget,
            final_url=landing_page_url or "{{your_landing_page_url}}",
        )
        _save_json(campaign_dir / "03_ads" / "google_campaign_result.json", google_campaign_result)
        results["steps"]["google_campaign"] = google_campaign_result.get("success", False)
        results["google_campaign_url"] = google_campaign_result.get("campaign_url", "")

        # ─── Summary ──────────────────────────────────────────────────────────
        _progress("summary", 96)
        summary = _build_summary(
            slug, business, campaign_goal, monthly_budget,
            campaign_dir, results, meta_campaign_result, google_campaign_result,
        )
        _save(campaign_dir / "campaign_summary.md", summary)

        _progress("done", 100)

        results["success"] = True  # partial success is still useful
        results["output_path"] = str(campaign_dir)
        results["summary"] = summary

        return results


# ── Helpers ───────────────────────────────────────────────────────────────────

def _save(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content or "", encoding="utf-8")


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _extract_section(text: str, section_title: str) -> str:
    lines = text.split("\n")
    capturing = False
    out = []
    for line in lines:
        if section_title.lower() in line.lower() and line.startswith("#"):
            capturing = True
            continue
        if capturing and line.startswith("#"):
            break
        if capturing:
            out.append(line)
    return "\n".join(out).strip()


def _build_summary(
    slug: str,
    business: str,
    goal: str,
    budget: int,
    output_dir: Path,
    results: dict,
    meta_result: dict,
    google_result: dict,
) -> str:
    steps_status = "\n".join(
        f"- {'✅' if v else '⚠️ (needs credentials)'} {k.replace('_', ' ').title()}"
        for k, v in results.get("steps", {}).items()
    )

    meta_url = meta_result.get("campaign_url", "")
    google_url = google_result.get("campaign_url", "")
    meta_line = f"[Review in Meta Ads Manager]({meta_url})" if meta_url else "Add META credentials to .env to auto-create"
    google_line = f"[Review in Google Ads]({google_url})" if google_url else "Add Google Ads credentials to .env to auto-create"

    return f"""# Campaign Package Summary

**Campaign:** {slug}
**Business:** {business}
**Goal:** {goal}
**Monthly Budget:** ${budget:,}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Generation Status
{steps_status}

---

## Ad Campaigns Created (PAUSED — review before activating)

| Platform | Status | Link |
|----------|--------|------|
| Meta (FB/IG) | ⏸ PAUSED | {meta_line} |
| Google Ads | ⏸ PAUSED | {google_line} |

---

## Package Contents

| File | Contents |
|------|----------|
| `01_research_report.md` | Competitor ad analysis & market insights |
| `02_strategy.md` | Full-funnel strategy & 90-day roadmap |
| `03_ads/meta_ads.json` | Facebook/Instagram ad copy + video scripts |
| `03_ads/google_ads.json` | Google RSAs + keywords |
| `03_ads/tiktok_ads.json` | TikTok scripts |
| `04_lead_magnet/` | Lead magnet concept + landing page copy |
| `05_email_sequences/` | 14-email nurture + 5-email retargeting |
| `06_sms_sequences/` | SMS drip sequence |
| `08_ghl_setup/setup_guide.md` | GHL pipeline + retargeting audience sync |

---

## GHL Workflow Setup (one time)

Tag to use for retargeting: **`retarget-ready`**

In GHL Workflows, create:
```
Trigger: Tag Added = "retarget-ready"
Action 1: Add to Facebook Custom Audience → "GHL Non-Converters"
Action 2: Add to Google Ads Customer List → "GHL Non-Converters"
```

After this, every tagged lead automatically gets retargeting ads on Meta + Google. ✅
"""
