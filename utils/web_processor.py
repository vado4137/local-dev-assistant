from langchain_community.document_loaders import SitemapLoader, RecursiveUrlLoader
from bs4 import BeautifulSoup


def docs_extractor(html_input) -> str:
    """Extrahiert Text und stellt sicher, dass er nicht leer ist."""
    # Falls der Input noch kein BeautifulSoup-Objekt ist, erstelle eines
    if isinstance(html_input, str):
        soup = BeautifulSoup(html_input, "html.parser")
    else:
        soup = html_input

    # Suche nach Inhalten
    content = (
        soup.find("article", role="main") or 
        soup.find("div", {"class": "pytorch-article"}) or
        soup.find("main")
    )
    
    # WICHTIG: Prüfen, ob 'content' ein gültiges Tag-Objekt ist
    if content and hasattr(content, "find_all"):
        # Entferne unnötige Elemente
        for junk in content.find_all(["nav", "footer", "script", "style", "aside"]):
            junk.decompose()
        extracted_text = content.get_text(separator="\n", strip=True)
        if extracted_text:
            return extracted_text
    
    # Fallback: Wenn kein Container gefunden wurde, nimm den Body
    body = soup.find("body")
    if body and hasattr(body, "get_text"):
        return body.get_text(separator="\n", strip=True)
        
    return soup.get_text(separator="\n", strip=True) if hasattr(soup, "get_text") else ""

def get_recursive_loader(url, max_depth=2):
    """Konfiguriert den Crawler ohne 'requests_kwargs'."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    return RecursiveUrlLoader(
        url=url,
        max_depth=max_depth,
        extractor=docs_extractor,
        prevent_outside=True,
        use_async=False,
        timeout=10,
        headers=headers 
    )

def get_sitemap_loader(sitemap_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }
    
    return SitemapLoader(
        web_path=sitemap_url,
        parsing_function=docs_extractor,
        continue_on_failure=True,
        requests_per_second=1, # Zwingend langsam bei PyTorch
        requests_kwargs={
            "headers": headers,
            "timeout": 60,
            "verify": False # Ignoriert potenzielle SSL-Probleme beim Scrapen
        }
    )