import datetime
import pywhatkit as kit
import time
from firebase_store import get_plan_for_today, save_plan_to_cloud

# Replace with your number
WHATSAPP_NUMBER = "+916263496623"

def send_whatsapp_message(message, number: str = "+919340907174"):
    import pywhatkit
    import datetime
    import time

    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute + 2 if now.minute < 58 else (now.minute + 2) % 60

    print(f"📤 Sending message to WhatsApp number {number} at {hour}:{minute:02d}...")
    pywhatkit.sendwhatmsg(number, message, hour, minute, wait_time=15, tab_close=True)
    time.sleep(5)


def simulate_whatsapp_reply():
    plan = get_plan_for_today()
    if not plan:
        return "❌ No plan found to simulate."

    print("\n📲 WhatsApp Reply Simulation\n---------------------------")
    print("Goal:", plan['goal'])
    print("Motivation:", plan['motivation'])
    print("Tasks:")
    for i, t in enumerate(plan['tasks']):
        status = "✅" if plan['status'][i] else "⬜"
        print(f"{status} {t}")

    while True:
        action = input("\n🟢 Simulate WhatsApp Reply (done / reschedule / progress / exit): ").strip().lower()
        if action == "done":
            plan['status'] = [True] * len(plan['tasks'])
            save_plan_to_cloud(str(datetime.date.today()), plan['goal'], plan['tasks'], plan['status'], plan['motivation'])
            print("✅ All tasks marked as done!")
        elif action == "progress":
            done = sum(plan['status'])
            print(f"📈 Progress: {done}/{len(plan['tasks'])} tasks completed")
        elif action == "reschedule":
            tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
            save_plan_to_cloud(tomorrow, plan['goal'], plan['tasks'], [False]*len(plan['tasks']), plan['motivation'])
            print("📅 Plan moved to tomorrow.")
        elif action == "exit":
            print("👋 Exiting WhatsApp simulation.")
            break
        else:
            print("❌ Invalid input.")
