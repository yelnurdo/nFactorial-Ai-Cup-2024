import streamlit as st
import cohere
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

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

# Function to recommend recipes using Cohere
def recommend_recipes(user_preferences):
    favorites = load_favorites()
    favorite_recipes = "\n".join([f"Recipe: {item.recipe}" for item in favorites])
    prompt = f"""
    Based on the following preferences and past favorite recipes, recommend new recipes.
    Preferences: {user_preferences}

    Favorite Recipes:
    {favorite_recipes}

    Recommended Recipes:
    """
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=500,
        temperature=0.7
    )
    recommended_recipes = response.generations[0].text.strip()
    return recommended_recipes

# Streamlit UI
st.title("Recipe Recommendation Engine")

# User preferences
st.subheader("Enter your preferences")
user_preferences = st.text_area("Preferences (e.g., spicy food, vegetarian, quick meals)")

# Recommend recipes
if st.button("Recommend Recipes"):
    recommended_recipes = recommend_recipes(user_preferences)
    st.subheader("Recommended Recipes")
    st.markdown(f"<div style='background-color: #333333; color: white; padding: 15px; border-radius: 10px;'>{recommended_recipes}</div>", unsafe_allow_html=True)
