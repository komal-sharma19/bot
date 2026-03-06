# tool.py
"""
Tools for your Streamlit + Groq chatbot.

Includes:
1) Time tools (IST):
   - get_current_time
   - time_until
2) Simple Calendar tools (local JSON storage):
   - create_calendar_event
   - list_calendar_events
   - delete_calendar_event
   - export_event_as_ics

This is NOT Google Calendar. It's a lightweight local "calendar" that persists in a JSON file.
"""

from __future__ import annotations

import json
import os
import math
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta ,UTC
from typing import Any, Dict, List, Optional

import pytz


# -----------------------------
# Config
# -----------------------------
IST = pytz.timezone("Asia/Kolkata")

# Stores events in a local file (persists across runs)
DEFAULT_STORE_PATH = os.path.join(os.path.dirname(__file__), "calendar_store.json")


# -----------------------------
# Helpers
# -----------------------------
def _now_ist() -> datetime:
    return datetime.now(IST)


def _parse_dt_ist(dt_str: str) -> datetime:
    """
    Parse datetime from common formats into IST-aware datetime.

    Accepts:
    - "2026-03-05 17:00"
    - "2026-03-05 17:00:00"
    - "2026-03-05T17:00"
    - "2026-03-05T17:00:00"
    """
    dt_str = dt_str.strip()

    # Normalize T separator to space
    dt_str = dt_str.replace("T", " ")

    fmts = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in fmts:
        try:
            naive = datetime.strptime(dt_str, fmt)
            return IST.localize(naive)
        except ValueError:
            continue

    raise ValueError(
        "Invalid datetime format. Use 'YYYY-MM-DD HH:MM' (e.g., '2026-03-05 17:00')."
    )


def _load_events(store_path: str = DEFAULT_STORE_PATH) -> List[Dict[str, Any]]:
    if not os.path.exists(store_path):
        return []
    try:
        with open(store_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def _save_events(events: List[Dict[str, Any]], store_path: str = DEFAULT_STORE_PATH) -> None:
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)


def _dt_to_iso(dt: datetime) -> str:
    # ISO with timezone offset
    return dt.isoformat()


def _iso_to_dt(iso_str: str) -> datetime:
    dt = datetime.fromisoformat(iso_str)
    if dt.tzinfo is None:
        dt = IST.localize(dt)
    return dt.astimezone(IST)


def _ics_escape(s: str) -> str:
    # Minimal escaping for ICS
    return (s or "").replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")


# -----------------------------
# Time Tools
# -----------------------------
def get_current_time() -> Dict[str, str]:
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%I:%M %p"),
        "day": now.strftime("%A"),
        "timezone": "Asia/Kolkata",
        "iso": now.isoformat(),
    }


# def time_until(target_datetime: str, timezone: str = "Asia/Kolkata") -> Dict[str, Any]:
#     """
#     Returns time remaining until target_datetime (IST by default).

#     target_datetime format:
#     - "YYYY-MM-DD HH:MM"  e.g. "2026-03-05 17:00"
#     """
#     tz = pytz.timezone(timezone)
#     now = datetime.now(tz)

#     # Parse target in the same tz
#     target = _parse_dt_ist(target_datetime).astimezone(tz)

#     delta = target - now
#     seconds = int(delta.total_seconds())

#     status = "future"
#     if seconds < 0:
#         status = "past"
#         seconds = abs(seconds)

#     days = seconds // 86400
#     hours = (seconds % 86400) // 3600
#     minutes = (seconds % 3600) // 60

#     return {
#         "status": status,               # "future" or "past"
#         "now_iso": now.isoformat(),
#         "target_iso": target.isoformat(),
#         "days": days,
#         "hours": hours,
#         "minutes": minutes,
#         "human": f"{days}d {hours}h {minutes}m",
#         "timezone": timezone,
#     }


