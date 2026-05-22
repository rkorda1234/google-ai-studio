"""Strategy Agent — full-funnel campaign strategy.

Takes research output and business context, produces a complete campaign strategy:
- Ideal Customer Profile (ICP)
- Funnel stages with messaging for each
- Budget allocation by platform
- KPIs and success metrics
"""

from __future__ import annotations

from typing import Any
import anthropic
from config import settings

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


async def build_strategy(
    business_description: str,
    target_audience: str,
    campaign_goal: str,
    monthly_budget: int,
    research_report: str,
    niche: str = "marketing agency",
    landing_page_context: str = "",
) -> dict[str, Any]:
    """Generate a comprehensive full-funnel campaign strategy."""

    system_prompt = (
        "You are an elite performance marketing strategist with 15+ years building "
        "full-funnel campaigns for marketing agencies. You specialize in creating "
        "campaigns that combine paid ads, lead magnets, and automated nurture sequences "
        "to deliver predictable, scalable lead flow. "
        "Be extremely specific — give numbers, timelines, and exact copy angles."
    )

    lp_section = f"\n## Landing Page Intelligence\n{landing_page_context}\n" if landing_page_context else ""

    prompt = f"""Based on the competitive research below, create a complete full-funnel campaign strategy.

## Business Context
- **Business:** {business_description}
- **Target Audience:** {target_audience}
- **Campaign Goal:** {campaign_goal}
- **Monthly Budget:** ${monthly_budget:,}
- **Niche:** {niche}
{lp_section}
## Competitive Research Summary
{research_report[:3000]}

---

Create a comprehensive strategy document with these exact sections:

## 1. Ideal Customer Profile (ICP)
- Demographics, firmographics, psychographics
- Pain points (top 3)
- Desired outcomes (top 3)
- Where they hang out online
- Objections to buying

## 2. Unique Mechanism & Positioning
- What makes us different from competitors
- Our core promise / transformation statement
- Brand voice & tone

## 3. Lead Magnet Strategy
- Primary lead magnet (title, format, what it delivers)
- Secondary lead magnet for retargeting
- Landing page conversion elements

## 4. Full Funnel Map
For each stage (Awareness → Interest → Consideration → Conversion → Retention):
- Platform & ad format
- Message/angle
- CTA
- Expected conversion rate

## 5. Platform Strategy & Budget Allocation
Break down the ${monthly_budget:,}/month budget across:
- Meta (Facebook/Instagram)
- Google Ads
- TikTok
With rationale for each allocation.

## 6. Content Calendar Overview
- 30-day content themes
- Post frequency per platform
- Content mix (educational / social proof / promotional)

## 7. KPIs & Success Metrics
- CPL (Cost Per Lead) target
- ROAS target
- Email open rate target
- Conversion rate benchmarks at each funnel stage

## 8. 90-Day Launch Roadmap
- Week 1-2: Setup
- Week 3-4: Launch & test
- Month 2: Optimize
- Month 3: Scale
"""

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=6000,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    strategy_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            strategy_text += block.text

    return {
        "strategy": strategy_text,
        "success": True,
        "tokens_used": response.usage.output_tokens,
    }
