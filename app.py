import fitz  # PyMuPDF for handling PDFs
import streamlit as st
import re
import openai

# CSS for Better Readability
st.markdown("""
<style>
#text-container {
    font-family: Arial, sans-serif;
    font-size: 16px;
    line-height: 1.5;
    text-align: justify;
    margin: 10px 0;
}
.word {
    cursor: pointer;
    color: blue;
}
.word:hover {
    background-color: yellow;
}
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI API key input
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# Initialize session state for saved translations and selected word
if "saved_translations" not in st.session_state:
    st.session_state.saved_translations = []
if "selected_word" not in st.session_state:
    st.session_state.selected_word = None

# Function to split text into words and wrap with spans
def process_text_to_html(text):
    """Wrap each word in a span for interactivity."""
    words = re.findall(r'\S+|\s+', text)  # Keep words and whitespace
    html_parts = []
    for word in words:
        if word.strip():  # Only process non-whitespace words
            html_parts.append(
                f'<span class="word" onclick="handleWordClick(\'{word}\')">{word}</span>'
            )
        else:
            html_parts.append(word)  # Preserve whitespace
    return ''.join(html_parts)

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
        return f"Error: {e}"

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
        
        # Extract text
        text = page.get_text("text")
        if not text.strip():
            st.warning("No text found on this page. Try another page.")
        else:
            # Display interactive text
            st.markdown(
                f"""
                <div id="text-container">
                    {process_text_to_html(text)}
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
            
            # Handle word translation
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
                st.info(f"Selected word: {clicked_word}")
                with st.spinner(f"Translating '{clicked_word}'..."):
                    translation = translate_word(clicked_word)
                st.success(f"Translation: {clicked_word} → {translation}")
                if st.button("Save Translation"):
                    st.session_state.saved_translations.append({"English": clicked_word, "Kazakh": translation})
                    st.success("Translation saved!")
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
