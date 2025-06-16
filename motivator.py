# motivator.py (Gemini Flash version)
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_motivation(prompt):
    full_prompt = f"Give a short, powerful motivational message based on: {prompt}"
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print("Error from Gemini API:", e)
        return "Stay positive and keep moving forward! You can do it."
