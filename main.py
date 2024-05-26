import streamlit as st
from PIL import Image

# Set page configuration
st.set_page_config(page_title="NutriVision", page_icon="🍽️", layout="wide")

# Load logo
logo = Image.open("pages/logo.png")

# Custom CSS to style the page
st.markdown(
    """
    <style>
    .main-title {
        font-size: 4em;
        text-align: center;
        color: #4CAF50;
        font-weight: bold;
        margin-top: -100px;
    }
    .sub-title {
        font-size: 2em;
        text-align: center;
        color: #4CAF50;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .info-box {
        background-color: #333;
        padding: 30px;
        border-radius: 10px;
        color: #fff;
    }
    .feature-list {
        font-size: 1.5rem;
        line-height: 2;
    }
    .logo-title-container {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .logo {
        width: 150px;
        margin-right: 20px;
        margin-bottom: 0px;
    }
    .page-title {
        font-size: 1.2em;
        text-align: center;
        color: #4CAF50;
        margin-top: 20px;
        font-weight: bold;
    }
    .feature-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 50%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Page Title with Logo
st.markdown('<div class="logo-title-container">', unsafe_allow_html=True)
st.image(logo, width=150)
st.markdown(
    """
    <div>
        <div class="main-title">Welcome to NutriVision</div>
        <div class="sub-title">Your Personal AI-Powered Nutrition and Meal Planning Assistant</div>
    </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# About Section
st.markdown(
    """
    <div class="info-box">
        <h2>About NutriVision</h2>
        <p>NutriVision is your ultimate AI-powered assistant for all things related to nutrition, meal planning, and healthy living. Our app offers a variety of features to help you stay on top of your dietary needs:</p>
        <ul class="feature-list">
            <li><b>Favorite Recipes:</b> Save and manage your favorite recipes all in one place.</li>
            <li><b>Image Classification:</b> Identify food items and their ingredients through image uploads.</li>
            <li><b>Personal Nutritionist:</b> Get personalized nutritional advice based on your dietary preferences and saved recipes.</li>
            <li><b>Recipe Generator:</b> Generate new and exciting recipes based on the ingredients you have.</li>
            <li><b>Meal Planning:</b> Plan your weekly meals with ease, accommodating dietary restrictions and preferences.</li>
            <li><b>Nutrition Dashboard:</b> Visualize your nutritional intake over time with dynamic charts and insights.</li>
            <li><b>Recipe Recommendation:</b> Get recipe recommendations based on your preferences, past behavior, and seasonal ingredients.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)
