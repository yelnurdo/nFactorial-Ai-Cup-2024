import streamlit as st
import sqlite3

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
    c.execute('SELECT id, name, recipe FROM favorite_recipes')
    return c.fetchall()

# Function to add a favorite recipe
def add_favorite(name, recipe):
    c.execute('INSERT INTO favorite_recipes (name, recipe) VALUES (?, ?)', (name, recipe))
    conn.commit()

# Function to update a favorite recipe
def update_favorite(recipe_id, name, recipe):
    c.execute('UPDATE favorite_recipes SET name = ?, recipe = ? WHERE id = ?', (name, recipe, recipe_id))
    conn.commit()

# Function to delete a favorite recipe
def delete_favorite(recipe_id):
    c.execute('DELETE FROM favorite_recipes WHERE id = ?', (recipe_id,))
    conn.commit()

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
        st.write(f"{idx}. **{favorite[1]}**")
        st.write(favorite[2])
else:
    st.write("No favorite recipes found.")

# Close the database connection
conn.close()
