import streamlit as st
from streamlit_option_menu import option_menu
from pathlib import Path

# Load pages
pages = {
    "Home": "home_page.py",
    "Fridge Inventory": "Fridge.py",
    "Image Classification": "image_classification.py",
    "Personal Nutritionist": "Personal Nutritionist.py",
    "Recipe Generator": "recipe_generator.py"
}

st.set_page_config(page_title="AI Recipe App", page_icon="👋")

# Navigation bar
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=list(pages.keys()),
        icons=["house", "box", "image", "clipboard", "search"],
        menu_icon="cast",
        default_index=0,
    )

# Load selected page
page_path = Path(pages[selected])
with page_path.open("r") as f:
    exec(f.read())
