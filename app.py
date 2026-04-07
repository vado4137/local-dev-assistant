
import streamlit as st
import requests

# Seite konfigurieren
st.set_page_config(page_title="Local Dev-Assistant", page_icon="🤖")

# --- SIDEBAR FÜR EINSTELLUNGEN ---
with st.sidebar:
    st.header("Einstellungen")
    selected_lang = st.selectbox("Antwortsprache", ["Deutsch", "English"])
    if st.button("Verlauf löschen"):
        st.session_state.messages = []
        st.rerun()

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
