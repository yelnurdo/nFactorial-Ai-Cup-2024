import streamlit as st
from PIL import Image
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Streamlit App
st.title("GPT-4 Image Classification App")

# Upload an image
st.header("Upload an image for classification")
uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    # Convert image to bytes
    image_bytes = uploaded_image.read()

    # Generate description using GPT-4
    def get_image_description(image_data):
        response = openai.Image.create(
            image=image_data,
            prompt="Describe the contents of this image in detail",
            n=1,
            size="256x256"
        )
        return response['data'][0]['text']

    description = get_image_description(image_bytes)
    st.write("Image Description:", description)
