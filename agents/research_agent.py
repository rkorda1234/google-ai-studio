"""Research Agent — competitor ad intelligence & market analysis.

Uses Claude with tool use to search the Facebook Ad Library and
analyze Instagram content patterns, then synthesizes a research report.
"""

from __future__ import annotations

import json
from typing import Any

import anthropic

from config import settings
from tools.facebook_ad_library import search_ads, summarize_ads
from tools.instagram_research import get_top_marketing_accounts, analyze_content_patterns

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

TOOLS: list[dict] = [
    {
        "name": "search_facebook_ad_library",
        "description": (
            "Search the Facebook Ad Library for competitor ads. "
            "Returns ad copy, spend data, platforms, and creative details."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "search_terms": {
                    "type": "string",
                    "description": "Keywords to search (e.g. 'marketing agency leads')",
                },
                "countries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "ISO country codes, e.g. ['US', 'CA']",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of ads to return (max 30)",
                    "default": 10,
                },
            },
            "required": ["search_terms"],
        },
    },
    {
        "name": "get_instagram_account_insights",
        "description": (
            "Retrieve curated insights from top marketing and social media "
            "Instagram accounts — hook styles, CTAs, content pillars, patterns."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


async def _execute_tool(name: str, inputs: dict) -> str:
    if name == "search_facebook_ad_library":
        raw = await search_ads(
            search_terms=inputs["search_terms"],
            countries=inputs.get("countries"),
            limit=inputs.get("limit", 10),
        )
        ads = summarize_ads(raw)
        demo = raw.get("_demo", False)
        return json.dumps({"ads": ads, "count": len(ads), "demo_mode": demo})

    if name == "get_instagram_account_insights":
        accounts = await get_top_marketing_accounts()
        patterns = await analyze_content_patterns(accounts)
        return json.dumps({"accounts": accounts, "patterns": patterns})

    return json.dumps({"error": f"Unknown tool: {name}"})


async def run_research(
    business_description: str,
    target_audience: str,
    competitor_keywords: list[str],
    niche: str = "marketing agency",
) -> dict[str, Any]:
    """Run the full research pipeline and return a structured report."""

    keywords = competitor_keywords or [niche, "lead generation", "digital marketing agency"]
    keyword_str = ", ".join(keywords)

    system_prompt = (
        "You are a world-class digital marketing strategist and competitive intelligence analyst. "
        "Your job is to research competitor ads and content patterns, then synthesize actionable "
        "insights a marketing agency can use to build better-performing campaigns. "
        "Be specific, data-driven, and practical. Focus on WHAT is working and WHY."
    )

    user_message = f"""Research competitor advertising for a marketing agency with the following context:

**Business:** {business_description}
**Target Audience:** {target_audience}
**Keywords to Research:** {keyword_str}

Please:
1. Search the Facebook Ad Library for ads related to: {keyword_str}
2. Get Instagram content pattern insights from top marketing accounts
3. Analyze what's working: hooks, offers, CTAs, formats, angles
4. Identify gaps and opportunities

Then produce a comprehensive research report covering:
- Top-performing ad angles and hooks
- Winning offer structures (lead magnets, free trials, etc.)
- Platform-specific creative patterns (FB vs IG vs TikTok)
- Content themes that dominate the space
- 5 specific recommendations for differentiating our campaigns
"""

    messages = [{"role": "user", "content": user_message}]

    # Agentic tool-use loop
    tool_results: dict[str, Any] = {}
    max_iterations = 5

    for _ in range(max_iterations):
        response = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            # Extract final text
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            return {
                "report": final_text,
                "raw_tool_results": tool_results,
                "success": True,
            }

        if response.stop_reason == "tool_use":
            # Process tool calls
            messages.append({"role": "assistant", "content": response.content})
            tool_result_blocks = []

            for block in response.content:
                if block.type == "tool_use":
                    result_str = await _execute_tool(block.name, block.input)
                    tool_results[block.name] = json.loads(result_str)
                    tool_result_blocks.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_str,
                    })

            messages.append({"role": "user", "content": tool_result_blocks})
            continue

        break

    return {"report": "Research incomplete.", "raw_tool_results": tool_results, "success": False}
