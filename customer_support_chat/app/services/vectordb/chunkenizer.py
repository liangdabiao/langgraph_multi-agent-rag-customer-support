# customer_support_chat/app/services/vectordb/chunkenizer.py

from langchain.text_splitter import RecursiveCharacterTextSplitter

def recursive_character_splitting(text, chunk_size=300, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    return chunks
