import os
import re
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from env or Streamlit secrets
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

def extract_number_of_days(text):
    text = text.lower()
    days = 7  # Default

    # Check for days, weeks, months, years
    day_match = re.search(r'(\d+)\s*day', text)
    week_match = re.search(r'(\d+)\s*week', text)
    month_match = re.search(r'(\d+)\s*month', text)
    year_match = re.search(r'(\d+)\s*year', text)

    if year_match:
        days = int(year_match.group(1)) * 365
    elif month_match:
        days = int(month_match.group(1)) * 30
    elif week_match:
        days = int(week_match.group(1)) * 7
    elif day_match:
        days = int(day_match.group(1))
    else:
        # fallback: look for number only (eg: "in 10")
        num_match = re.search(r'(\d+)', text)
        if num_match:
            days = int(num_match.group(1))
    
    return min(days, 90)  # Hard limit: 90 days for quality

def generate_tasks(goal):
    days = extract_number_of_days(goal)
    prompt = (
        f"You are an expert productivity planner."
        f" Create a detailed, non-repetitive, and unique {days}-day plan for this goal:\n"
        f"Goal: {goal}\n\n"
        f"Format STRICTLY as follows (no HTML, no markdown, no extra symbols, no asterisks):\n"
        f"Day 1:\n"
        f"- 🌅 Morning: ...\n"
        f"- ☀️ Afternoon: ...\n"
        f"- 🌆 Evening: ...\n"
        f"- 🌙 Night: ...\n\n"
        f"Day 2:\n"
        f"- 🌅 Morning: ...\n"
        f"- ☀️ Afternoon: ...\n"
        f"- 🌆 Evening: ...\n"
        f"- 🌙 Night: ...\n\n"
        f"(Continue this pattern for all days. Each 'Day n:' block must be separated by a blank line.)"
    )

    st.info(f"Generating a {days}-day plan with Gemini Flash 1.5 for: {goal}")
    print("Gemini prompt:", prompt)
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        content = response.text.strip()
        print("Gemini response received.")
        # Split on double newlines to get day blocks
        blocks = re.split(r'\n\s*\n', content)
        blocks = [b.strip() for b in blocks if b.strip()]
        st.success(f"Plan generated! ({len(blocks)} days)")
        return blocks[:days]
    except Exception as e:
        st.error(f"Error generating tasks: {e}")
        print("Error generating tasks:", e)
        return [f"Day {i+1}:\n- Placeholder task" for i in range(min(days, 7))]

# Test locally
if __name__ == "__main__":
    test_goal = "I want to crack a data analyst job in 1 month"
    tasks = generate_tasks(test_goal)
    for t in tasks:
        print(t)
