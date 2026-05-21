"""n8n Agent — generates importable workflow JSON files.

Produces three core workflows:
1. Lead Capture → GHL Contact Creation
2. Email Nurture Sequence with delays
3. Retargeting Audience Builder (tags non-converters)

Also generates an n8n upload manifest so workflows can be pushed via API.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from config import settings
from tools.n8n_workflow_builder import (
    lead_capture_workflow,
    email_nurture_workflow,
    retargeting_workflow,
    workflow_to_json,
)


async def generate_all_workflows(
    email_sequence: list[dict],
    output_dir: Path,
) -> dict[str, Any]:
    """Generate and save all n8n workflows. Returns paths to the saved files."""

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Lead Capture
    lc_wf = lead_capture_workflow(
        ghl_api_key=settings.GHL_API_KEY or "{{GHL_API_KEY}}",
        ghl_location_id=settings.GHL_LOCATION_ID or "{{GHL_LOCATION_ID}}",
    )

    # 2. Email Nurture — convert sequence data to workflow nodes
    nurture_emails = _prepare_nurture_emails(email_sequence)
    nurture_wf = email_nurture_workflow(
        email_sequence=nurture_emails,
        ghl_api_key=settings.GHL_API_KEY or "{{GHL_API_KEY}}",
        ghl_location_id=settings.GHL_LOCATION_ID or "{{GHL_LOCATION_ID}}",
    )

    # 3. Retargeting
    retarget_wf = retargeting_workflow(
        ghl_api_key=settings.GHL_API_KEY or "{{GHL_API_KEY}}",
        ghl_location_id=settings.GHL_LOCATION_ID or "{{GHL_LOCATION_ID}}",
    )

    saved: dict[str, str] = {}

    for name, wf in [
        ("01_lead_capture", lc_wf),
        ("02_email_nurture", nurture_wf),
        ("03_retargeting", retarget_wf),
    ]:
        path = output_dir / f"{name}.json"
        path.write_text(workflow_to_json(wf), encoding="utf-8")
        saved[name] = str(path)

    # Save import manifest
    manifest = {
        "description": "Import these workflows into n8n in order",
        "import_order": list(saved.keys()),
        "files": saved,
        "post_import_steps": [
            "1. In each workflow, update credential references to use your actual credentials",
            "2. Set the GHL_API_KEY and GHL_LOCATION_ID variables in n8n Variables",
            "3. Configure the Webhook URLs in your landing page form",
            "4. Activate the Lead Capture workflow FIRST",
            "5. Test with a real form submission before activating nurture workflows",
        ],
    }
    manifest_path = output_dir / "00_import_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    saved["manifest"] = str(manifest_path)

    return {"workflows": saved, "success": True}


async def upload_workflows_to_n8n(workflow_files: list[str]) -> dict[str, Any]:
    """Upload generated workflow JSON files directly to n8n via API."""
    if not settings.N8N_API_KEY:
        return {"success": False, "message": "N8N_API_KEY not configured"}

    headers = {
        "X-N8N-API-KEY": settings.N8N_API_KEY,
        "Content-Type": "application/json",
    }
    results = []

    async with httpx.AsyncClient(timeout=30) as client:
        for wf_path in workflow_files:
            path = Path(wf_path)
            if not path.exists() or path.name.startswith("00_"):
                continue
            wf_data = json.loads(path.read_text())
            try:
                resp = await client.post(
                    f"{settings.N8N_BASE_URL}/api/v1/workflows",
                    json=wf_data,
                    headers=headers,
                )
                results.append({
                    "file": path.name,
                    "status": resp.status_code,
                    "workflow_id": resp.json().get("id"),
                    "success": resp.status_code in (200, 201),
                })
            except Exception as e:
                results.append({"file": path.name, "error": str(e), "success": False})

    return {"uploads": results, "success": all(r["success"] for r in results)}


def _prepare_nurture_emails(email_sequence: list[dict]) -> list[dict]:
    """Transform email sequence data into the format expected by the workflow builder."""
    prepared = []
    all_emails: list[dict] = []

    # Flatten from nested structure if needed
    if isinstance(email_sequence, list):
        all_emails = email_sequence
    elif isinstance(email_sequence, dict):
        sequences = email_sequence.get("sequences", {})
        welcome = sequences.get("welcome", {})
        for v in welcome.values():
            if isinstance(v, dict):
                all_emails.append(v)
        for item in sequences.get("nurture", []):
            all_emails.append(item)
        for item in sequences.get("conversion", []):
            all_emails.append(item)

    # Build simplified list for workflow builder
    prev_day = 0
    for email in all_emails[:10]:  # n8n workflows get complex fast — cap at 10
        day = email.get("day", 0)
        delay = max(0, day - prev_day)
        prepared.append({
            "subject": email.get("subject", "Follow up"),
            "html_body": email.get("body_html", email.get("body_plain", "Hi {{first_name}},")),
            "delay_days": delay,
        })
        prev_day = day

    return prepared
