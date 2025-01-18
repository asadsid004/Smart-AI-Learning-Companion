from utils.chat_with_pdf import (
    add_to_vector_collection,
    query_collection,
    process_document,
    call_llm,
    re_rank_cross_encoders,
)
import streamlit as st

st.title("Chat with Pdf")

uploaded_file = st.file_uploader(
    "**📑 Upload PDF files for QnA**", type=["pdf"], accept_multiple_files=False
)

process = st.button(
    "⚡️ Process",
)
if uploaded_file and process:
    normalize_uploaded_file_name = uploaded_file.name.translate(
        str.maketrans({"-": "_", ".": "_", " ": "_"})
    )
    all_splits = process_document(uploaded_file)
    add_to_vector_collection(all_splits, normalize_uploaded_file_name)
prompt = st.text_area("**Ask a question related to your document:**")
ask = st.button(
    "🔥 Ask",
)

if ask and prompt:
    results = query_collection(prompt)
    context = results.get("documents")[0]
    relevant_text, relevant_text_ids = re_rank_cross_encoders(context, prompt)
    response = call_llm(context=relevant_text, prompt=prompt)
    st.write_stream(response)
