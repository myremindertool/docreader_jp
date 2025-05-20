
import streamlit as st
from openai import OpenAI
import docx
import pdfplumber
import os

# ------------------ Configuration ------------------ #
st.set_page_config(page_title="GPT Document Extractor", layout="centered")
st.title("📄 GPT Document Extractor")
st.markdown("Upload a document and ask GPT to extract anything you want.")

# ------------------ OpenAI API Key ------------------ #
openai_api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
if not openai_api_key:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()

# ------------------ File Upload ------------------ #
uploaded_file = st.file_uploader("📤 Upload a PDF or DOCX file", type=["pdf", "docx"])
custom_prompt = st.text_area("🧠 What do you want to extract?", "Extract summary, names, dates, and key points.")

# ------------------ Read Document ------------------ #
def read_pdf(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# ------------------ Ask GPT ------------------ #
def ask_gpt(prompt, content):
    client = OpenAI(api_key=openai_api_key)
    full_prompt = f"{prompt}\n\nDocument:\n{content[:7000]}"  # Limit for token safety
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.2,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ------------------ Main Logic ------------------ #
if uploaded_file and custom_prompt and openai_api_key:
    file_text = ""
    file_name = uploaded_file.name

    with st.spinner("🔍 Reading document..."):
        if file_name.endswith(".pdf"):
            file_text = read_pdf(uploaded_file)
        elif file_name.endswith(".docx"):
            file_text = read_docx(uploaded_file)
        else:
            st.error("Unsupported file format.")

    if file_text:
        st.success("✅ File read successfully. Ready to extract.")
        if st.button("🚀 Run GPT Extraction"):
            with st.spinner("💬 Talking to GPT..."):
                result = ask_gpt(custom_prompt, file_text)
                st.markdown("### ✅ Extracted Information")
                st.write(result)
