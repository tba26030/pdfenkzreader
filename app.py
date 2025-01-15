import fitz  # PyMuPDF for handling PDFs
import streamlit as st
import openai
import re

# Initialize OpenAI API key input
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# Initialize session state for saved translations
if "saved_translations" not in st.session_state:
    st.session_state.saved_translations = []

# Debug logs
def debug_log(message):
    st.text(f"DEBUG: {message}")

# File uploader for PDFs
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

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
        return f"Error: {str(e)}"

if uploaded_file:
    # Load the PDF with PyMuPDF
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page_count = len(doc)
        debug_log(f"PDF loaded successfully with {page_count} pages.")
    except Exception as e:
        st.error(f"Failed to load PDF: {e}")
        debug_log(f"Error loading PDF: {e}")
        doc = None

    if doc:
        # Page selection slider
        page_number = st.slider("Select a page", 1, page_count, 1)
        page = doc[page_number - 1]

        # Extract text from the page
        try:
            text = page.get_text("text")
            debug_log(f"Text extracted successfully from page {page_number}.")
        except Exception as e:
            st.error(f"Failed to extract text: {e}")
            debug_log(f"Error extracting text: {e}")
            text = ""

        # Make words clickable
        def render_clickable_text(text):
            """Render text with clickable words."""
            words = text.split()
            processed_text = []
            for word in words:
                clean_word = re.sub(r'[^\w]', '', word)  # Clean punctuation
                if clean_word:  # Ensure it's a valid word
                    tooltip = f'<span style="cursor: pointer;" onclick="handleWordClick(\'{clean_word}\')">{word}</span>'
                    processed_text.append(tooltip)
                else:
                    processed_text.append(word)  # Append as is if not a word
            return " ".join(processed_text)

        # Display the text with interactive words
        st.write(
            f"""
            <div id="book-content">
                {render_clickable_text(text)}
            </div>
            <script>
            function handleWordClick(word) {{
                const streamlit = parent.streamlit;
                streamlit.setComponentValue(word);
            }}
            </script>
            """,
            unsafe_allow_html=True,
        )

        # Handle clicked word
        clicked_word = st.components.v1.html(
            """
            <script>
            const streamlit = window.parent.streamlit;
            streamlit.setComponentValue(null);
            </script>
            """,
            height=0,
        )
        if clicked_word:
            st.info(f"You clicked: {clicked_word}")
            if api_key:
                translation = translate_word(api_key, clicked_word)
                st.success(f"Translation: {clicked_word} → {translation}")
                if st.button("Save Translation"):
                    st.session_state.saved_translations.append(
                        {"English": clicked_word, "Kazakh": translation}
                    )
                    st.success("Translation saved!")
            else:
                st.warning("Please enter your OpenAI API key.")

        # Show saved translations
        if st.session_state.saved_translations:
            st.subheader("Saved Translations")
            for translation in st.session_state.saved_translations:
                st.write(f"{translation['English']} → {translation['Kazakh']}")
else:
    st.info("Upload a PDF to get started.")
