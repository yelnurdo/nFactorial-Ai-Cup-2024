import streamlit as st
import cohere
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PIL import Image

logo = Image.open("pages/logo.png")
st.image(logo, width=150)

# Load environment variables
load_dotenv()

# Get the Cohere API key and database URL from the environment variables
cohere_api_key = os.getenv("COHERE_API_KEY")
database_url = os.getenv("DATABASE_URL")

# Initialize Cohere
co = cohere.Client(cohere_api_key)

# Initialize SQLAlchemy
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Define the FavoriteRecipe model
class FavoriteRecipe(Base):
    __tablename__ = 'favorite_recipes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    recipe = Column(Text, nullable=False)

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Function to load favorites
def load_favorites():
    return session.query(FavoriteRecipe).all()

# Function to analyze recipes using Cohere API
def analyze_nutrition(favorites, user_input=None):
    favorite_recipes = "\n".join([f"Recipe: {item.recipe}" for item in favorites])

    prompt = f"""
    You are a personal nutritionist. Analyze the following favorite recipes and provide detailed nutritional advice.

    Favorite Recipes:
    {favorite_recipes}

    Nutritional Advice:
    """

    if user_input:
        prompt += f"\nUser's Question: {user_input}\n"

    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=500,
        temperature=0.7
    )

    return response.generations[0].text.strip()

# Streamlit UI
st.title("Personal Nutritionist Chat with AI")

# Initialize conversation history
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Button to start the chat
if st.button("Start Chat"):
    favorites = load_favorites()
    if not favorites:
        st.warning("Add favorite recipes to get nutritional advice.")
    else:
        initial_response = analyze_nutrition(favorites)
        st.session_state['conversation'] = initial_response
        st.session_state['chat_history'] = [(initial_response, "Nutritionist")]

        st.success("Chat started! You can now ask questions.")

# Load favorites
favorites = load_favorites()

# Display favorite recipes with expanders
st.subheader("Favorite Recipes")
if favorites:
    for favorite in favorites:
        with st.expander(f"{favorite.name} (ID: {favorite.id})"):
            st.write(favorite.recipe)
            if st.button("Delete", key=f"delete_{favorite.id}"):
                session.delete(favorite)
                session.commit()
                st.experimental_rerun()
else:
    st.write("No favorite recipes found.")

# Chat interface at the end of the page
if st.session_state['conversation']:
    st.subheader("Chat History")
    for chat, role in st.session_state['chat_history']:
        if role == "You":
            st.markdown(f"<div style='padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; background-color: #6e7685;'>You: {chat}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; background-color: #495d85;'>Nutritionist: {chat}</div>", unsafe_allow_html=True)

    user_input = st.text_input("You:", key="user_input")

    if user_input:
        response = analyze_nutrition(favorites, user_input)
        st.session_state['chat_history'].append((user_input, "You"))
        st.session_state['chat_history'].append((response, "Nutritionist"))
        st.experimental_rerun()