# -----------------------------
# Calendar Tools (Local JSON)
# -----------------------------
def create_calendar_event(
    title: str,
    start_datetime: str,
    end_datetime: Optional[str] = None,
    duration_minutes: int = 30,
    location: str = "",
    meeting_link: str = "",
    description: str = "",
    timezone: str = "Asia/Kolkata",
    store_path: str = DEFAULT_STORE_PATH,
) -> Dict[str, Any]:
    """
    Create a calendar event and store it locally.

    start_datetime / end_datetime format:
      "YYYY-MM-DD HH:MM" (e.g., "2026-03-05 17:00")

    If end_datetime not provided, it will use duration_minutes.
    """
    tz = pytz.timezone(timezone)
    start = _parse_dt_ist(start_datetime).astimezone(tz)

    if end_datetime:
        end = _parse_dt_ist(end_datetime).astimezone(tz)
    else:
        end = start + timedelta(minutes=int(duration_minutes))

    event_id = uuid.uuid4().hex

    event = {
        "id": event_id,
        "title": title.strip(),
        "start_iso": _dt_to_iso(start),
        "end_iso": _dt_to_iso(end),
        "timezone": timezone,
        "location": location.strip(),
        "meeting_link": meeting_link.strip(),
        "description": description.strip(),
        "created_iso": _dt_to_iso(datetime.now(tz)),
    }

    events = _load_events(store_path)
    events.append(event)
    _save_events(events, store_path)

    return {"ok": True, "event": event}


def list_calendar_events(
    date: Optional[str] = None,
    from_datetime: Optional[str] = None,
    to_datetime: Optional[str] = None,
    timezone: str = "Asia/Kolkata",
    store_path: str = DEFAULT_STORE_PATH,
) -> Dict[str, Any]:
    """
    List stored events with optional filters.

    date: "YYYY-MM-DD"
    OR
    from_datetime/to_datetime: "YYYY-MM-DD HH:MM"
    """
    tz = pytz.timezone(timezone)
    events = _load_events(store_path)

    def in_range(ev: Dict[str, Any]) -> bool:
        start = _iso_to_dt(ev["start_iso"]).astimezone(tz)
        end = _iso_to_dt(ev["end_iso"]).astimezone(tz)

        if date:
            d = datetime.strptime(date, "%Y-%m-%d").date()
            return start.date() == d

        if from_datetime:
            frm = _parse_dt_ist(from_datetime).astimezone(tz)
            if end < frm:
                return False

        if to_datetime:
            to = _parse_dt_ist(to_datetime).astimezone(tz)
            if start > to:
                return False

        return True

    filtered = [ev for ev in events if in_range(ev)]

    # Sort by start time
    filtered.sort(key=lambda ev: ev["start_iso"])
    return {"ok": True, "count": len(filtered), "events": filtered}


def delete_calendar_event(
    event_id: str,
    store_path: str = DEFAULT_STORE_PATH,
) -> Dict[str, Any]:
    """
    Delete an event by id.
    """
    events = _load_events(store_path)
    new_events = [ev for ev in events if ev.get("id") != event_id]

    if len(new_events) == len(events):
        return {"ok": False, "error": "Event not found", "event_id": event_id}

    _save_events(new_events, store_path)
    return {"ok": True, "deleted_event_id": event_id}


def export_event_as_ics(
    event_id: str,
    store_path: str = DEFAULT_STORE_PATH,
) -> Dict[str, Any]:
    """
    Export a stored event as ICS text (so you can download/save).
    """
    events = _load_events(store_path)
    event = next((ev for ev in events if ev.get("id") == event_id), None)
    if not event:
        return {"ok": False, "error": "Event not found", "event_id": event_id}

    start = _iso_to_dt(event["start_iso"])
    end = _iso_to_dt(event["end_iso"])

    # ICS wants UTC timestamps in YYYYMMDDTHHMMSSZ
    start_utc = start.astimezone(pytz.UTC).strftime("%Y%m%dT%H%M%SZ")
    end_utc = end.astimezone(pytz.UTC).strftime("%Y%m%dT%H%M%SZ")

    uid = event["id"]
    summary = _ics_escape(event.get("title", ""))
    loc = _ics_escape(event.get("location", ""))
    desc = _ics_escape(
        (event.get("description", "") + ("\n" + event.get("meeting_link", "") if event.get("meeting_link") else "")).strip()
    )

    ics = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "PRODID:-//SkillSonics//LocalCalendar//EN\n"
        "BEGIN:VEVENT\n"
        f"UID:{uid}\n"
        f"DTSTAMP:{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}\n"
        f"DTSTART:{start_utc}\n"
        f"DTEND:{end_utc}\n"
        f"SUMMARY:{summary}\n"
        f"LOCATION:{loc}\n"
        f"DESCRIPTION:{desc}\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    )

    return {"ok": True, "event_id": event_id, "ics": ics}

