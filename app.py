import streamlit as st
import fitz  # PyMuPDF for PDF
from ebooklib import epub  # For EPUB
from bs4 import BeautifulSoup  # For parsing EPUB content
import mammoth  # For DOC/DOCX
import openai

# Initialize session state for the word list
if "word_list" not in st.session_state:
    st.session_state.word_list = []

# Sidebar for OpenAI API key input
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# Function to translate words
def translate_word(api_key, word):
    """Translate a word from English to Kazakh using OpenAI's newer API."""
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt4o",
            messages=[
                {"role": "system", "content": "You are a Kazakh translator."},
                {"role": "user", "content": f"Translate this word to Kazakh: {word}"}
            ],
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        st.error(f"Error with OpenAI API: {str(e)}")
        return None

def save_word_pair(english_word, kazakh_word):
    """Saves the word pair to session state."""
    st.session_state.word_list.append({"English": english_word, "Kazakh": kazakh_word})
    st.success(f"Saved '{english_word}' - '{kazakh_word}' to the word list.")

def extract_text(file, file_type):
    """Extract text from non-PDF files."""
    if file_type == "epub":
        book = epub.read_epub(file)
        text = ""
        for item in book.get_items():
            if item.get_type() == 9:  # Text type
                soup = BeautifulSoup(item.get_content(), "html.parser")
                text += soup.get_text()
        return text
    elif file_type in ["doc", "docx"]:
        content = file.read()
        result = mammoth.extract_raw_text(content)
        return result.value
    else:
        return None

# File uploader
uploaded_file = st.file_uploader("Upload your file (PDF, EPUB, DOC, DOCX)", type=["pdf", "epub", "doc", "docx"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "pdf":
        # Render the PDF using pdf.js in a custom component
        clicked_word = st.components.v1.html(
            """
            <iframe id="pdf-viewer" src="pdf_viewer_component/index.html" 
                    width="100%" height="800px" style="border:none;"></iframe>
            <script>
                const iframe = document.getElementById('pdf-viewer');
                iframe.addEventListener('wordClick', (event) => {
                    const clickedWord = event.detail.word;
                    Streamlit.setComponentValue(clickedWord);
                });
            </script>
            """,
            height=800,
        )

        if clicked_word:
            st.write(f"**Clicked Word:** {clicked_word}")
            if api_key:
                translation = translate_word(api_key, clicked_word)
                if translation:
                    st.write(f"**Translation:** {clicked_word} → {translation}")
                    if st.button(f"Save '{clicked_word}' - '{translation}'"):
                        save_word_pair(clicked_word, translation)
            else:
                st.warning("Please enter your OpenAI API key in the sidebar.")

    else:
        # Handle non-PDF files (EPUB, DOC, etc.)
        text = extract_text(uploaded_file, file_type)

        if text:
            st.text_area("File Content", text, height=500)
            word_to_translate = st.text_input("Enter the word you selected for translation:")

            if st.button("Translate"):
                if api_key and word_to_translate:
                    translation = translate_word(api_key, word_to_translate)
                    if translation:
                        st.write(f"**Translation:** {word_to_translate} → {translation}")
                        if st.button(f"Save '{word_to_translate}' - '{translation}'"):
                            save_word_pair(word_to_translate, translation)
                elif not api_key:
                    st.warning("Please enter your OpenAI API key in the sidebar.")
                else:
                    st.warning("Please select a word first.")
        else:
            st.error("Unable to extract text from the uploaded file. Please check the file format.")

# Display saved word list
if st.session_state.word_list:
    st.subheader("Saved Word List")
    st.json(st.session_state.word_list)
