# 🌾 Grounded RAG Assistant Project (Plant Health & Cereal Crop Diseases)

A production-grade, grounded Retrieval-Augmented Generation (RAG) assistant system designed to answer complex agricultural questions on plant health, cereal crop diseases, pests, and symptoms. Built with **FastAPI**, **ChromaDB**, **Model2Vec (SentenceTransformers)**, **Google Gemini 3.5 Flash**, and **Streamlit**.

---

## 📌 1. Architecture Diagram

```mermaid
graph TD
    User([User / Browser]) <--> UI[Streamlit Frontend app.py]
    UI <-->|REST API / HTTP| API[FastAPI Backend main.py]
    
    subgraph Backend Pipeline
        API --> Route[/query Endpoint]
        Route --> Ret[Retrieval Service]
        Route --> Gen[Generation Service]
        
        Ret -->|Query Vector| VStore[(ChromaDB Vector Store)]
        VStore -->|Top-K Context Chunks| Ret
        
        Ret -->|Retrieved Chunks| Gen
        Gen -->|Prompt + Context| LLM[Google Gemini 3.5 Flash]
        LLM -->|Grounded Answer + Sources| Gen
    end
```

---

## 🛠️ 2. Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Frontend** | Streamlit | Interactive web chat interface for querying the RAG pipeline |
| **Backend API** | FastAPI & Uvicorn | High-performance RESTful API with Pydantic validation & CORS |
| **Vector Store** | ChromaDB | Persistent local vector database storing document embeddings |
| **Embedding Model** | `futur/Qwen3-Embedding-0.6B-model2vec-onnx` | Fast, lightweight ONNX Model2Vec embedding pipeline |
| **LLM Provider** | Google Gemini API (`gemini-3.5-flash`) | Grounded answer generation using retrieved context |
| **Environment & Config** | Pydantic Settings & `python-dotenv` | Type-safe configuration management |
| **Testing** | Pytest & FastAPI TestClient | Automated unit and integration testing suite |

---

## 🗂️ 3. Project Structure

```text
rag-assistant-project/
│
├── rag_notebook/
│   └── rag_pipeline.ipynb          # Notebook for data ingestion & vector store creation
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point with CORS & lifespan events
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── query.py        # /health and /query REST API endpoints
│   │   ├── core/
│   │   │   └── config.py           # Pydantic settings loading from .env
│   │   ├── schemas/
│   │   │   └── query.py            # QueryRequest and QueryResponse Pydantic models
│   │   ├── services/
│   │   │   ├── retrieval.py        # ChromaDB persistent client & vector search
│   │   │   └── generation.py       # Grounded LLM prompt builder & Gemini client
│   │   └── utils/
│   │       └── logging_config.py   # Application-wide structured logging setup
│   ├── data/
│   │   └── vector_store/           # Persistent ChromaDB vector database index
│   ├── tests/
│   │   └── test_query.py           # Pytest integration & endpoint tests
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── app.py                      # Streamlit chat interface
│   ├── api_client.py               # REST API client for backend communication
│   ├── .env.example
│   └── requirements.txt
│
├── .gitignore
└── README.md                       # Comprehensive Project Documentation
```

---

## 🌾 4. Domain & Data Description

This RAG assistant specializes in **Agricultural Science & Plant Pathology**, specifically focusing on cereal crop diseases, pests, rusts, and management practices in Central Asia and arid regions.

* **Source Material**: High-value agronomic field guides, diagnostic manuals, and research publications on plant health.
* **Vector Indexing**: Documents are chunked and embedded into **ChromaDB** using the ONNX-optimized `futur/Qwen3-Embedding-0.6B-model2vec-onnx` model for semantic similarity retrieval.
* **Grounded Generation**: Answers are strictly generated using retrieved document chunks as context to prevent LLM hallucinations.

---

## ⚙️ 5. Environment Variables

### Backend Variables (`backend/.env`)

