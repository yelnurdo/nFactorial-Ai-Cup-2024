import streamlit as st
from streamlit_option_menu import option_menu
from pathlib import Path

# Set page configuration
st.set_page_config(page_title="AI Recipe App", page_icon="👋", layout="wide")

# Define the navigation menu
with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["Home", "Recipe Generator", "Favorite Recipes"],
        icons=["house", "book", "heart"],
        menu_icon="cast",
        default_index=0,
    )

# Load the selected page
if selected == "Home":
    st.title("Welcome to the AI Recipe App!")
    st.write("Use the menu to navigate through the app.")
elif selected == "Recipe Generator":
    exec(Path("pages/recipe_generator.py").read_text())
elif selected == "Favorite Recipes":
    exec(Path("pages/FavoriteRecipes.py").read_text())
