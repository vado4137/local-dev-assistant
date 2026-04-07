
import streamlit as st
import requests
from ingest import ingest_web_docs, process_web_url, get_vectorstore, ingest_recursive_web
# web_ingest.py importieren falls du die Funktion dort behalten willst:
from web_ingest import ingest_entire_documentation 

st.set_page_config(page_title="Local Dev-Assistant", page_icon="🤖")

# Vector Store initialisieren, damit er in allen Funktionen verfügbar ist
if "vector_store" not in st.session_state:
    st.session_state.vector_store = get_vectorstore()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Einstellungen")
    selected_lang = st.selectbox("Antwortsprache", ["Deutsch", "English"])
    if st.button("Verlauf löschen"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.header("🌐 Wissensquellen")

    # Modus wählen: Einzelne Seite oder ganze Doku
    mode = st.radio("Modus", ["Einzelne URL", "Ganze Dokumentation (Sitemap)"])

    if mode == "Einzelne URL":
        web_url = st.text_input("URL eingeben", placeholder="https://pytorch.org/docs/...")
        if st.button("Seite indizieren"):
            with st.spinner("Lade Seite..."):
                num_chunks = process_web_url(web_url, st.session_state.vector_store)
                st.success(f"{num_chunks} Blöcke hinzugefügt!")

    else:
        doc_options = {
            "PyTorch": "https://pytorch.org/docs/stable/sitemap.xml",
            "Python": "https://devguide.python.org/sitemap.xml", # Korrigiert: Anführungszeichen gesetzt
            "TensorFlow": "https://www.tensorflow.org/sitemap_0_of_1.xml",
            "Custom": ""
        }
        selection = st.selectbox("Wähle Doku", list(doc_options.keys()))
        sitemap_input = st.text_input("Sitemap URL") if selection == "Custom" else doc_options[selection]
        
        if st.button("Doku indizieren"):
            with st.status("Indiziere Web-Daten...", expanded=True) as status:
                pages, chunks = ingest_web_docs(sitemap_input, st.session_state.vector_store)
                if chunks > 0:
                    status.update(label="Fertig!", state="complete")
                    st.success(f"{pages} Seiten ({chunks} Fragmente) gelernt!")
                else:
                    status.update(label="Fehlgeschlagen", state="error")
                    st.error("Es konnten keine Inhalte extrahiert werden. Prüfe die URL oder die Sitemap.")
st.sidebar.header("🌐 Web-Crawler (Ohne Sitemap)")
target_url = st.sidebar.text_input("Start-URL der Doku", placeholder="https://docs.python.org/3/library/")
crawl_depth = st.sidebar.slider("Tiefe (Links folgen)", 1, 3, 2)

if st.sidebar.button("Doku scannen"):
    with st.sidebar.status("Crawler läuft...") as status:
        pages, chunks = ingest_recursive_web(target_url, st.session_state.vector_store, depth=crawl_depth)
        st.sidebar.success(f"{pages} Seiten gefunden und gesäubert!")                   

st.title("🤖 Dein Local Dev-Assistant")
st.markdown("Frage mich etwas über deinen Code im `/code`-Ordner.")

# Initialisierung des Chat-Verlaufs
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat-Verlauf anzeigen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Benutzereingabe
if prompt := st.chat_input("Wie kann ich dir helfen?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Wir nutzen einen Platzhalter für das Streaming
        response_placeholder = st.empty()
        
        try:
            # WICHTIG: stream=True beim Request setzen
            res = requests.post(
                "http://localhost:8000/ask",
                json={"question": prompt, "language": selected_lang},
                stream=True 
            )

            if res.status_code == 200:
                full_response = ""
                # Wir lesen die Antwort Stück für Stück
                for chunk in res.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_response += chunk
                        # Update den Text in Echtzeit
                        response_placeholder.markdown(full_response + "▌")
                
                # Finalen Text ohne Cursor setzen
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error("Fehler in der API-Antwort.")
        except Exception as e:
            st.error(f"Verbindung zum Backend fehlgeschlagen: {e}")
            
            
if st.sidebar.button("Lokalen Code (/code) neu einlesen"):
    with st.sidebar.spinner("Lese lokale Dateien..."):
        from ingest import ingest_local_code
        result = ingest_local_code()
        st.sidebar.success(result)

