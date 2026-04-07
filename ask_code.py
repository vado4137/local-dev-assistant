from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Setup Datenbank
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 2. Setup Modell
llm = OllamaLLM(model="llama3")

# 3. Das Prompt-Template (Die Instruktion für die KI)
template = """Nutze die folgenden Codestücke, um die Frage am Ende zu beantworten. 
Wenn du die Antwort nicht weißt, sag einfach, dass du es nicht weißt.

Kontext:
{context}

Frage: {question}

Antwort:"""
prompt = ChatPromptTemplate.from_template(template)

# 4. Die Chain (Modern: LCEL)
# Hier bauen wir die Logik wie eine Pipeline zusammen
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 5. Abfrage
frage = "Welche Funktionen sind in meinem Code definiert?"
print(f"Suche nach Antwort für: {frage}...")

antwort = rag_chain.invoke(frage)

print("\n--- KI ANTWORT ---")
print(antwort)