import firebase_admin
from firebase_admin import credentials, firestore

# Prevent initializing multiple times
if not firebase_admin._apps:
    cred = credentials.Certificate("avid-stratum-458105-m6-firebase-adminsdk-fbsvc-58dece7abc.json")  # Replace with your correct path
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_plan_to_cloud(date, goal, tasks, status, motivation):
    doc_ref = db.collection("plans").document(date)
    doc_ref.set({
        "goal": goal,
        "tasks": tasks,
        "status": status,
        "motivation": motivation
    })

def get_plan_for_today():
    import datetime
    today = str(datetime.date.today())
    doc_ref = db.collection("plans").document(today)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None
