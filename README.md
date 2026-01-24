# Collibra Data Governance Assistant

An AI-powered natural language interface for querying Collibra metadata stored in Neo4j. This application converts natural language questions into Cypher queries using LangChain and Groq LLM, providing an intuitive way to explore your data governance landscape.

> **Note:** This project has been refactored into a modern decoupled architecture with a **FastAPI** backend and a **React + Tailwind** frontend.

## 🎯 What This Project Does

This application serves as an intelligent bridge between users and their Collibra data governance metadata by:

- **Converting natural language to Cypher queries** using advanced LLM technology.
- **Visualizing Data Lineage** with an interactive, hierarchical graph view.
- **Executing queries against Neo4j** containing Collibra metadata.
- **Providing conversational responses** with comprehensive conversation history tracking.

## 🚀 Key Features

### Core Capabilities

- **Natural Language Processing**: Ask questions in plain English about your Collibra assets, stewardship, domains, and relationships.
- **Interactive Lineage Graph**: Explore data dependencies with a structured **React Flow** visualization (Left-to-Right layout).
- **Intelligent Query Generation**: Advanced prompt engineering for accurate Cypher query creation.
- **Node Details Side Panel**: Click on any node in the lineage view to see full properties and metadata.

### Enhanced User Experience

- **Responsive Chat Interface**: Modern React-powered UI with optimistic updates.
- **Dark Mode Support**: Toggle between Light and Dark themes (auto-detects system preference).
- **Query Transparency**: View generated Cypher queries and execution results used by the AI.
- **Performance Metrics**: Response times and result counts.

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :-- | :-- | :-- |
| **Frontend** | [React](https://react.dev/) + [Tailwind CSS v4](https://tailwindcss.com/) | Modern, responsive web interface |
| **Visualization** | [React Flow](https://reactflow.dev/) + Dagre | Hierarchical graph layout and interaction |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance REST API |
| **LLM Orchestration** | [LangChain](https://www.langchain.com/) | AI workflow management |
| **Language Model** | [Groq](https://groq.com/) | Fast LLM inference (`llama-3.3-70b-versatile`) |
| **Database** | [Neo4j](https://neo4j.com/) | Graph database for Collibra metadata |

## 📋 Prerequisites

- **Python 3.10+** (Backend)
- **Node.js 20+** (Frontend)
- **Neo4j Database** containing Collibra metadata.
- **Groq API Key** for LLM access.

## ⚙️ Installation & Setup

### 1. Backend Setup (FastAPI)

The backend handles the connection to Neo4j and Groq (LLM).

```powershell
# In the root directory
# Install dependencies (using uv)
uv sync

# Run the server
uv run uvicorn backend.app.main:app --reload
```

*The backend will start at `http://localhost:8000`*

### 2. Frontend Setup (React)

The frontend provides the chat and visualization interface.

```powershell
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

*The frontend will start at `http://localhost:5173`*

## 🔧 Configuration

Ensure your `.env` file in the project root contains the necessary credentials:

```env
# Neo4j Configuration
NEO4J_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# Groq Configuration
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_NAME=llama-3.3-70b-versatile

# Performance Settings
MAX_QUERY_RESULTS=100
QUERY_TIMEOUT=30
```

## 🏗️ Project Structure

```text
├── backend/               # FastAPI Backend
│   ├── app/
│   │   ├── api/          # API Endpoints (/chat, /lineage)
│   │   ├── core/         # Configuration & Settings
│   │   └── services/     # Logic (GraphService, ChatService)
├── frontend/             # React Frontend
│   ├── src/
│   │   ├── components/   # Chat, LineageView, CustomNode
│   │   └── api/          # API Client
├── .env                  # Environment Variables
└── pyproject.toml        # Python Dependencies
```

## 📖 Usage Guide

1. **Start Components**: Run both Backend and Frontend.
2. **Access UI**: Open `http://localhost:5173`.
3. **Chat**: Ask questions like "Show me the lineage of Customer Data."
4. **Lineage View**: Switch to the **Lineage Tab** (Share Icon) to visualize relationships.
    - **Click Nodes**: View details in the side panel.
    - **Auto Layout**: Use the wand icon to re-organize the graph.
5. **Dark Mode**: Use the moon/sun icon in the sidebar to toggle themes.
