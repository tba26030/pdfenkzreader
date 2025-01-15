import fitz  # PyMuPDF for handling PDFs
import streamlit as st
import re
import openai

# Initialize OpenAI API key input
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# Initialize session state for saved translations and selected word
if "saved_translations" not in st.session_state:
    st.session_state.saved_translations = []
if "selected_word" not in st.session_state:
    st.session_state.selected_word = None

# Function to split text into words while preserving whitespace
def process_text(text):
    return re.findall(r'\S+|\s+', text)

# Function to translate a word using OpenAI GPT
def translate_word(word):
    try:
        if not api_key:
            raise ValueError("OpenAI API Key is missing.")
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Translate the given English word to Kazakh."},
                {"role": "user", "content": f"Translate this word to Kazakh: {word}"}
            ],
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Translation error: {e}"

# File uploader for PDFs
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file:
    try:
        # Load the PDF with PyMuPDF
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page_count = len(doc)
        
        # Page selection slider
        page_number = st.slider("Select a page", 1, page_count, 1)
        page = doc[page_number - 1]
        
        # Extract and process text
        text = page.get_text("text")
        words = process_text(text)
        
        # Display text with clickable words
        st.markdown("### Page Content")
        for word in words:
            if word.strip():  # If it's a valid word (not whitespace)
                if st.button(word):
                    st.session_state.selected_word = word  # Save the clicked word
            else:
                st.write(word, unsafe_allow_html=True)  # Preserve whitespace
            
        # Handle word translation if a word is selected
        if st.session_state.selected_word:
            word = st.session_state.selected_word
            st.info(f"Selected word: {word}")
            with st.spinner(f"Translating '{word}'..."):
                translation = translate_word(word)
            st.success(f"Translation: {word} → {translation}")
            if st.button("Save Translation"):
                st.session_state.saved_translations.append({"English": word, "Kazakh": translation})
                st.success("Translation saved!")
                st.session_state.selected_word = None  # Clear selection
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
else:
    st.info("Upload a PDF to get started.")

# Display saved translations in a sidebar
with st.sidebar:
    st.subheader("Saved Translations")
    if st.session_state.saved_translations:
        for translation in st.session_state.saved_translations:
            st.write(f"{translation['English']} → {translation['Kazakh']}")
    else:
        st.write("No translations saved yet.")
