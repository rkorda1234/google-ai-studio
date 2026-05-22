"""Central configuration loaded from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Anthropic ─────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL: str = "claude-sonnet-4-6"

# ── Meta ──────────────────────────────────────────────────────────────────────
META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "")
META_AD_ACCOUNT_ID: str = os.getenv("META_AD_ACCOUNT_ID", "").replace("act_", "")  # store without act_ prefix
META_PAGE_ID: str = os.getenv("META_PAGE_ID", "")
META_API_VERSION: str = "v21.0"
META_GRAPH_BASE: str = f"https://graph.facebook.com/{META_API_VERSION}"

# ── GoHighLevel ───────────────────────────────────────────────────────────────
GHL_API_KEY: str = os.getenv("GHL_API_KEY", "")
GHL_LOCATION_ID: str = os.getenv("GHL_LOCATION_ID", "")
GHL_BASE_URL: str = "https://services.leadconnectorhq.com"

# ── Google Ads ────────────────────────────────────────────────────────────────
GOOGLE_ADS_DEVELOPER_TOKEN: str = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "")
GOOGLE_ADS_CLIENT_ID: str = os.getenv("GOOGLE_ADS_CLIENT_ID", "")
GOOGLE_ADS_CLIENT_SECRET: str = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "")
GOOGLE_ADS_REFRESH_TOKEN: str = os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "")
GOOGLE_ADS_CUSTOMER_ID: str = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "")

# ── n8n ───────────────────────────────────────────────────────────────────────
N8N_BASE_URL: str = os.getenv("N8N_BASE_URL", "http://localhost:5678")
N8N_API_KEY: str = os.getenv("N8N_API_KEY", "")

# ── Defaults ──────────────────────────────────────────────────────────────────
DEFAULT_COUNTRY: str = os.getenv("DEFAULT_COUNTRY", "US")
DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")
OUTPUT_DIR: Path = Path("output/campaigns")


def validate() -> list[str]:
    """Return list of missing required env vars."""
    required = {"ANTHROPIC_API_KEY": ANTHROPIC_API_KEY}
    return [k for k, v in required.items() if not v]
