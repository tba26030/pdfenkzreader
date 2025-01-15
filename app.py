import fitz  # PyMuPDF for handling PDFs
import streamlit as st
import openai

# Initialize OpenAI API key input
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# File uploader for PDFs
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file:
    # Load the PDF using PyMuPDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    page_count = len(doc)
    
    # Page selection slider
    page_number = st.slider("Select a page", 1, page_count, 1)
    page = doc[page_number - 1]
    
    # Extract text from the page
    text = page.get_text("text")
    st.write("**Click a word below to translate:**")

    # Split text into words and display each word as a clickable button
    words = text.split()
    for word in words:
        if st.button(word):
            if api_key:
                try:
                    # Call OpenAI GPT API to translate the clicked word
                    openai.api_key = api_key
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a translator that only translates English words to Kazakh."},
                            {"role": "user", "content": f"Translate this word to Kazakh: {word}"}
                        ],
                    )
                    translation = response.choices[0].message["content"].strip()
                    st.success(f"Translation: {word} → {translation}")
                except Exception as e:
                    st.error(f"Error with OpenAI API: {str(e)}")
            else:
                st.warning("Please enter your OpenAI API key.")
else:
    st.info("Upload a PDF file to get started.")
