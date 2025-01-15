import fitz  # PyMuPDF for handling PDFs
import streamlit as st
import re
from streamlit_js_eval import streamlit_js_eval
from openai import OpenAI
import os

# Initialize OpenAI client
if "OPENAI_API_KEY" not in st.secrets:
    st.sidebar.text_input("Enter OpenAI API Key", type="password", key="openai_api_key")
    if "openai_api_key" in st.session_state:
        client = OpenAI(api_key=st.session_state.openai_api_key)
else:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize session state
if "saved_translations" not in st.session_state:
    st.session_state.saved_translations = []
if "selected_word" not in st.session_state:
    st.session_state.selected_word = None

# Custom CSS for word styling and tooltip
st.markdown("""
<style>
.word-span {
    display: inline;
    cursor: pointer;
    padding: 2px;
}
.word-span:hover {
    background-color: #f0f0f0;
}
.translation-modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    z-index: 1000;
}
</style>
""", unsafe_allow_html=True)

def process_text(text):
    """Split text into words while preserving whitespace and punctuation"""
    words = re.findall(r'\S+|\s+', text)
    return words

def get_translation(word):
    """Translate word using OpenAI API"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a translator. Translate the given English word to Kazakh. Provide only the translation without any additional text or explanation."},
                {"role": "user", "content": f"Translate this word to Kazakh: {word}"}
            ],
            temperature=0.3,
            max_tokens=50
        )
        translation = response.choices[0].message.content.strip()
        return translation
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return "Translation failed"

def create_interactive_text(words):
    """Create interactive text with clickable words"""
    html_parts = []
    for word in words:
        if word.strip():  # If it's a word (not whitespace)
            html_parts.append(
                f'<span class="word-span" onclick="handle_word_click(\'{word}\')">{word}</span>'
            )
        else:  # If it's whitespace
            html_parts.append(word)
    return ''.join(html_parts)

# File uploader for PDFs
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page_count = len(doc)
        
        # Page selection slider
        page_number = st.slider("Select a page", 1, page_count, 1)
        page = doc[page_number - 1]
        
        # Extract and process text
        text = page.get_text("text")
        words = process_text(text)
        
        # Display interactive text
        st.markdown(create_interactive_text(words), unsafe_allow_html=True)
        
        # Handle word selection
        if st.session_state.selected_word:
            word = st.session_state.selected_word
            with st.spinner(f'Translating "{word}"...'):
                translation = get_translation(word)
            
            # Create a modal for translation
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown("### Translation")
                    st.write(f"**{word}**: {translation}")
                    if st.button("Save Translation"):
                        st.session_state.saved_translations.append({
                            "English": word,
                            "Kazakh": translation
                        })
                        st.success("Translation saved!")
                    if st.button("Close"):
                        st.session_state.selected_word = None
                        st.rerun()
        
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        
else:
    st.info("Upload a PDF to get started.")

# Show saved translations in a sidebar
with st.sidebar:
    if st.session_state.saved_translations:
        st.subheader("Saved Translations")
        for translation in st.session_state.saved_translations:
            st.write(f"🔤 {translation['English']} → {translation['Kazakh']}")
        
        # Add export functionality
        if st.button("Export Translations"):
            import pandas as pd
            import base64
            
            # Convert to DataFrame
            df = pd.DataFrame(st.session_state.saved_translations)
            
            # Convert to CSV
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            
            # Create download link
            href = f'<a href="data:file/csv;base64,{b64}" download="my_translations.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)

# JavaScript for handling word clicks
st.markdown("""
<script>
function handle_word_click(word) {
    window.parent.postMessage({
        type: "streamlit:setComponentValue",
        value: word
    }, "*");
}
</script>
""", unsafe_allow_html=True)
