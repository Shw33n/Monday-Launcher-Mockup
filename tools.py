"""
Monday Launcher tools.
Extends the starter repo's tools with everything the agent needs:
- get_time            (from starter)
- search_memory       (MEMORY HOOK 3 — now actually works)
- save_task           (log a Friday task)
- get_monday_briefing (build the Monday morning digest)
- generate_call_script (write a phone script for a task)
- get_address         (look up an address for an appointment)
- mark_done           (remove a completed task)
"""

import json
from datetime import datetime

from memory import recall, save_task, get_monday_tasks, clear_completed


# ── Starter tools ────────────────────────────────────────────────────────────

def get_time():
    """Return the current time."""
    return datetime.now().isoformat(timespec="minutes")


def search_memory(query: str) -> str:
    """MEMORY HOOK 3: let the model search saved tasks and past conversations."""
    return recall(query)


# ── Monday Launcher tools ─────────────────────────────────────────────────────

def save_task_tool(title: str, task_type: str, notes: str = "",
                   phone: str = "", address: str = "", due_day: str = "Monday") -> str:
    """
    Save an unfinished task so it shows up on Monday.
    task_type: 'call', 'email', 'errand', 'appointment', or 'reminder'
    """
    save_task({
        "title": title,
        "type": task_type,
        "notes": notes,
        "phone": phone,
        "address": address,
        "due_day": due_day,
    })
    return f"✅ Saved: '{title}' — I'll remind you {due_day} morning."


def get_monday_briefing() -> str:
    """
    Build the Monday morning digest from everything saved on Friday.
    Returns a formatted briefing the model will present to the user.
    """
    tasks = get_monday_tasks()
    if not tasks:
        return "No tasks saved for Monday. Enjoy your fresh start! 🎉"

    sections = {"call": [], "email": [], "appointment": [], "errand": [], "reminder": []}
    for t in tasks:
        bucket = t.get("type", "reminder")
        sections.setdefault(bucket, []).append(t)

    lines = ["🗓️  MONDAY LAUNCHER — Your Morning Briefing\n"]

    if sections["appointment"]:
        lines.append("📅 APPOINTMENTS")
        for t in sections["appointment"]:
            lines.append(f"  • {t['title']}")
            if t.get("address"):
                lines.append(f"    📍 Address: {t['address']}")
            if t.get("phone"):
                lines.append(f"    📞 Phone: {t['phone']}")
            if t.get("notes"):
                lines.append(f"    📝 {t['notes']}")

    if sections["call"]:
        lines.append("\n📞 CALLS TO MAKE")
        for t in sections["call"]:
            lines.append(f"  • {t['title']}")
            if t.get("phone"):
                lines.append(f"    📞 {t['phone']}")
            if t.get("notes"):
                lines.append(f"    📝 {t['notes']}")

    if sections["email"]:
        lines.append("\n📧 EMAILS TO SEND")
        for t in sections["email"]:
            lines.append(f"  • {t['title']}")
            if t.get("notes"):
                lines.append(f"    📝 {t['notes']}")

    if sections["errand"]:
        lines.append("\n🏃 ERRANDS")
        for t in sections["errand"]:
            lines.append(f"  • {t['title']}")
            if t.get("notes"):
                lines.append(f"    📝 {t['notes']}")

    if sections["reminder"]:
        lines.append("\n🔔 REMINDERS")
        for t in sections["reminder"]:
            lines.append(f"  • {t['title']}")
            if t.get("notes"):
                lines.append(f"    📝 {t['notes']}")

    lines.append(f"\n{len(tasks)} task(s) total. Type 'script for [task name]' to get a call script.")
    return "\n".join(lines)


