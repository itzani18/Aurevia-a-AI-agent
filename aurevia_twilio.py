import json
import os
import time
import threading
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_FROM")  # e.g. whatsapp:+14155238886
TEMPLATE_SID = os.getenv("TWILIO_TEMPLATE_SID")

client = Client(TWILIO_SID, TWILIO_AUTH)


def send_day_message(day_number, to_number, name, goal, tasks, motivation):
    matched = [t for t in tasks if t.lower().startswith(f"day {day_number}:")]
    if not matched:
        print(f"❌ Day {day_number} not found.")
        return

    lines = matched[0].strip().split("\n")
    title = lines[0].strip()
    task_list = "\n".join([f"- {line.strip()}" for line in lines[1:] if line.strip()])
    motivation = motivation[:300] + "..." if len(motivation) > 300 else motivation

    variables = {
        "1": name,
        "2": f"{goal} ({title})",
        "3": task_list,
        "4": motivation
    }

    message = client.messages.create(
        from_=FROM_NUMBER,
        content_sid=TEMPLATE_SID,
        content_variables=json.dumps(variables),
        to=f"whatsapp:{to_number}"
    )
    print(f"✅ Day {day_number} sent! SID: {message.sid}")


def start_auto_schedule(to_number, name, goal, tasks, motivation):
    total_days = sum(1 for t in tasks if t.lower().startswith("day "))
    print(f"🟢 Starting auto-schedule for {total_days} days...")

    def scheduler():
        for day in range(2, total_days + 1):  # Day 2 to N
            print(f"⏳ Waiting to send Day {day}...")
            time.sleep(300)  # 5 minutes
            print(f"📤 Sending Day {day} to {to_number}")
            send_day_message(day, to_number, name, goal, tasks, motivation)

    thread = threading.Thread(target=scheduler, daemon=True)
    thread.start()
