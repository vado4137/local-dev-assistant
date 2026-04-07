from langchain_community.document_loaders import SitemapLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def ingest_entire_documentation(sitemap_url, vector_store):
    """
    Lädt eine komplette Dokumentation via Sitemap und speichert sie im Vector Store.
    Beispiel Sitemap: https://pytorch.org/docs/stable/sitemap.xml
    """
    
    # Der SitemapLoader lädt alle URLs, die er in der XML findet
    loader = SitemapLoader(
        web_path=sitemap_url,
        # Optional: Mit filter_urls kannst du bestimmte Bereiche ausschließen
        # filter_urls=["https://pytorch.org/docs/stable/generated/"]
    )
    
    # Daten laden (das kann je nach Größe der Doku ein paar Minuten dauern)
    docs = loader.load()
    
    # Splitting: Große Doku-Seiten in verdaubare Häppchen teilen
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, 
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(docs)
    
    # In deinen bestehenden ChromaDB Vector Store einfügen
    vector_store.add_documents(chunks)
    
    return len(docs), len(chunks)