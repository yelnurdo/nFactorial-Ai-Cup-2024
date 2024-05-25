import streamlit as st
import openai
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
import sqlite3

# Load environment variables
load_dotenv()

# Get the tokens from the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

# Initialize the SQLite database
conn = sqlite3.connect('fridge.db')
c = conn.cursor()

# Create table for favorite recipes if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS favorite_recipes (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        recipe TEXT NOT NULL
    )
''')
conn.commit()

# Set the OpenAI API key
openai.api_key = openai_api_key

# Function to load favorites
def load_favorites():
    c.execute('SELECT id, name, recipe FROM favorite_recipes')
    return c.fetchall()

# Function to save favorites
def save_favorite(name, recipe):
    c.execute('INSERT INTO favorite_recipes (name, recipe) VALUES (?, ?)', (name, recipe))
    conn.commit()

# Function to generate the recipe using OpenAI GPT-3.5
def generate_recipe(ingredients):
    try:
        prompt = f"Generate a recipe with the following ingredients: {ingredients}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.7
        )
        recipe = response.choices[0].message['content'].strip()
        return recipe
    except Exception as e:
        st.error(f"Error generating recipe: {e}")
        return None

# Function to get the name of the dish from the generated recipe
def get_dish_name(recipe_text):
    try:
        prompt = f"Extract the name of the dish from the following recipe text, write only name nothing more only name: {recipe_text}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )
        dish_name = response.choices[0].message['content'].strip()
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
            st.write(recipe)

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
    st.sidebar.subheader(favorite[1])
    st.sidebar.write(favorite[2])

# Close the database connection
conn.close()
