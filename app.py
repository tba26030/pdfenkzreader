import streamlit as st
import fitz  # PyMuPDF for PDF
from ebooklib import epub  # For EPUB
from bs4 import BeautifulSoup  # For parsing EPUB content
import mammoth  # For DOC/DOCX
import openai
import streamlit.components.v1 as components
import os
from uuid import uuid4

# Initialize session state for the word list
if "word_list" not in st.session_state:
    st.session_state.word_list = []

# Sidebar for OpenAI API key input
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# Function to translate words
def translate_word(api_key, word):
    """Translate a word from English to Kazakh using the updated OpenAI API."""
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a translator that only translates English to Kazakh."},
                {"role": "user", "content": f"Translate this word to Kazakh: {word}"}
            ]
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        st.error(f"Error with OpenAI API: {str(e)}")
        return None

def save_word_pair(english_word, kazakh_word):
    """Saves the word pair to session state."""
    st.session_state.word_list.append({"English": english_word, "Kazakh": kazakh_word})
    st.success(f"Saved '{english_word}' - '{kazakh_word}' to the word list.")

# File uploader for user-uploaded PDFs
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file:
    # Save the uploaded file to a temporary directory
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    file_id = str(uuid4())  # Generate a unique ID for the file
    file_path = os.path.join(temp_dir, f"{file_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Serve the PDF file dynamically by injecting its path into the HTML
    clicked_word = st.components.v1.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PDF Viewer</title>
        </head>
        <body>
            <iframe
                src="/pdf_viewer_component/index.html?pdfUrl=file://{file_path}"
                width="100%"
                height="800px"
                style="border:none;">
            </iframe>
        </body>
        </html>
        """,
        height=800,
    )

    # Check if a clicked word was received
    if isinstance(clicked_word, str):
        st.write(f"**Clicked Word:** {clicked_word}")
        # Implement your translation logic here
    else:
        st.warning("No word was clicked yet.")

# Display saved word list
if st.session_state.word_list:
    st.subheader("Saved Word List")
    st.json(st.session_state.word_list)
