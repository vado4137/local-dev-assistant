import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 1. Dokumente laden - EXTREM WICHTIG: venv ignorieren!
print("Lade Dokumente (ohne venv)...")
# Wir nutzen hier eine Liste von Dateien, um venv gezielt auszuschließen
loader = DirectoryLoader(
    './code', 
    glob="**/*.py", 
    exclude=["venv/**", "**/__pycache__/**", "chroma_db/**"], # Hier werden die Störenfriede ignoriert
    loader_cls=TextLoader,
    show_progress=True
)
docs = loader.load()

# Rest bleibt gleich...
if not docs:
    print("Keine Dateien gefunden! Hast du schon eigene .py Dateien erstellt?")
else:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    print("Erstelle Vektoren...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print(f"Fertig! {len(splits)} Code-Fragmente gespeichert.")