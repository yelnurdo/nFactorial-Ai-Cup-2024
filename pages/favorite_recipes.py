import streamlit as st
from PIL import Image
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
logo = Image.open("pages/logo.png")
st.image(logo, width=150)

st.title("Избранные рецепты")

# Add new favorite recipe
st.subheader("Добавить новый рецепт в избранное")
new_name = st.text_input("Название рецепта")
new_recipe = st.text_area("Рецепт")
if st.button("Добавить рецепт"):
    if new_name and new_recipe:
        add_favorite(new_name, new_recipe)
        st.success("Рецепт добавлен в избранное!")
        if 'favorites' in st.session_state:
            st.session_state['favorites'] = load_favorites()
    else:
        st.warning("Пожалуйста, укажите название и рецепт.")

# Update existing favorite recipe
st.subheader("Обновить рецепт в избранном")
update_id = st.number_input("ID рецепта для обновления", min_value=1, step=1)
update_name = st.text_input("Обновленное название рецепта", key="update_name")
update_recipe = st.text_area("Обновленный рецепт", key="update_recipe")
if st.button("Обновить рецепт"):
    if update_id and update_name and update_recipe:
        update_favorite(update_id, update_name, update_recipe)
        st.success("Рецепт обновлен!")
        if 'favorites' in st.session_state:
            st.session_state['favorites'] = load_favorites()
    else:
        st.warning("Пожалуйста, укажите ID рецепта, обновленное название и рецепт.")

# Delete favorite recipe
st.subheader("Удалить рецепт из избранного")
if 'favorites' in st.session_state:
    favorites = st.session_state['favorites']
    for favorite in favorites:
        if st.button(f"Удалить {favorite.name}", key=f"delete_{favorite.id}"):
            delete_favorite(favorite.id)
            st.success(f"Рецепт {favorite.name} удален!")
            st.session_state['favorites'] = load_favorites()
else:
    st.write("Нет избранных рецептов.")

# Load favorites
if 'favorites' not in st.session_state:
    st.session_state['favorites'] = load_favorites()

favorites = st.session_state['favorites']

# Display favorite recipes
st.subheader("Сохраненные рецепты")
if favorites:
    for idx, favorite in enumerate(favorites, start=1):
        st.write(f"{idx}. **{favorite.name}** (ID: {favorite.id})")
        st.write(favorite.recipe)
else:
    st.write("Нет избранных рецептов.")

# Close the session
session.close()
