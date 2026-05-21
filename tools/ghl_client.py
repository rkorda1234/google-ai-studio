"""GoHighLevel API v2 client.

Docs: https://highlevel.stoplight.io/docs/integrations
"""

from __future__ import annotations

import httpx
from typing import Any
from config import settings

HEADERS = {
    "Authorization": f"Bearer {settings.GHL_API_KEY}",
    "Content-Type": "application/json",
    "Version": "2021-07-28",
}


class GHLClient:
    """Async HTTP client wrapping the GHL REST API v2."""

    def __init__(self):
        self.base = settings.GHL_BASE_URL
        self.location_id = settings.GHL_LOCATION_ID

    # ── Contacts ──────────────────────────────────────────────────────────────

    async def create_contact(self, data: dict[str, Any]) -> dict[str, Any]:
        payload = {**data, "locationId": self.location_id}
        return await self._post("/contacts/", payload)

    async def update_contact(self, contact_id: str, data: dict) -> dict:
        return await self._put(f"/contacts/{contact_id}", data)

    async def get_contact(self, contact_id: str) -> dict:
        return await self._get(f"/contacts/{contact_id}")

    # ── Pipelines & Opportunities ─────────────────────────────────────────────

    async def get_pipelines(self) -> dict:
        return await self._get(f"/opportunities/pipelines?locationId={self.location_id}")

    async def create_pipeline(self, name: str, stages: list[dict]) -> dict:
        payload = {
            "locationId": self.location_id,
            "name": name,
            "stages": stages,
        }
        return await self._post("/opportunities/pipelines", payload)

    async def create_opportunity(self, data: dict) -> dict:
        payload = {**data, "locationId": self.location_id}
        return await self._post("/opportunities/", payload)

    # ── Campaigns ─────────────────────────────────────────────────────────────

    async def get_campaigns(self) -> dict:
        return await self._get(f"/campaigns/?locationId={self.location_id}")

    # ── Email Templates ───────────────────────────────────────────────────────

    async def create_email_template(
        self, name: str, subject: str, html_body: str
    ) -> dict:
        payload = {
            "locationId": self.location_id,
            "name": name,
            "subject": subject,
            "body": html_body,
            "type": "email",
        }
        return await self._post("/templates/", payload)

    async def list_email_templates(self) -> dict:
        return await self._get(f"/templates/?locationId={self.location_id}&type=email")

    # ── SMS Templates ─────────────────────────────────────────────────────────

    async def create_sms_template(self, name: str, body: str) -> dict:
        payload = {
            "locationId": self.location_id,
            "name": name,
            "body": body,
            "type": "sms",
        }
        return await self._post("/templates/", payload)

    # ── Workflows (Automations) ────────────────────────────────────────────────

    async def list_workflows(self) -> dict:
        return await self._get(f"/workflows/?locationId={self.location_id}")

    # ── Custom Fields ─────────────────────────────────────────────────────────

    async def create_custom_field(
        self, name: str, field_key: str, data_type: str = "TEXT"
    ) -> dict:
        payload = {
            "locationId": self.location_id,
            "name": name,
            "fieldKey": field_key,
            "dataType": data_type,
        }
        return await self._post("/locations/customFields", payload)

    # ── Tags ──────────────────────────────────────────────────────────────────

    async def create_tag(self, name: str) -> dict:
        return await self._post(
            f"/locations/{self.location_id}/tags", {"name": name}
        )

    # ── HTTP helpers ──────────────────────────────────────────────────────────

    async def _get(self, path: str) -> dict:
        if not settings.GHL_API_KEY:
            return {"_demo": True, "message": "GHL not configured"}
        async with httpx.AsyncClient(headers=HEADERS, timeout=30) as c:
            r = await c.get(f"{self.base}{path}")
            r.raise_for_status()
            return r.json()

    async def _post(self, path: str, payload: dict) -> dict:
        if not settings.GHL_API_KEY:
            return {"_demo": True, "message": "GHL not configured", "payload": payload}
        async with httpx.AsyncClient(headers=HEADERS, timeout=30) as c:
            r = await c.post(f"{self.base}{path}", json=payload)
            r.raise_for_status()
            return r.json()

    async def _put(self, path: str, payload: dict) -> dict:
        if not settings.GHL_API_KEY:
            return {"_demo": True, "message": "GHL not configured"}
        async with httpx.AsyncClient(headers=HEADERS, timeout=30) as c:
            r = await c.put(f"{self.base}{path}", json=payload)
            r.raise_for_status()
            return r.json()
