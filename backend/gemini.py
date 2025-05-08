import google.generativeai as genai
import os
import streamlit as st

# Get API key from Streamlit secrets or environment variable
API_KEY = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

# Text model (fast)
text_model = genai.GenerativeModel("gemini-1.5-flash")
# Vision model (for image analysis)
vision_model = genai.GenerativeModel("gemini-1.5-pro-latest")

def generate_text(prompt):
    response = text_model.generate_content(prompt)
    return response.text

def generate_vision(prompt, image):
    response = vision_model.generate_content([prompt, image])
    return response.text

menu = [
    "User Profile",
    "Meal Plan Generator",
    "Food Analysis",
    "Tracking & Analytics",
    "Recommendations",
    "AI Chat Coach",
    "Food Image Analysis"
]
choice = st.sidebar.selectbox("Navigation", menu) 