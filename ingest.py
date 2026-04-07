import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import streamlit as st
import time

# Embeddings global definieren
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vectorstore():
    return Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

def ingest_local_code():
    """Diese Funktion kapselt deinen bisherigen 'print'-Code"""
    if not os.path.exists('./code'):
        return "Ordner ./code nicht gefunden."
        
    loader = DirectoryLoader(
        './code', 
        glob="**/*.py", 
        exclude=["venv/**", "**/__pycache__/**", "chroma_db/**"],
        loader_cls=TextLoader
    )
    docs = loader.load()
    
    if not docs:
        return "Keine Dateien gefunden."

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    vectorstore = get_vectorstore()
    vectorstore.add_documents(splits)
    return f"Fertig! {len(splits)} Code-Fragmente gespeichert."

def process_web_url(url, vector_store):
    # HIER LAG DER FEHLER: Alles unter 'def' muss eingerückt sein!
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    loader = WebBaseLoader(web_path=url, requests_kwargs={"headers": headers})
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)
    vector_store.add_documents(chunks)
    return len(chunks)

def batch_add_documents(vector_store, chunks, batch_size=4000):
    """Hilfsfunktion, um das Batch-Limit von ChromaDB zu umgehen."""
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        vector_store.add_documents(batch)

def ingest_web_docs(sitemap_url, vector_store):
    from utils.web_processor import get_sitemap_loader, get_recursive_loader
    
    # SCHRITT 1: Sitemap-Versuch
    loader = get_sitemap_loader(sitemap_url)
    try:
        st.write("🔍 Prüfe Sitemap...")
        docs = loader.load()
        
        # SCHRITT 2: Index-Fallback (Automatischer Wechsel)
        if not docs:
            st.info("Sitemap-Index erkannt. Versuche verschachtelte Sitemaps aufzulösen...")
            loader.is_sitemap_index = True
            if "pytorch.org" in sitemap_url:
                loader.sitemap_filter = ["/docs/stable/"]
            docs = loader.load()
            
        # SCHRITT 3: Der "Rettungs-Anker" - Automatischer Wechsel zum Crawler
        if not docs or len(docs) == 0:
            st.warning("Sitemap blockiert oder leer. Starte automatischen Web-Crawler als Fallback...")
            # Wir wandeln die sitemap.xml URL in eine normale HTML URL um
            base_url = sitemap_url.replace("sitemap.xml", "index.html")
            recursive_loader = get_recursive_loader(base_url, max_depth=2)
            docs = recursive_loader.load()

        if not docs:
            return 0, 0

        # Verarbeitung der gefundenen Dokumente
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)
        
        if chunks:
            from ingest import batch_add_documents
            batch_add_documents(vector_store, chunks)
            return len(docs), len(chunks)
        
        return len(docs), 0
        
    except Exception as e:
        st.error(f"Automatisierung abgebrochen: {str(e)}")
        return 0, 0

def ingest_recursive_web(url, vector_store, depth=2):
    from utils.web_processor import get_recursive_loader
    loader = get_recursive_loader(url, max_depth=depth)
    docs = loader.load()
    
    if not docs:
        return 0, 0

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    
    if chunks:
        # STATT: vector_store.add_documents(chunks)
        batch_add_documents(vector_store, chunks)
        return len(docs), len(chunks)
    return len(docs), 0    