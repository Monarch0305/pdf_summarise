from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings  # ✅ Corrected import
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM  # ✅ Corrected import

import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

UPLOAD_FOLDER = "uploads"
VECTOR_DB_PATH = "faiss_index"  # Persistent FAISS index storage
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Initialize OllamaLLM and HuggingFaceEmbeddings correctly
llm = OllamaLLM(model="llama3")  
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  

# ✅ Load FAISS index safely
vector_store = None
if os.path.exists(VECTOR_DB_PATH):
    vector_store = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)  # ✅ Fix applied

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_store  

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = text_splitter.split_documents(documents)

    # ✅ Generate embeddings for the new PDF
    new_vector_store = FAISS.from_documents(chunks, embeddings)

    if vector_store:
        # ✅ Merge new embeddings with existing FAISS index
        vector_store.merge_from(new_vector_store)
    else:
        vector_store = new_vector_store

    # ✅ Save updated FAISS index
    vector_store.save_local(VECTOR_DB_PATH)

    return {"message": f"Processed {file.filename} successfully"}

@app.post("/chat/")
async def chat_with_pdf(query: str = Form(...)):
    global vector_store

    if not os.path.exists(VECTOR_DB_PATH):
        return {"error": "No documents uploaded yet."}

    # ✅ Always load the latest FAISS index safely
    vector_store = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)

    if not vector_store:
        return {"error": "No vector store found. Please upload a document first."}

    retriever = vector_store.as_retriever()
    rag_chain = RetrievalQA.from_chain_type(llm, retriever=retriever, chain_type="stuff")

    response = rag_chain.run(query)
    return {"answer": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
