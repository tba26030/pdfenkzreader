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
                iframe.contentWindow.addEventListener('click', function(event) {
                    const clickedWord = event.target.textContent.trim(); // Captures the clicked word
                    if (clickedWord) {
                        console.log("Clicked Word:", clickedWord); // Debug in browser console
                        Streamlit.setComponentValue(clickedWord);
                    }
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
        st.error("Currently, only PDFs are supported for direct word selection.")
else:
    st.warning("Please upload a PDF file.")

# Display saved word list
if st.session_state.word_list:
    st.subheader("Saved Word List")
    st.json(st.session_state.word_list)

import streamlit as st

# Embed the HTML content directly into Streamlit
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Viewer</title>
    <script src="https://mozilla.github.io/pdf.js/build/pdf.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        #viewer {
            height: 100vh;
            width: 100vw;
        }
    </style>
</head>
<body>
    <canvas id="viewer"></canvas>
    <script>
        const url = "sample.pdf"; // Replace with your dynamic PDF URL
        const pdfjsLib = window['pdfjs-dist/build/pdf'];
        const canvas = document.getElementById('viewer');
        const ctx = canvas.getContext('2d');

        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://mozilla.github.io/pdf.js/build/pdf.worker.js';

        // Load PDF
        pdfjsLib.getDocument(url).promise.then(pdf => {
            pdf.getPage(1).then(page => {
                const viewport = page.getViewport({ scale: 1.5 });
                canvas.width = viewport.width;
                canvas.height = viewport.height;

                const renderContext = {
                    canvasContext: ctx,
                    viewport: viewport,
                };
                page.render(renderContext);
            });
        });
    </script>
</body>
</html>
"""

# Render the HTML content directly
st.components.v1.html(html_content, height=800)

