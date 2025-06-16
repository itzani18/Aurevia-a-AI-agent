# motivator.py (Gemini Flash 1.5 version, Streamlit-ready)
import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai

# Use Streamlit secrets if on Cloud, else dotenv for local
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

def generate_motivation(prompt):
    full_prompt = f"Give a short, powerful motivational message based on: {prompt}"
    st.info("Generating motivational message with Gemini Flash 1.5...")
    print("Motivation prompt:", full_prompt)
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
        response = model.generate_content(full_prompt)
        st.success("Motivation generated!")
        print("Gemini motivation:", response.text.strip())
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini API Error (motivation): {e}")
        print("Error from Gemini API:", e)
        return "Stay positive and keep moving forward! You can do it."

# Test locally
if __name__ == "__main__":
    print(generate_motivation("Preparing for an important interview."))
