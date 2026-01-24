# Collibra Data Governance Assistant

An AI-powered natural language interface for querying Collibra metadata stored in Neo4j. This application uses **Hybrid RAG** (Retrieval-Augmented Generation) combining vector embeddings with Cypher queries for intelligent, context-aware responses.

> **Architecture**: FastAPI backend + React/Tailwind frontend with Neo4j vector search.

## 🏛️ Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    React + Tailwind + React Flow                │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Router    │  │  Embedding  │  │      Chat Service       │  │
│  │  (Classify) │  │   Service   │  │   (Hybrid RAG Logic)    │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                      │                │
│         ▼                ▼                      ▼                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Graph Service                          │   │
│  │         Neo4j Connection + Vector Search                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Neo4j Database                          │
│           Collibra Metadata + Vector Embeddings                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Key Features

### Hybrid RAG (Semantic + Structured)

- **Vector Search**: Semantic similarity using sentence-transformers embeddings
- **Text-to-Cypher**: Structured queries for factual/relational questions
- **Combined Context**: LLM uses both sources for richer answers

### Interactive Traceability Graph

- **Collibra-style visualization** with React Flow
- **Path highlighting** on hover/click
- **MiniMap navigation** and legends
- **Details panel** with full node metadata

### Smart Chat

- **Intelligent routing**: Distinguishes greetings from database queries
- **Conversation history**: Context-aware follow-up questions
- **Production mode**: Hide Cypher queries from responses

## 🛠️ Technology Stack

| Component | Technology |
|:--|:--|
| **Frontend** | React 18 + Tailwind CSS v4 + React Flow |
| **Backend** | FastAPI + Pydantic |
| **LLM** | Groq (`llama-3.3-70b-versatile`) |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) |
| **Database** | Neo4j 5.x with native vector indexes |

## ⚙️ Installation

### 1. Clone & Install Dependencies

```powershell
# Install Python dependencies
uv sync

# Install Frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Configure Environment

Create `.env` in the project root:

```env
# Neo4j
NEO4J_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# Groq LLM
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_NAME=llama-3.3-70b-versatile

# Application
DEBUG_MODE=true          # Set false in production to hide Cypher
MAX_QUERY_RESULTS=100
QUERY_TIMEOUT=30

# Vector Search
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_INDEX_NAME=asset_embeddings
VECTOR_DIMENSION=384
VECTOR_TOP_K=5
```

### 3. Setup Vector Index (One-time)

Generate embeddings for all nodes in Neo4j:

```powershell
uv run python -m backend.scripts.setup_vector_index
```

### 4. Run the Application

```powershell
# Terminal 1: Backend
uv run uvicorn backend.app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

Open `http://localhost:5173`

## 📡 API Endpoints

| Endpoint | Method | Description |
|:--|:--|:--|
| `/api/v1/chat` | POST | Send a question, get Hybrid RAG response |
| `/api/v1/lineage` | GET | Get all nodes/edges for graph visualization |
| `/api/v1/schema` | GET | Get Neo4j graph schema |
| `/api/v1/admin/reindex` | POST | Trigger embedding re-indexing |
| `/api/v1/admin/index-status` | GET | Check vector index coverage |
| `/health` | GET | Health check |

### Incremental Indexing

When new data is added to Neo4j:

```powershell
# CLI (only new nodes)
uv run python -m backend.scripts.setup_vector_index --incremental

# Or via API
curl -X POST http://localhost:8000/api/v1/admin/reindex \
  -H "Content-Type: application/json" \
  -d '{"incremental": true}'
```

## 🏗️ Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # chat, lineage, admin
│   │   ├── core/               # config settings
│   │   └── services/           # graph, chat, embedding
│   └── scripts/                # setup_vector_index.py
├── frontend/
│   └── src/
│       ├── components/         # ChatInterface, LineageView
│       └── api/                # client.js
├── .env
├── pyproject.toml
└── README.md
```

## 📖 Usage Examples

| Query Type | Example |
|:--|:--|
| **Factual** | "How many tables are in the Enterprise domain?" |
| **Semantic** | "Find assets related to GDPR compliance" |
| **Relational** | "Who owns the Customer Data Platform?" |
| **Follow-up** | "What else does Bob own?" |

## 🔒 Production Deployment

1. Set `DEBUG_MODE=false` in `.env` to hide Cypher queries
2. Run vector indexing: `uv run python -m backend.scripts.setup_vector_index`
3. Use a production ASGI server: `uvicorn backend.app.main:app --host 0.0.0.0`
