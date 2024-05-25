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

# Streamlit UI
st.title("Favorite Recipes")

# Add new favorite recipe
st.subheader("Add New Favorite Recipe")
new_name = st.text_input("Recipe Name")
new_recipe = st.text_area("Recipe")
if st.button("Add Recipe"):
    if new_name and new_recipe:
        add_favorite(new_name, new_recipe)
        st.success("Recipe added to favorites!")
        # Update session state to reflect changes
        if 'favorites' in st.session_state:
            st.session_state['favorites'] = load_favorites()
    else:
        st.warning("Please provide both a name and a recipe.")

# Update existing favorite recipe
st.subheader("Update Favorite Recipe")
update_id = st.number_input("Recipe ID to Update", min_value=1, step=1)
update_name = st.text_input("Updated Recipe Name", key="update_name")
update_recipe = st.text_area("Updated Recipe", key="update_recipe")
if st.button("Update Recipe"):
    if update_id and update_name and update_recipe:
        update_favorite(update_id, update_name, update_recipe)
        st.success("Recipe updated!")
        # Update session state to reflect changes
        if 'favorites' in st.session_state:
            st.session_state['favorites'] = load_favorites()
    else:
        st.warning("Please provide the recipe ID, updated name, and updated recipe.")

# Delete favorite recipe
st.subheader("Delete Favorite Recipe")
delete_id = st.number_input("Recipe ID to Delete", min_value=1, step=1, key="delete_id")
if st.button("Delete Recipe"):
    if delete_id:
        delete_favorite(delete_id)
        st.success("Recipe deleted!")
        # Update session state to reflect changes
        if 'favorites' in st.session_state:
            st.session_state['favorites'] = load_favorites()
    else:
        st.warning("Please provide the recipe ID to delete.")

# Load favorites
if 'favorites' not in st.session_state:
    st.session_state['favorites'] = load_favorites()

favorites = st.session_state['favorites']

# Display favorite recipes
st.subheader("Saved Recipes")
if favorites:
    for idx, favorite in enumerate(favorites, start=1):
        st.write(f"{idx}. **{favorite.name}**")
        st.write(favorite.recipe)
else:
    st.write("No favorite recipes found.")

# Close the session
session.close()