def generate_call_script(task_title: str, context: str = "") -> str:
    """
    Generate a phone call script for a saved task.
    The model will fill in a natural-sounding script based on task details.
    context: any extra info to make the script more specific
    """
    tasks = get_monday_tasks()
    task = next((t for t in tasks if task_title.lower() in t.get("title", "").lower()), None)

    if not task:
        return f"No task found matching '{task_title}'. Try 'get monday briefing' to see your tasks."

    script = f"""📞 CALL SCRIPT: {task['title']}
────────────────────────────────
Phone number: {task.get('phone', 'Look this up before calling')}

When they answer:
"Hi, my name is [YOUR NAME]. I'm calling to {task.get('notes', task['title'].lower())}."

If they ask for more details:
{context if context else task.get('notes', 'Explain your situation clearly and ask for next steps.')}

If they put you on hold: That's normal, stay on the line.

Before you hang up, confirm:
- Any reference or confirmation number
- Next steps or follow-up date
- Name of person you spoke with
────────────────────────────────"""
    return script


def get_address(location_name: str) -> str:
    """
    Return the address for a saved task by name.
    If not saved, prompt the user to add it.
    """
    tasks = get_monday_tasks()
    task = next((t for t in tasks if location_name.lower() in t.get("title", "").lower()), None)

    if not task:
        return f"No saved address for '{location_name}'. Add it with save_task."

    address = task.get("address", "")
    if not address:
        return f"Task '{task['title']}' has no address saved. Edit the task to add one."

    return f"📍 {task['title']}: {address}\n(Tap to open in Google Maps or paste into Uber)"


def mark_done(task_title: str) -> str:
    """Mark a task as done and remove it from Monday's list."""
    clear_completed(task_title)
    return f"✅ '{task_title}' marked as done and removed from your list."


# ── Tool registry ─────────────────────────────────────────────────────────────

TOOLS = {
    "get_time": get_time,
    "search_memory": search_memory,
    "save_task": save_task_tool,
    "get_monday_briefing": get_monday_briefing,
    "generate_call_script": generate_call_script,
    "get_address": get_address,
    "mark_done": mark_done,
}

SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_time",
        "description": "Get the current date and time.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "search_memory",
        "description": "Search saved tasks and past conversations by keyword.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "Keyword to search for"}
        }, "required": ["query"]},
    }},
    {"type": "function", "function": {
        "name": "save_task",
        "description": "Save an unfinished task to show up on Monday morning.",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string", "description": "Short name for the task"},
            "task_type": {"type": "string", "enum": ["call", "email", "errand", "appointment", "reminder"]},
            "notes": {"type": "string", "description": "Details, talking points, or reminders"},
            "phone": {"type": "string", "description": "Phone number if this is a call"},
            "address": {"type": "string", "description": "Address if this needs travel"},
            "due_day": {"type": "string", "description": "Day it's due, default Monday"},
        }, "required": ["title", "task_type"]},
    }},
    {"type": "function", "function": {
        "name": "get_monday_briefing",
        "description": "Get the full Monday morning digest of all saved tasks.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "generate_call_script",
        "description": "Generate a phone call script for a saved task.",
        "parameters": {"type": "object", "properties": {
            "task_title": {"type": "string"},
            "context": {"type": "string", "description": "Extra context to personalize the script"},
        }, "required": ["task_title"]},
    }},
    {"type": "function", "function": {
        "name": "get_address",
        "description": "Get the saved address for an appointment or errand.",
        "parameters": {"type": "object", "properties": {
            "location_name": {"type": "string"}
        }, "required": ["location_name"]},
    }},
    {"type": "function", "function": {
        "name": "mark_done",
        "description": "Mark a task as completed and remove it from Monday's list.",
        "parameters": {"type": "object", "properties": {
            "task_title": {"type": "string"}
        }, "required": ["task_title"]},
    }},
]


def run_tool_call(call):
    """Run one tool call from the model and return the result message."""
    args = json.loads(call.function.arguments or "{}")
    result = TOOLS[call.function.name](**args)
    return {"role": "tool", "tool_call_id": call.id, "content": str(result)}
