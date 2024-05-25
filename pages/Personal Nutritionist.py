import streamlit as st
import sqlite3
import json
from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()

# Get the OpenAI API key from the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key
openai.api_key = openai_api_key

# Initialize the SQLite database
conn = sqlite3.connect('fridge.db')
c = conn.cursor()

# File to store favorite recipes
favorites_file = "favorites.json"

# Function to load favorites
def load_favorites():
    if os.path.exists(favorites_file):
        with open(favorites_file, "r") as file:
            return json.load(file)
    return []

# Function to get all products from the fridge database
def get_all_products():
    c.execute('SELECT name, quantity FROM products')
    return c.fetchall()

# Function to analyze recipes and fridge items using OpenAI API
def analyze_nutrition(favorites, fridge_items, user_input=None):
    favorite_recipes = "\n".join([f"Recipe: {item['recipe']}" for item in favorites])
    fridge_contents = "\n".join([f"{item[0]}: {item[1]}" for item in fridge_items])

    prompt = f"""
    You are a personal nutritionist. Analyze the following favorite recipes and the items in the fridge.
    Provide personalized nutritional advice based on the analysis.

    Favorite Recipes:
    {favorite_recipes}

    Fridge Contents:
    {fridge_contents}

    Nutritional Advice:
    """

    if user_input:
        prompt += f"\nUser's Question: {user_input}\n"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    return response['choices'][0]['message']['content'].strip()

# Streamlit UI
st.title("Personal Nutritionist Chat with AI")

# Load favorites and fridge items
favorites = load_favorites()
fridge_items = get_all_products()

# Display favorite recipes
st.subheader("Favorite Recipes")
if favorites:
    for favorite in favorites:
        st.write(f"**{favorite['name']}**")
        st.write(favorite['recipe'])
else:
    st.write("No favorite recipes found.")

# Display fridge contents
st.subheader("Fridge Contents")
if fridge_items:
    for item in fridge_items:
        st.write(f"{item[0]}: {item[1]}")
else:
    st.write("No items in the fridge.")

# Initialize conversation history
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Button to start the chat
if st.button("Start Chat"):
    if not favorites and not fridge_items:
        st.warning("Add favorite recipes and items in the fridge to get nutritional advice.")
    else:
        initial_response = analyze_nutrition(favorites, fridge_items)
        st.session_state['conversation'] = initial_response
        st.session_state['chat_history'] = [(initial_response, "Nutritionist")]

        st.success("Chat started! You can now ask questions.")

# Chat interface
if st.session_state['conversation']:
    user_input = st.text_input("You:", key="user_input")

    if user_input:
        response = analyze_nutrition(favorites, fridge_items, user_input)
        st.session_state['chat_history'].append((user_input, "You"))
        st.session_state['chat_history'].append((response, "Nutritionist"))

    st.subheader("Chat History")
    for chat, role in st.session_state['chat_history']:
        if role == "You":
            st.markdown(f"<div style='padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; background-color: #6e7685;'>You: {chat}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; background-color: #495d85;'>Nutritionist: {chat}</div>", unsafe_allow_html=True)

# Close the database connection
conn.close()
