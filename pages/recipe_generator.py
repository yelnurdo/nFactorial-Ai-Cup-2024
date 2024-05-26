import streamlit as st
import cohere
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PIL import Image

logo = Image.open("pages/logo.png")
st.image(logo, width=150)
# Load environment variables
load_dotenv()

# Get the tokens from the environment variables
cohere_api_key = os.getenv("COHERE_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
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

# Function to save favorites
def save_favorite(name, recipe):
    new_favorite = FavoriteRecipe(name=name, recipe=recipe)
    session.add(new_favorite)
    session.commit()

# Function to generate the recipe using Cohere
def generate_recipe(ingredients):
    try:
        prompt = f"Generate a recipe with the following ingredients: {ingredients}"
        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=512,
            temperature=0.7
        )
        recipe = response.generations[0].text.strip()
        return recipe
    except Exception as e:
        st.error(f"Error generating recipe: {e}")
        return None

# Function to get the name of the dish from the generated recipe
def get_dish_name(recipe_text):
    try:
        prompt = f"Extract the name of the dish from the following recipe text, output only name of the dish nothing else!: {recipe_text}"
        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=50,
            temperature=0.7
        )
        dish_name = response.generations[0].text.strip()
        return dish_name
    except Exception as e:
        st.error(f"Error extracting dish name: {e}")
        return "Dish Name Not Generated Correctly"

# Function to search for a YouTube video
def search_youtube_video(query):
    youtube = build("youtube", "v3", developerKey=youtube_api_key)
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    response = request.execute()
    video_id = response["items"][0]["id"]["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return video_url

# Load favorites
favorites = load_favorites()

# Create a Streamlit page
st.title("Recipe Generator")
st.write("Enter the ingredients you have, and I'll generate a recipe for you!")

# Create a text input for the user to enter ingredients
ingredients_input = st.text_input("Ingredients (separated by commas):")

# Create a button to generate the recipe
if st.button("Generate Recipe"):
    if not ingredients_input.strip():
        st.warning("Please enter the ingredients you have.")
    else:
        # Generate the recipe
        st.write(f"Generating recipe for: {ingredients_input}")
        recipe = generate_recipe(ingredients_input)
        if recipe:
            st.subheader("Generated Recipe")
            st.markdown(f"<div style='background-color: #333333; color: white; padding: 15px; border-radius: 10px;'>{recipe}</div>", unsafe_allow_html=True)

            # Get the name of the dish
            dish_name = get_dish_name(recipe)
            st.subheader("Dish Name")
            st.write(dish_name)

            # Search for a YouTube video of the dish
            video_url = search_youtube_video(dish_name + " cooking")
            st.subheader("Recipe Video")
            st.video(video_url)

            # Store the generated recipe and dish name in the session state
            st.session_state["generated_recipe"] = recipe
            st.session_state["dish_name"] = dish_name

# Check if there's a generated recipe in the session state
if "generated_recipe" in st.session_state and "dish_name" in st.session_state:
    # Create a favorite button to save the recipe
    if st.button("Add to Favorites List"):
        save_favorite(st.session_state["dish_name"], st.session_state["generated_recipe"])
        st.success("Recipe added to favorites!")

# Display favorite recipes
st.sidebar.header("Favorite Recipes")
for favorite in favorites:
    st.sidebar.subheader(favorite.name)
    st.sidebar.write(favorite.recipe)

# Close the session
session.close()
