"""
Builds the messages sent to the model.
MEMORY HOOK 1: recent tasks injected into the system prompt.
MEMORY HOOK 2: full Monday briefing injected as a message on Monday mornings.
"""

from datetime import datetime
from memory import recall, get_monday_tasks

SYSTEM_BASE = """You are Monday Launcher, a personal assistant that helps people end their workweek cleanly and start Monday with momentum.

Your two modes:
- FRIDAY MODE (end of day): Help the user log unfinished tasks, calls to make, appointments, and reminders. Ask for phone numbers, addresses, and talking points so Monday-you has everything ready.
- MONDAY MODE (morning): Present the full briefing of saved tasks. Offer call scripts, addresses, and step-by-step help for each item. Be energizing and organized.

Always be concise and practical. When saving tasks, confirm what you saved. When presenting the Monday briefing, go item by item and offer to help with each one."""


def build_messages(history, user_input):
    """
    Build the message list for the model.
    MEMORY HOOK 1: pull recent tasks into the system prompt so the model always has context.
    MEMORY HOOK 2: on Monday mornings, inject the full briefing as a message.
    """
    # MEMORY HOOK 1 — inject recent saved tasks into the system prompt
    recent = recall(query="", limit=5)
    system_content = SYSTEM_BASE
    if recent and "No tasks" not in recent:
        system_content += f"\n\nRecently saved tasks:\n{recent}"

    system = {"role": "system", "content": system_content}
    user = {"role": "user", "content": user_input}

    messages = [system] + history

    # MEMORY HOOK 2 — on Monday mornings, inject the briefing as a context message
    now = datetime.now()
    is_monday_morning = (now.weekday() == 0 and now.hour < 12)
    if is_monday_morning:
        tasks = get_monday_tasks()
        if tasks:
            briefing_text = f"[MONDAY BRIEFING — {len(tasks)} tasks saved from last week. Present these to the user.]"
            messages.append({"role": "system", "content": briefing_text})

    messages.append(user)
    return messages