# -----------------------------
# Calculator Tool
# -----------------------------

def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate a basic math expression.
    Supported:
    - +, -, *, /, %, **
    - parentheses
    - math functions: sqrt, sin, cos, tan, log, log10
    - constants: pi, e
    """

    allowed_names = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "round": round,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return {
            "ok": True,
            "expression": expression,
            "result": result,
        }
    except Exception as e:
        return {
            "ok": False,
            "expression": expression,
            "error": str(e),
        }


# -----------------------------
# Tool Schemas for Groq (OpenAI-compatible tools)
# -----------------------------
def get_tool_schemas() -> List[Dict[str, Any]]:
    """
    Return tool schema definitions to pass to:
      client.chat.completions.create(..., tools=get_tool_schemas(), tool_choice="auto")
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current date and time in Asia/Kolkata timezone only.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        # {
        #     "type": "function",
        #     "function": {
        #         "name": "time_until",
        #         "description": "Get time remaining until a target datetime (default IST).",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "target_datetime": {
        #                     "type": "string",
        #                     "description": "Target time in format 'YYYY-MM-DD HH:MM' (e.g. '2026-03-05 17:00').",
        #                 },
        #                 "timezone": {
        #                     "type": "string",
        #                     "description": "IANA timezone string (default Asia/Kolkata).",
        #                 },
        #             },
        #             "required": ["target_datetime"],
        #         },
        #     },
        # },
        {
            "type": "function",
            "function": {
                "name": "create_calendar_event",
                "description": "Create a local calendar event (stored in a JSON file).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "start_datetime": {
                            "type": "string",
                            "description": "Start in 'YYYY-MM-DD HH:MM' (IST unless timezone provided).",
                        },
                        "end_datetime": {
                            "type": "string",
                            "description": "Optional end in 'YYYY-MM-DD HH:MM'. If omitted, duration_minutes is used.",
                        },
                        "duration_minutes": {"type": "integer", "description": "Used if end_datetime omitted. Default 30."},
                        "location": {"type": "string"},
                        "meeting_link": {"type": "string"},
                        "description": {"type": "string"},
                        "timezone": {"type": "string", "description": "Default Asia/Kolkata."},
                    },
                    "required": ["title", "start_datetime"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_calendar_events",
                "description": "List local calendar events (filter by date or datetime range).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "Optional 'YYYY-MM-DD'"},
                        "from_datetime": {"type": "string", "description": "Optional 'YYYY-MM-DD HH:MM'"},
                        "to_datetime": {"type": "string", "description": "Optional 'YYYY-MM-DD HH:MM'"},
                        "timezone": {"type": "string", "description": "Default Asia/Kolkata."},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_calendar_event",
                "description": "Delete a local calendar event by id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string", "description": "Event id"},
                    },
                    "required": ["event_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "export_event_as_ics",
                "description": "Export a local calendar event as ICS text (for download/import).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string", "description": "Event id"},
                    },
                    "required": ["event_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Evaluate a mathematical expression like 2+2, 25*4, sqrt(16), or log10(100).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Math expression to evaluate."
                        }
                    },
                    "required": ["expression"],
                },
            },
        },
    ]


def dispatch_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
    """
    Execute a tool call by name with arguments dict.
    Use this when handling tool_calls returned by the model.
    """
    if not isinstance(arguments, dict):
        arguments = {}
    
    if name == "get_current_time":
        return get_current_time(**arguments)
    # if name == "time_until":
    #     return time_until(**arguments)
    if name == "calculate":
        return calculate(**arguments)
    if name == "create_calendar_event":
        return create_calendar_event(**arguments)
    if name == "list_calendar_events":
        return list_calendar_events(**arguments)
    if name == "delete_calendar_event":
        return delete_calendar_event(**arguments)
    if name == "export_event_as_ics":
        return export_event_as_ics(**arguments)

    raise ValueError(f"Unknown tool: {name}")