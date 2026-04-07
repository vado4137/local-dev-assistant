from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from fastapi.responses import StreamingResponse

# 1. Initialisierung (beim Start des Servers)
app = FastAPI(title="AI Dev-Assistant API")

print("Lade KI-Komponenten...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
llm = OllamaLLM(model="llama3")

template = """Nutze den Kontext, um die Frage zu beantworten.
Kontext: {context}
Frage: {question}
Antwort:"""
prompt = ChatPromptTemplate.from_template(template)

# Die Chain
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 2. Datenmodell für die Anfrage
class Query(BaseModel):
    question: str
    language: str = "Deutsch"  # Standardmäßig Deutsch

# 3. Die Endpunkte (Routes)
@app.get("/")
def read_root():
    return {"status": "Assistant API is running"}

@app.post("/ask")
async def ask_assistant(query: Query):
    try:
        system_instruction = f"Antworte strikt auf {query.language}."
        dynamic_template = f"{system_instruction}\n\nKontext: {{context}}\nFrage: {{question}}\nAntwort:"
        prompt = ChatPromptTemplate.from_template(dynamic_template)
        
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        # Generator-Funktion für das Streaming
        def stream_generator():
            for chunk in chain.stream(query.question):
                # Wir schicken den Text direkt als Chunk raus
                yield chunk

        return StreamingResponse(stream_generator(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))