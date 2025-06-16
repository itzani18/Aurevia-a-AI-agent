import streamlit as st
import pyrebase
import datetime
from planner import generate_tasks
from motivator import generate_motivation
from aurevia_twilio import send_day_message, start_auto_schedule
from tts_voice import speak_plan, stop_audio
import os
import socket
from fpdf import FPDF

# For local audio (tts_voice.py must exist for local use)
try:
    from tts_voice import speak_plan, stop_audio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# ---- REPLACE WITH YOUR FIREBASE CONFIG ----
firebaseConfig = {
    "apiKey": "AIzaSyBrFmQlsFzNh8AZPKshQIduOHPo8Y4j5Tw",
    "authDomain": "avid-stratum-458105-m6.firebaseapp.com",
    "projectId": "avid-stratum-458105-m6",
    "storageBucket": "avid-stratum-458105-m6.firebasestorage.app",
    "messagingSenderId": "1042983559929",
    "appId": "1:1042983559929:web:5b29da6395897639617828",
    "measurementId": "G-YVWD74Y49S",
    "databaseURL": "https://avid-stratum-458105-m6-default-rtdb.asia-southeast1.firebasedatabase.app/"
}
# -------------------------------------------

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

st.title("Aurevia AI Planner Login / Signup")

if "page" not in st.session_state:
    st.session_state.page = "login"

def switch_page(page):
    st.session_state.page = page
    st.rerun()

def get_user_info(uid):
    return db.child("users").child(uid).get().val()

def get_chats(uid):
    chats = db.child("users").child(uid).child("chats").get().val()
    if chats:
        return list(chats.keys())
    else:
        return []

def is_cloud():
    # Streamlit Cloud sets this env variable
    return os.environ.get("STREAMLIT_SERVER_ENABLED") == "1" or "STREAMPOD_ENV" in os.environ
def clean_for_pdf(text):
    # Remove tabs, replace with space
    text = text.replace('\t', ' ')
    # Remove all non-ASCII
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Remove weird newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text
def sanitize_text_for_pdf(text):
    # Remove leading/trailing whitespace and empty lines
    lines = text.split('\n')
    safe_lines = []
    for line in lines:
        # remove leading/trailing spaces, ignore if empty after
        clean = line.strip()
        if clean:
            safe_lines.append(clean)
    # Also, for each "word" that is longer than 40 chars, add spaces to force wrap
    result = []
    for line in safe_lines:
        words = line.split(' ')
        new_words = []
        for word in words:
            if len(word) > 40:
                # break it into 40-char pieces
                new_words.extend([word[i:i+40] for i in range(0, len(word), 40)])
            else:
                new_words.append(word)
        result.append(' '.join(new_words))
    return '\n'.join(result)

def create_pdf(title, tasks, motivation, filename):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, clean_for_pdf(title), ln=1)
    pdf.ln(5)
    pdf.set_font("Helvetica", size=12)
    for task in tasks:
        print("\n---RAW TASK---\n", repr(task))
        clean_task = clean_for_pdf(task)
        print("---CLEAN TASK---\n", repr(clean_task))
        safe_task = sanitize_text_for_pdf(clean_task)
        print("---SAFE TASK---\n", repr(safe_task))
        pdf.multi_cell(0, 10, safe_task, align='L')# <--- THIS IS KEY!
    pdf.ln(5)
    safe_motivation = sanitize_text_for_pdf(clean_for_pdf(motivation))
    pdf.multi_cell(0, 10, "Motivation:\n" + safe_motivation, align='L')
    pdf.output(filename)

# ----------- LOGIN PAGE -------------
if st.session_state.page == "login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state['user'] = user
            st.success("Login successful!")
            switch_page("chat")
        except Exception as e:
            error_str = str(e)
            if "EMAIL_NOT_FOUND" in error_str or "INVALID_PASSWORD" in error_str:
                st.error("Invalid email or password.")
            else:
                st.error(f"Login failed: {e}")
    if st.button("Go to Signup"):
        switch_page("signup")

# ---------- SIGNUP PAGE -------------
elif st.session_state.page == "signup":
    st.subheader("Sign Up")
    name = st.text_input("Name")
    phone = st.text_input("WhatsApp Number (with +91)", max_chars=13)
    email = st.text_input("Email (Signup)")
    password = st.text_input("Password (Signup)", type="password")
    if st.button("Create Account"):
        try:
            user = auth.create_user_with_email_and_password(email, password)
            uid = user['localId']
            db.child("users").child(uid).set({
                "name": name,
                "phone": phone,
                "email": email
            })
            st.success("Signup successful! Please login.")
            switch_page("login")
        except Exception as e:
            error_str = str(e)
            if "EMAIL_EXISTS" in error_str:
                st.error("This email is already registered. Please log in.")
            else:
                st.error(f"Signup failed: {e}")
    if st.button("Go to Login"):
        switch_page("login")

