# 🤖 Local Private Dev-Assistant (RAG)

Ein leistungsstarker, lokal laufender KI-Assistent, der deinen eigenen Code versteht. Dieses Projekt nutzt **RAG (Retrieval-Augmented Generation)**, um präzise Antworten auf Basis deiner lokalen Dateien zu geben – ohne dass Daten deine Maschine verlassen.

## 🚀 Features
- **Vollständige Privatsphäre:** Alles läuft lokal via WSL 2 und Ollama.
- **Code-Verständnis:** Indiziert Python-Dateien im `/code` Ordner für kontextbezogene Antworten.
- **Streaming UI:** Echtzeit-Antworten in einem modernen Streamlit-Interface.
- **Mehrsprachig:** Wähle zwischen Deutsch und Englisch für die Antworten.
- **GPU-Beschleunigt:** Nutzt NVIDIA CUDA für blitzschnelle Inferenz.

## 🛠 Architektur
Das Projekt ist in eine moderne Microservice-Struktur unterteilt:
1. **Vector Database:** ChromaDB speichert Code-Embeddings (erstellt mit HuggingFace).
2. **Backend:** FastAPI-Server, der die RAG-Logik und die Kommunikation mit Ollama steuert.
3. **Frontend:** Streamlit-Weboberfläche für ein flüssiges Chat-Erlebnis.

## 📋 Voraussetzungen
- Windows mit **WSL 2** (Ubuntu empfohlen)
- **NVIDIA GPU** + installierte CUDA-Treiber
- **Ollama** in WSL installiert (`ollama run llama3`)
- Python 3.10+

## ⚙️ Installation & Setup

1. **Repository klonen & Umgebung einrichten:**
   ```bash
   git clone https://github.com/vado4137/local-dev-assistant.git
   cd dev-assistant
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt