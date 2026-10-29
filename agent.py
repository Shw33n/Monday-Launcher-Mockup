# /// script
# dependencies = ["groq"]
# ///
"""
Monday Launcher — main agent loop.
Built on the minimal-agent starter repo.
Helps you end Friday clean and start Monday with momentum.
"""

import os
from datetime import datetime

from groq import Groq

from prompt import build_messages
from tools import SCHEMAS, run_tool_call
from memory import save_exchange  # MEMORY HOOK 4

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")


def respond(history, user_input):
    """Answer one user message, looping while the model asks for tools."""
    messages = build_messages(history, user_input)
    while True:
        reply = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=SCHEMAS
        ).choices[0].message
        messages.append(reply)
        if not reply.tool_calls:
            return reply.content
        for call in reply.tool_calls:
            messages.append(run_tool_call(call))


def greeting():
    """Print a time-aware greeting."""
    now = datetime.now()
    day = now.strftime("%A")
    hour = now.hour

    if day == "Friday" and hour >= 15:
        print("🌅 Friday wrap-up time! Let's make sure Monday-you has everything ready.")
        print("   Tell me what's unfinished — calls, appointments, errands, reminders.")
    elif day == "Monday" and hour < 12:
        print("☀️  Good Monday morning! Let me pull up your briefing from last week...")
        print("   (type 'briefing' to see everything, or just ask about a specific task)")
    else:
        print(f"👋 Monday Launcher ready. Today is {day}.")
        print("   Log tasks for Monday, or type 'briefing' to review what's saved.")
    print("   Type 'quit' or press Enter to exit.\n")


def main():
    """Chat loop."""
    greeting()
    history = []

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSee you Monday! 👋")
            break

        if not user_input or user_input.lower() in ("quit", "exit"):
            print("See you Monday! 👋")
            break

        # Shortcut: "briefing" triggers Monday digest
        if user_input.lower() in ("briefing", "monday briefing", "show briefing"):
            user_input = "Show me my full Monday morning briefing."

        answer = respond(history, user_input)
        print(f"agent> {answer}\n")

        # MEMORY HOOK 4 — save this exchange to long-term memory
        save_exchange(user_input, answer)

        history += [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": answer},
        ]


if __name__ == "__main__":
    main()