# ---------- CHAT/PLANNER PAGE -------------
elif st.session_state.page == "chat":
    user = st.session_state.get('user')
    if not user:
        st.warning("Session expired. Please login again.")
        switch_page("login")
    uid = user['localId']
    user_info = get_user_info(uid)
    st.success(f"Welcome, {user_info['name']} ({user_info['phone']})")

    if "goto_new_chat" not in st.session_state:
        st.session_state.goto_new_chat = None
    if st.session_state.goto_new_chat is not None:
        st.session_state.selected_chat = st.session_state.goto_new_chat
        st.session_state.goto_new_chat = None
    if "selected_chat" not in st.session_state:
        st.session_state.selected_chat = "Create New Chat"

    chat_names = get_chats(uid)
    selected_chat = st.sidebar.selectbox(
        "Your Chats", ["Create New Chat"] + chat_names, key="selected_chat"
    )

    if selected_chat == "Create New Chat":
        st.subheader("Create a New Plan (Chat)")
        chat_name = st.text_input("Enter Chat Name")
        goal = st.text_input("What's your goal for this plan?")
        if st.button("Generate Plan"):
            tasks = generate_tasks(goal)
            motivation = generate_motivation(goal)
            status = [False] * len(tasks)
            plan_data = {
                "goal": goal,
                "tasks": tasks,
                "status": status,
                "motivation": motivation,
                "created_at": str(datetime.datetime.now())
            }
            db.child("users").child(uid).child("chats").child(chat_name).set(plan_data)
            st.session_state.goto_new_chat = chat_name
            st.success("Plan saved! Loading your plan...")
            st.rerun()
    else:
        # Show selected chat
        chat_data = db.child("users").child(uid).child("chats").child(selected_chat).get().val()
        if chat_data:
            st.header(f"Chat: {selected_chat}")
            st.markdown(f"**Goal:** {chat_data['goal']}")
            st.markdown("---")
            st.subheader("Full Plan")
            for task in chat_data['tasks']:
                lines = task.strip().split("\n")
                if lines:
                    st.markdown(f"### {lines[0]}")
                    for subline in lines[1:]:
                        if subline.strip():
                            st.markdown(subline.strip())
                else:
                    st.markdown(task)
            st.markdown("---")
            st.subheader("Motivation")
            st.info(chat_data["motivation"])

            # --- Cloud/Local Features ---

            def get_daywise_chunks(tasks, motivation):
                chunks = []
                for task in tasks:
                    if task.strip():
                        chunks.append(task.strip())
                if motivation:
                    chunks.append("Motivation: " + motivation)
                return chunks

            # --- PDF/Checklist Download (Both Cloud & Local) ---
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬇️ Download To-Do List (.txt)"):
                    todo_lines = []
                    for i, task in enumerate(chat_data['tasks']):
                        lines = task.strip().split('\n')
                        for line in lines:
                            if line.strip():
                                todo_lines.append(f"- [ ] {line.strip()}")
                    todo_lines.append(f"\nMotivation: {chat_data['motivation']}")
                    todo_txt = "\n".join(todo_lines)
                    st.download_button("Download To-Do List", todo_txt, file_name=f"{selected_chat}_plan.txt")
            with col2:
                if st.button("⬇️ Download Plan as PDF"):
                    plan_title = selected_chat
                    pdf_filename = f"{selected_chat}_plan.pdf"
                    create_pdf(plan_title, chat_data['tasks'], chat_data['motivation'], pdf_filename)
                    with open(pdf_filename, "rb") as f:
                        st.download_button("Download PDF", f, file_name=pdf_filename, mime="application/pdf")
                    try:
                        os.remove(pdf_filename)
                    except Exception:
                        pass

            # --- Audio playback (local only) ---
            if not is_cloud() and AUDIO_AVAILABLE:
                full_plan_text = ""
                for task in chat_data['tasks']:
                    full_plan_text += task + "\n\n"
                full_plan_text += "\nMotivation: " + chat_data['motivation']
                col3, col4 = st.columns(2)
                with col3:
                    if st.button("🔊 Read Out Plan (Local)"):
                        speak_plan(full_plan_text)
                with col4:
                    if st.button("⏹️ Stop Voice"):
                        stop_audio()
                        st.success("Voice stopped.")

            # --- WhatsApp Integration ---
            if st.button("Send to WhatsApp"):
                user_phone = user_info['phone']
                user_name = user_info['name']
                goal = chat_data['goal']
                tasks = chat_data['tasks']
                motivation = chat_data['motivation']
                send_day_message(
                    day_number=1, 
                    to_number=user_phone, 
                    name=user_name, 
                    goal=goal, 
                    tasks=tasks, 
                    motivation=motivation
                )
                st.success(f"Day 1 sent to WhatsApp: {user_phone}")

                if st.checkbox("Also schedule all future days (every 5 minutes)?"):
                    start_auto_schedule(
                        to_number=user_phone,
                        name=user_name,
                        goal=goal,
                        tasks=tasks,
                        motivation=motivation
                    )
                    st.info("Auto-scheduling started! Future days will be sent every 5 min.")

            # --- Delete Chat Button ---
            if st.button("Delete Chat", type="primary"):
                db.child("users").child(uid).child("chats").child(selected_chat).remove()
                st.success(f"Chat '{selected_chat}' deleted.")
                st.session_state.goto_new_chat = "Create New Chat"
                st.rerun()

    # --- Logout ---
    if st.button("Logout"):
        for k in ["user", "page"]:
            if k in st.session_state:
                del st.session_state[k]
        st.success("Logged out. Please login again.")
        st.rerun()