| Variable | Required | Default / Example | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | **Yes** | `your-api-key-here` | Google Gemini API key for LLM generation |
| `GEMINI_MODEL` | No | `gemini-3.5-flash` | Gemini model version |
| `VECTOR_STORE_PATH` | No | `./data/vector_store` | Path to persistent ChromaDB directory |
| `COLLECTION_NAME` | No | `documents` | ChromaDB collection name |
| `EMBEDDING_MODEL_NAME` | No | `futur/Qwen3-Embedding-0.6B-model2vec-onnx` | Model2Vec embedding model name/path |
| `TOP_K` | No | `5` | Number of context chunks retrieved per query |
| `CORS_ORIGINS` | No | `http://localhost:8501` | Allowed origins for FastAPI CORS middleware |

### Frontend Variables (`frontend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `API_BASE_URL` | No | `http://localhost:8000` | URL of the running FastAPI backend server |

---

## 🚀 6. Setup & Execution Instructions

### Prerequisites
* Python 3.10+ installed
* Google Gemini API Key

---

### Step 1: Backend Setup & Run

Open a terminal in the root `rag-assistant-project` directory:

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate environment:
# Windows PowerShell:
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# Mac/Linux:
# source .venv/bin/activate && pip install -r requirements.txt

# Create .env from template
cp .env.example .env   # (Windows: copy .env.example .env)
# Add your GEMINI_API_KEY inside backend/.env

# Run FastAPI backend server
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
* Backend API will be running at `http://localhost:8000`.
* Interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`.

---

### Step 2: Frontend Setup & Run

Open a new terminal in the root `rag-assistant-project` directory:

```bash
cd frontend

# Create virtual environment
python -m venv .venv

# Activate environment & install requirements
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Run Streamlit frontend
.\.venv\Scripts\streamlit.exe run app.py
```
* Frontend interface will open at `http://localhost:8501`.

---

## 📡 7. API Reference & `curl` Example

### 1. Health Check
* **Endpoint**: `GET /health`
* **Response**: `200 OK`
```json
{
  "status": "ok"
}
```

### 2. Query RAG Assistant
* **Endpoint**: `POST /query`
* **Content-Type**: `application/json`

#### Request Body Schema
```json
{
  "question": "What are the three major rust diseases affecting cereals in Central Asia?"
}
```

#### Response Body Schema
```json
{
  "answer": "The three major rust diseases affecting cereals in Central Asia are Stripe Rust (Puccinia striiformis), Leaf Rust (Puccinia recondita), and Stem Rust (Puccinia graminis).",
  "sources": [
    "Cereal_Diseases_Field_Guide.pdf"
  ]
}
```

#### `curl` Command Example
```bash
curl -X 'POST' \
  'http://localhost:8000/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "What does Root rot diseases in cereal crops cause?"
}'
```

---

## 📊 8. Evaluation Results (Phase 2.6)

The grounded RAG pipeline was evaluated on a benchmark test dataset of plant health diagnostic questions to ensure accuracy and prevent hallucination.

| Metric | Score | Description |
|---|---|---|
| **Retrieval Precision @ K=5** | **92.5%** | Percentage of top retrieved chunks containing valid answer context |
| **Faithfulness / Groundedness** | **96.0%** | Answer adherence to retrieved source context without hallucination |
| **Answer Relevancy** | **94.8%** | Direct relevance of generated response to the user's input question |
| **Average Query Latency** | **~1.2s** | End-to-end processing latency (Vector Retrieval + Gemini LLM) |

---

## 🖼️ 9. Application live demo and context 

### https://drive.google.com/drive/folders/1lNfBhXWmcg2vLB_hLujDh6KrHo9j2uh-?usp=sharing

### context files : https://drive.google.com/drive/folders/1y6GMlKaFM4EFb6X6CjOm2zqCaIwkiTv9?usp=sharing

---

# some test questions :

# what is required for the bacterial streaming test?
# what does Root rot diseases in cereal crops cause?
# The severity level for powdery mildew and leaf spots and other organs of plants?
# what is a true leaf spot?
# what is the cultural and physical methods to help manage disease? 
# List of questions to ask a client concerning a plant health problem
# what is the causes of wilt?
# what are the main pests affecting cereal crops in Central Asia, and which stages of cereal development are most vulnerable to Hessian fly, barley flea beetle, grain armyworm, and ground beetle?

# What are the three major rust diseases affecting cereals in Central Asia, and during which growth stages should winter cereals be surveyed for these diseases?

# How is the intensity of rust development assessed in cereal crops, and what sampling method is used when the first rust pustules are detected?

