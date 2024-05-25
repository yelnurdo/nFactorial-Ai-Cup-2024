import streamlit as st
import torch
from transformers import T5TokenizerFast, T5ForConditionalGeneration
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
import sqlite3

# Load environment variables
load_dotenv()

# Get the tokens from the environment variables
hf_token = os.getenv("HF_TOKEN")
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

# Function to load favorites
def load_favorites():
    c.execute('SELECT name, recipe FROM favorite_recipes')
    return c.fetchall()

# Function to save favorites
def save_favorite(name, recipe):
    c.execute('INSERT INTO favorite_recipes (name, recipe) VALUES (?, ?)', (name, recipe))
    conn.commit()

if not hf_token or not youtube_api_key:
    st.error("API tokens not found. Please add them to the .env file.")
else:
    # Load the T5 model and tokenizer with the token
    try:
        recipe_model = T5ForConditionalGeneration.from_pretrained("flax-community/t5-recipe-generation", use_auth_token=hf_token)
        recipe_tokenizer = T5TokenizerFast.from_pretrained("flax-community/t5-recipe-generation", use_auth_token=hf_token)
    except Exception as e:
        st.error(f"Error loading model or tokenizer: {e}")
        st.stop()

    # Function to generate the recipe
    def generate_recipe(ingredients):
        try:
            # Tokenize the ingredients
            inputs = recipe_tokenizer.encode_plus(
                ingredients,
                add_special_tokens=True,
                max_length=256,
                truncation=True,
                return_attention_mask=True,
                return_tensors="pt"
            )

            # Generate the recipe
            generation_kwargs = {
                "max_length": 512,
                "min_length": 64,
                "no_repeat_ngram_size": 3,
                "do_sample": True,
                "top_k": 60,
                "top_p": 0.95,
                "length_penalty": 1.5,
                "num_beams": 5  # Ensuring beam search is used
            }
            outputs = recipe_model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                **generation_kwargs
            )

            # Decode the generated recipe
            recipe = recipe_tokenizer.decode(outputs[0], skip_special_tokens=True)
            return recipe
        except Exception as e:
            st.error(f"Error generating recipe: {e}")
            return None

    # Function to get the name of the dish from the generated recipe
    def get_dish_name(recipe_text):
        # Extract the dish name from the generated recipe
        start_idx = recipe_text.lower().find("title:") + len("title:")
        end_idx = recipe_text.lower().find("recipe")
        if end_idx == -1:  # If "recipe" is not found, look for "ingredients"
            end_idx = recipe_text.lower().find("ingredients")
        if start_idx != -1 and end_idx != -1:
            dish_name = recipe_text[start_idx:end_idx].strip()
        else:
            dish_name = "Dish Name Not Generated Correctly"
        return dish_name

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
        st.sidebar.subheader(favorite[0])
        st.sidebar.write(favorite[1])

# Close the database connection
conn.close()
