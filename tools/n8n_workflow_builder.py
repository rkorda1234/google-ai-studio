"""Programmatic n8n workflow JSON builder.

Generates importable workflow JSON for n8n.
Supports: Webhook triggers, HTTP requests, IF conditions, Wait, Set, Email.
"""

from __future__ import annotations

import uuid
import json
from typing import Any


def _id() -> str:
    return str(uuid.uuid4())


def _pos(x: int, y: int) -> list[int]:
    return [x, y]


# ── Node builders ────────────────────────────────────────────────────────────

def webhook_node(name: str, path: str, pos: list[int]) -> dict:
    return {
        "parameters": {
            "path": path,
            "responseMode": "responseNode",
            "options": {},
        },
        "id": _id(),
        "name": name,
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": pos,
        "webhookId": _id(),
    }


def http_request_node(
    name: str,
    url: str,
    method: str,
    body: dict | None,
    headers: dict | None,
    pos: list[int],
) -> dict:
    node: dict[str, Any] = {
        "parameters": {
            "method": method.upper(),
            "url": url,
            "options": {},
        },
        "id": _id(),
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": pos,
    }
    if body:
        node["parameters"]["sendBody"] = True
        node["parameters"]["contentType"] = "json"
        node["parameters"]["body"] = {"values": [{"name": k, "value": v} for k, v in body.items()]}
    if headers:
        node["parameters"]["sendHeaders"] = True
        node["parameters"]["headers"] = {"parameters": [{"name": k, "value": v} for k, v in headers.items()]}
    return node


def set_node(name: str, assignments: dict[str, str], pos: list[int]) -> dict:
    return {
        "parameters": {
            "assignments": {
                "assignments": [
                    {"id": _id(), "name": k, "value": v, "type": "string"}
                    for k, v in assignments.items()
                ]
            },
            "options": {},
        },
        "id": _id(),
        "name": name,
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": pos,
    }


def if_node(name: str, condition_left: str, condition_value: str, pos: list[int]) -> dict:
    return {
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [
                    {
                        "id": _id(),
                        "leftValue": condition_left,
                        "rightValue": condition_value,
                        "operator": {"type": "string", "operation": "equals"},
                    }
                ],
                "combinator": "and",
            },
            "options": {},
        },
        "id": _id(),
        "name": name,
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": pos,
    }


def wait_node(name: str, amount: int, unit: str, pos: list[int]) -> dict:
    """unit: seconds | minutes | hours | days"""
    return {
        "parameters": {
            "resume": "timeInterval",
            "amount": amount,
            "unit": unit,
            "options": {},
        },
        "id": _id(),
        "name": name,
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": pos,
    }


def respond_to_webhook_node(name: str, pos: list[int]) -> dict:
    return {
        "parameters": {
            "respondWith": "json",
            "responseBody": '={"success": true, "message": "Lead captured"}',
            "options": {},
        },
        "id": _id(),
        "name": name,
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1.1,
        "position": pos,
    }


def send_email_node(
    name: str,
    to_email: str,
    subject: str,
    html_body: str,
    pos: list[int],
) -> dict:
    return {
        "parameters": {
            "fromEmail": "={{$vars.FROM_EMAIL}}",
            "toEmail": to_email,
            "subject": subject,
            "emailType": "html",
            "message": html_body,
            "options": {},
        },
        "id": _id(),
        "name": name,
        "type": "n8n-nodes-base.emailSend",
        "typeVersion": 2.1,
        "position": pos,
    }


def note_node(content: str, pos: list[int]) -> dict:
    return {
        "parameters": {"content": content, "height": 80, "width": 220},
        "id": _id(),
        "name": f"Note_{_id()[:6]}",
        "type": "n8n-nodes-base.stickyNote",
        "typeVersion": 1,
        "position": pos,
    }


# ── Connection helpers ────────────────────────────────────────────────────────

def connect(source: str, target: str, source_output: int = 0, target_input: int = 0) -> tuple:
    """Returns (source_name, connection_dict) for building connections map."""
    return source, {
        "node": target,
        "type": "main",
        "index": target_input,
    }, source_output


def build_connections(edges: list[tuple]) -> dict:
    """
    edges: list of (source_name, target_name) or
           (source_name, target_name, output_index).
    """
    conns: dict[str, Any] = {}
    for edge in edges:
        src = edge[0]
        tgt = edge[1]
        out_idx = edge[2] if len(edge) > 2 else 0
        if src not in conns:
            conns[src] = {"main": [[]]}
        while len(conns[src]["main"]) <= out_idx:
            conns[src]["main"].append([])
        conns[src]["main"][out_idx].append({"node": tgt, "type": "main", "index": 0})
    return conns


# ── Full workflow builder ────────────────────────────────────────────────────

def build_workflow(
    name: str,
    nodes: list[dict],
    edges: list[tuple],
    tags: list[str] | None = None,
) -> dict:
    return {
        "name": name,
        "nodes": nodes,
        "connections": build_connections(edges),
        "active": False,
        "settings": {
            "executionOrder": "v1",
            "saveManualExecutions": True,
            "callerPolicy": "workflowsFromSameOwner",
            "errorWorkflow": "",
        },
        "versionId": _id(),
        "id": _id(),
        "meta": {"instanceId": _id()},
        "tags": [{"name": t, "id": _id()} for t in (tags or [])],
    }


def workflow_to_json(workflow: dict, indent: int = 2) -> str:
    return json.dumps(workflow, indent=indent)


# ── Pre-built workflow templates ─────────────────────────────────────────────

def lead_capture_workflow(ghl_api_key: str, ghl_location_id: str) -> dict:
    """Webhook → validate → create GHL contact → respond."""
    ghl_url = "https://services.leadconnectorhq.com/contacts/"

    nodes = [
        webhook_node("Lead Form Webhook", "lead-capture", _pos(240, 300)),
        note_node("Receives form submissions from landing page", _pos(240, 180)),
        set_node(
            "Extract Lead Data",
            {
                "firstName": "={{$json.body.firstName}}",
                "lastName": "={{$json.body.lastName}}",
                "email": "={{$json.body.email}}",
                "phone": "={{$json.body.phone}}",
                "source": "={{$json.body.source || 'Landing Page'}}",
                "leadMagnet": "={{$json.body.leadMagnet || ''}}",
            },
            _pos(460, 300),
        ),
        http_request_node(
            "Create GHL Contact",
            ghl_url,
            "POST",
            body={
                "firstName": "={{$json.firstName}}",
                "lastName": "={{$json.lastName}}",
                "email": "={{$json.email}}",
                "phone": "={{$json.phone}}",
                "locationId": ghl_location_id,
                "source": "={{$json.source}}",
                "tags": ["new-lead", "{{$json.leadMagnet}}"],
            },
            headers={"Authorization": f"Bearer {ghl_api_key}", "Version": "2021-07-28"},
            pos=_pos(680, 300),
        ),
        respond_to_webhook_node("Confirm Receipt", _pos(900, 300)),
    ]

    edges = [
        ("Lead Form Webhook", "Extract Lead Data"),
        ("Extract Lead Data", "Create GHL Contact"),
        ("Create GHL Contact", "Confirm Receipt"),
    ]

    return build_workflow(
        "Lead Capture → GHL",
        nodes,
        edges,
        tags=["lead-gen", "marketing-agency"],
    )


def email_nurture_workflow(
    email_sequence: list[dict],
    ghl_api_key: str,
    ghl_location_id: str,
) -> dict:
    """GHL webhook trigger → send email sequence with delays.

    email_sequence: list of {subject, html_body, delay_days}
    """
    nodes: list[dict] = []
    edges: list[tuple] = []

    # Trigger
    trigger = webhook_node(
        "Nurture Sequence Trigger",
        "nurture-start",
        _pos(240, 300),
    )
    nodes.append(trigger)

    prev_name = "Nurture Sequence Trigger"
    x = 460

    for i, email in enumerate(email_sequence):
        delay_days = email.get("delay_days", 1)

        # Wait node (skip for first email)
        if i > 0:
            wait_name = f"Wait {delay_days}d (Email {i + 1})"
            nodes.append(wait_node(wait_name, delay_days, "days", _pos(x, 300)))
            edges.append((prev_name, wait_name))
            prev_name = wait_name
            x += 220

        # Tag contact in GHL
        tag_name = f"Tag: nurture-email-{i + 1}"
        nodes.append(
            http_request_node(
                tag_name,
                f"https://services.leadconnectorhq.com/contacts/{{{{$json.contactId}}}}/tags",
                "POST",
                body={"tags": [f"nurture-email-{i + 1}"]},
                headers={"Authorization": f"Bearer {ghl_api_key}", "Version": "2021-07-28"},
                pos=_pos(x, 300),
            )
        )
        edges.append((prev_name, tag_name))
        prev_name = tag_name
        x += 220

        # Send email
        email_node_name = f"Email {i + 1}: {email['subject'][:30]}"
        nodes.append(
            send_email_node(
                email_node_name,
                "={{$json.email}}",
                email["subject"],
                email["html_body"],
                _pos(x, 300),
            )
        )
        edges.append((prev_name, email_node_name))
        prev_name = email_node_name
        x += 220

    return build_workflow(
        "Email Nurture Sequence",
        nodes,
        edges,
        tags=["nurture", "email", "marketing-agency"],
    )


def retargeting_workflow(ghl_api_key: str, ghl_location_id: str) -> dict:
    """Tag non-converters for retargeting after 7 days of inactivity."""
    nodes = [
        webhook_node("Inactivity Trigger", "retarget-check", _pos(240, 300)),
        note_node(
            "Fires 7 days after lead capture if no conversion tag exists",
            _pos(240, 180),
        ),
        http_request_node(
            "Get Contact Details",
            "https://services.leadconnectorhq.com/contacts/={{$json.contactId}}",
            "GET",
            body=None,
            headers={"Authorization": f"Bearer {ghl_api_key}", "Version": "2021-07-28"},
            pos=_pos(460, 300),
        ),
        if_node(
            "Has Converted?",
            "={{$json.tags.includes('converted')}}",
            "true",
            _pos(680, 300),
        ),
        http_request_node(
            "Tag for Retargeting",
            "https://services.leadconnectorhq.com/contacts/={{$json.id}}/tags",
            "POST",
            body={"tags": ["retarget-ad-audience", "no-convert-7d"]},
            headers={"Authorization": f"Bearer {ghl_api_key}", "Version": "2021-07-28"},
            pos=_pos(900, 420),
        ),
        set_node("Skip — Already Converted", {"status": "converted"}, _pos(900, 180)),
    ]

    edges = [
        ("Inactivity Trigger", "Get Contact Details"),
        ("Get Contact Details", "Has Converted?"),
        ("Has Converted?", "Skip — Already Converted", 0),    # TRUE branch
        ("Has Converted?", "Tag for Retargeting", 1),          # FALSE branch
    ]

    return build_workflow(
        "Retargeting Audience Builder",
        nodes,
        edges,
        tags=["retargeting", "audience", "marketing-agency"],
    )
