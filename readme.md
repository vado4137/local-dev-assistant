# 🤖 Local Private Dev-Assistant (RAG)

Ein leistungsstarker, lokal laufender KI-Assistent, der deinen eigenen Code und Online-Dokumentationen versteht. Dieses Projekt nutzt **RAG (Retrieval-Augmented Generation)**, um präzise Antworten auf Basis deiner lokalen Dateien und Web-Ressourcen zu geben – ohne dass Daten deine Maschine verlassen.

## 🚀 Features

- **Vollständige Privatsphäre:** Alles läuft lokal via WSL 2 und Ollama. Keine Cloud-Abhängigkeiten für die Inferenz.
- **Smart Sitemap Ingest:** Automatische Erkennung und Auflösung von verschachtelten Sitemap-Indizes (optimiert für komplexe Strukturen wie bei PyTorch oder TensorFlow).
- **Automatischer Crawler-Fallback:** Intelligenter Mechanismus, der bei blockierten Sitemaps automatisch auf rekursives Web-Crawling umschaltet.
- **Code-Verständnis:** Indiziert Python-Dateien im `/code` Ordner für kontextbezogene Antworten zu deinen Projekten.
- **Persistent Vector Storage:** Nutzt ChromaDB zur lokalen Speicherung von Embeddings inklusive Batch-Processing für große Dokumentationsmengen.
- **Streaming UI:** Modernes Streamlit-Interface mit Echtzeit-Antworten und Sprachauswahl (DE/EN).
- **GPU-Beschleunigt:** Optimiert für NVIDIA CUDA unter WSL 2 für blitzschnelle Antwortzeiten.

## 🛠 Architektur

Das Projekt folgt einer modernen RAG-Pipeline:
1. **Vector Database:** ChromaDB verwaltet Embeddings via HuggingFace (`all-MiniLM-L6-v2`).
2. **Smart Ingest Logic:** Eine mehrstufige Logik sorgt dafür, dass Web-Inhalte auch bei schwierigen Server-Konfigurationen geladen werden.
3. **LLM-Backend:** Kommunikation mit Ollama (z. B. Llama 3) für die generative Beantwortung.
4. **Frontend:** Streamlit als interaktive Schaltzentrale für Ingest und Chat.

## 📋 Voraussetzungen

- **OS:** Windows mit **WSL 2** (Ubuntu empfohlen).
- **Hardware:** NVIDIA GPU + installierte CUDA-Treiber für WSL.
- **Software:** - **Ollama** in WSL installiert (`ollama serve`).
  - **Python 3.10+**.

## ⚙️ Installation & Setup

1. **Repository klonen:**
   ```bash
   git clone [https://github.com/vado4137/local-dev-assistant.git](https://github.com/vado4137/local-dev-assistant.git)
   cd local-dev-assistant```
2. **Virtuelle Umgebung erstellen & aktivieren:**
```Bash

python3 -m venv venv
source venv/bin/activate```

3. ***Abhängigkeiten installieren:***
```Bash

pip install -r requirements.txt```

4. ***Ollama Modell vorbereiten:**
Stelle sicher, dass Ollama läuft und lade das gewünschte Modell:
```Bash

ollama run llama3```

5. *** fastapi Backend starten:
```bash
uvicorn api:app --reload
```
6. ***Streamlit Frontend starten:***
```Bash

streamlit run app.py```

##🧠 Smart-Ingest Logik (Automatisierung)

Um auch restriktive Dokumentationen (wie z. B. PyTorch) erfolgreich einzulesen, durchläuft das System automatisch folgende Eskalationsstufen:

    - **Sitemap-Scan:** Versuch, die sitemap.xml direkt zu parsen.

    - **Index-Auflösung:** Falls die Sitemap ein Index ist, werden verschachtelte Strukturen automatisch aufgelöst.

    - **Recursive Crawler:** Falls XML-Anfragen blockiert werden (z. B. durch Botschutz), schaltet das System auf HTML-Crawling um und folgt den Links auf der Webseite bis zur gewünschten Tiefe.

##📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.