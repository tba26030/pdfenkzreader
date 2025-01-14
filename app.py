import os
import streamlit as st
from uuid import uuid4
from pathlib import Path
import openai

# Initialize OpenAI API key input
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# Ensure a folder for serving static files
STATIC_DIR = Path("streamlit_static")
STATIC_DIR.mkdir(exist_ok=True)

# Function to translate words using GPT
def translate_word(api_key, word):
    """Translate a word from English to Kazakh using OpenAI."""
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a translator that only translates English words to Kazakh."},
                {"role": "user", "content": f"Translate this word to Kazakh: {word}"}
            ],
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        st.error(f"Error with OpenAI API: {str(e)}")
        return None

# File uploader for PDF files
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file:
    # Save the uploaded file to the static folder
    file_id = str(uuid4())
    file_path = STATIC_DIR / f"{file_id}.pdf"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Construct a full URL for the PDF file
    pdf_url = f"/streamlit_static/{file_path.name}"

    # Embed the iframe pointing to the index.html with the PDF URL
    clicked_word = st.components.v1.html(
        f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>PDF Viewer</title>
        </head>
        <body>
            <iframe
                src="/pdf_viewer_component/index.html?pdfUrl={pdf_url}"
                width="100%"
                height="800px"
                style="border:none;">
            </iframe>
        </body>
        </html>
        ''',
        height=800,
    )

    # Process clicked word for translation
    if isinstance(clicked_word, str):
        st.write(f"**Clicked Word:** {clicked_word}")
        if api_key:
            translation = translate_word(api_key, clicked_word)
            if translation:
                st.write(f"**Translation:** {clicked_word} → {translation}")
        else:
            st.warning("Please enter your OpenAI API key in the sidebar.")
else:
    st.warning("Please upload a PDF to view it.")
