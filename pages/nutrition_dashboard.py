import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

logo = Image.open("pages/logo.png")
st.image(logo, width=150)
# Dummy nutritional data for demonstration
data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Calories": [2000, 1800, 2200, 2100, 1900, 2300, 2000],
    "Proteins": [50, 60, 55, 70, 65, 75, 60],
    "Fats": [70, 65, 75, 80, 60, 85, 70],
    "Carbohydrates": [300, 250, 350, 330, 280, 360, 300]
}
df = pd.DataFrame(data)

st.title("Interactive Nutrition Dashboard")

# Plotly chart
fig = px.line(df, x='Day', y=['Calories', 'Proteins', 'Fats', 'Carbohydrates'], title='Nutritional Intake Over the Week')
st.plotly_chart(fig)
