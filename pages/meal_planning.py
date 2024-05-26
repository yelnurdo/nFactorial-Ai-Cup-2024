import streamlit as st
import cohere
from dotenv import load_dotenv
import os
from PIL import Image

# Load environment variables
load_dotenv()

# Get the Cohere API key from the environment variables
cohere_api_key = os.getenv("COHERE_API_KEY")

# Initialize Cohere
co = cohere.Client(cohere_api_key)

logo = Image.open("pages/logo.png")
st.image(logo, width=150)

# Streamlit UI
st.title("AI-Powered Meal Planning")

# User inputs for dietary preferences and constraints
st.subheader("Enter your dietary preferences and constraints")
dietary_preferences = st.text_input("Dietary Preferences (e.g., vegan, keto, etc.)")
allergies = st.text_input("Allergies (e.g., peanuts, dairy, etc.)")
available_ingredients = st.text_area("Available Ingredients (separated by commas)")

# Generate meal plan
if st.button("Generate Meal Plan"):
    prompt = f"""
    Create a weekly meal plan based on the following preferences and constraints:
    Dietary Preferences: {dietary_preferences}
    Allergies: {allergies}
    Available Ingredients: {available_ingredients}

    Weekly Meal Plan:
    """
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=500,
        temperature=0.7
    )
    meal_plan = response.generations[0].text.strip()
    
    st.subheader("Weekly Meal Plan")
    st.markdown(f"<div style='background-color: #333333; padding: 15px; border-radius: 10px;'>{meal_plan}</div>", unsafe_allow_html=True)

    # Save meal plan to session state
    st.session_state['meal_plan'] = meal_plan
