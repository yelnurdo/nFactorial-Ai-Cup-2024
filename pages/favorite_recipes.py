import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the database URL from the environment variables
database_url = os.getenv("DATABASE_URL")

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

# Function to add a favorite recipe
def add_favorite(name, recipe):
    new_favorite = FavoriteRecipe(name=name, recipe=recipe)
    session.add(new_favorite)
    session.commit()

# Function to update a favorite recipe
def update_favorite(recipe_id, name, recipe):
    favorite = session.query(FavoriteRecipe).filter(FavoriteRecipe.id == recipe_id).first()
    if favorite:
        favorite.name = name
        favorite.recipe = recipe
        session.commit()

# Function to delete a favorite recipe
def delete_favorite(recipe_id):
    favorite = session.query(FavoriteRecipe).filter(FavoriteRecipe.id == recipe_id).first()
    if favorite:
        session.delete(favorite)
        session.commit()

# Custom CSS to style the page
st.markdown(
    """
    <style>
    .main-title {
        font-size: 3em;
        text-align: center;
        margin-top: 20px;
        font-weight: bold;
    }
    .sub-title {
        font-size: 2em;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .info-box {
        background-color: #333;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .input-box {
        margin-bottom: 20px;
    }
    .delete-button {
        color: red;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Page Title
st.markdown('<div class="main-title">Favorite Recipes</div>', unsafe_allow_html=True)

# Add new favorite recipe
st.markdown('<div class="sub-title">Add New Favorite Recipe</div>', unsafe_allow_html=True)
new_name = st.text_input("Recipe Name", key="new_name", placeholder="Enter recipe name")
new_recipe = st.text_area("Recipe", key="new_recipe", placeholder="Enter recipe details")
if st.button("Add Recipe"):
    if new_name and new_recipe:
        add_favorite(new_name, new_recipe)
        st.success("Recipe added to favorites!")
        if 'favorites' in st.session_state:
            st.session_state['favorites'] = load_favorites()
    else:
        st.warning("Please provide both a name and a recipe.")

# Update existing favorite recipe
st.markdown('<div class="sub-title">Update Favorite Recipe</div>', unsafe_allow_html=True)
update_id = st.number_input("Recipe ID to Update", min_value=1, step=1, key="update_id")
update_name = st.text_input("Updated Recipe Name", key="update_name", placeholder="Enter updated recipe name")
update_recipe = st.text_area("Updated Recipe", key="update_recipe", placeholder="Enter updated recipe details")
if st.button("Update Recipe"):
    if update_id and update_name and update_recipe:
        update_favorite(update_id, update_name, update_recipe)
        st.success("Recipe updated!")
        if 'favorites' in st.session_state:
            st.session_state['favorites'] = load_favorites()
    else:
        st.warning("Please provide the recipe ID, updated name, and updated recipe.")

# Load favorites
if 'favorites' not in st.session_state:
    st.session_state['favorites'] = load_favorites()

favorites = st.session_state['favorites']

# Display favorite recipes
st.markdown('<div class="sub-title">Saved Recipes</div>', unsafe_allow_html=True)
if favorites:
    for idx, favorite in enumerate(favorites, start=1):
        col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
        with col1:
            st.markdown(f"**ID: {favorite.id}**")
        with col2:
            st.text_input(f"Recipe Name {idx}", value=favorite.name, key=f"saved_name_{idx}", disabled=True)
            st.text_area(f"Recipe {idx}", value=favorite.recipe, key=f"saved_recipe_{idx}", disabled=True)
        with col3:
            if st.button("❌", key=f"delete_{favorite.id}"):
                delete_favorite(favorite.id)
                st.experimental_rerun()
else:
    st.write("No favorite recipes found.")

# Clear unused data from session state
if 'favorites' in st.session_state:
    del st.session_state['favorites']

# Close the session
session.close()
