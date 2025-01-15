import fitz  # PyMuPDF for handling PDFs
import streamlit as st

# Initialize session state for saved translations
if "saved_translations" not in st.session_state:
    st.session_state.saved_translations = []

# Debug log function
def debug_log(message):
    st.text(f"DEBUG: {message}")

# File uploader for PDFs
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

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
            st.write("### Page Content")
            st.markdown(f"```\n{text}\n```")
        except Exception as e:
            st.error(f"Failed to extract text: {e}")
            debug_log(f"Error extracting text: {e}")
else:
    st.info("Upload a PDF to get started.")

# Show saved translations
if st.session_state.saved_translations:
    st.subheader("Saved Translations")
    for translation in st.session_state.saved_translations:
        st.write(f"{translation['English']} → {translation['Kazakh']}")
