# Collibra Data Governance Assistant

An AI-powered natural language interface for querying Collibra metadata stored in Neo4j. This Streamlit application converts natural language questions into Cypher queries using LangChain and Groq LLM, providing an intuitive way to explore your data governance landscape.

## 🎯 What This Project Does

This application serves as an intelligent bridge between users and their Collibra data governance metadata by:

- **Converting natural language to Cypher queries** using advanced LLM technology
- **Executing queries against Neo4j** containing Collibra metadata
- **Providing conversational responses** with technical details and performance metrics
- **Offering real-time schema exploration** and database statistics
- **Caching queries** for improved performance and user experience

## 🚀 Key Features

### Core Functionality
- **Natural Language Processing**: Ask questions in plain English about your Collibra assets, stewardship, domains, and relationships
- **Intelligent Query Generation**: Advanced prompt engineering for accurate Cypher query creation
- **Real-time Execution**: Direct query execution against Neo4j with performance monitoring
- **Smart Response Formatting**: Context-aware answer generation with proper data governance terminology

### User Experience
- **Interactive Chat Interface**: Streamlit-powered conversational UI with message history
- **Query Transparency**: View generated Cypher queries, execution results, and validation status
- **Performance Metrics**: Response times, success rates, and query statistics
- **Sample Questions**: Quick-start buttons for common data governance queries

### Technical Features
- **Connection Management**: Robust connection handling with detailed diagnostics
- **Schema Caching**: Optimized schema retrieval with refresh capabilities
- **Error Handling**: Comprehensive error reporting and recovery mechanisms
- **Query Validation**: Syntax checking and optimization for generated queries

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | [Streamlit](https://streamlit.io/) | Interactive web interface |
| **LLM Orchestration** | [LangChain](https://www.langchain.com/) | AI workflow management |
| **Language Model** | [Groq](https://groq.com/) | Fast LLM inference |
| **Database** | [Neo4j](https://neo4j.com/) | Graph database for Collibra metadata |
| **Configuration** | Python-dotenv | Environment variable management |

## 📋 Prerequisites

- **Python 3.8+** with pip package manager
- **Neo4j Database** containing Collibra metadata (local or cloud instance)
- **Groq API Key** for LLM access
- **Environment Variables** configured for database and API connections

## ⚙️ Installation & Setup

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd collibra-assistant
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:

```env
# Neo4j Configuration
NEO4J_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# Groq Configuration
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_NAME=llama3-70b-8192

# Optional Performance Settings
MAX_QUERY_RESULTS=100
QUERY_TIMEOUT=30

# Optional UI Customization
APP_TITLE=Collibra Data Governance Assistant
APP_ICON=🔗
APP_VERSION=v2.0
SIDEBAR_ASSETS_LABEL=Assets
SIDEBAR_ASSET_TYPES_LABEL=Asset Types
```

## 🚀 Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Getting Started
1. **Initialize Connection**: Click "🔌 Initialize Connection" in the sidebar
2. **Verify Status**: Wait for "✅ Connected" confirmation
3. **Explore Database**: Review database statistics and schema information
4. **Start Querying**: Use sample questions or type your own

### Sample Questions
- "How many assets are in the database?"
- "Who owns the Customer table?"
- "Show me all data concepts in the Finance domain"
- "List technical stewards for database assets"
- "What are the different asset types available?"

### Advanced Features
- **Schema Viewer**: Inspect node labels and relationship types
- **Query Cache**: Automatic caching for repeated questions
- **Performance Monitoring**: Track response times and success rates
- **Technical Details**: View generated Cypher queries and raw results

## 🏗️ Project Structure

```
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .env                  # Environment variables (create this)
├── src/
│   ├── __init__.py       # Package initialization
│   ├── config.py         # Configuration management
│   ├── graph_service.py  # Neo4j and LLM service layer
│   ├── nl_to_cypher.py   # Natural language to Cypher conversion
│   └── prompts.py        # LLM prompt templates
└── example/
    └── example_cypher_query_to_replicate_real_collibra_data.txt
```

## 🔧 Configuration Options

The application supports various configuration options through environment variables:

### Performance Settings
- `MAX_QUERY_RESULTS`: Limit query result size (default: 100)
- `QUERY_TIMEOUT`: Database query timeout in seconds (default: 30)
- `GROQ_MODEL_NAME`: Groq model selection (default: llama3-70b-8192)

### UI Customization
- `APP_TITLE`: Application title (default: "Collibra Data Governance Assistant")
- `APP_ICON`: Application icon (default: "🔗")
- `APP_VERSION`: Version display (default: "v2.0")
- `SIDEBAR_ASSETS_LABEL`: Label for assets count (default: "Assets")
- `SIDEBAR_ASSET_TYPES_LABEL`: Label for asset types count (default: "Asset Types")

## 🎯 Use Cases

This application is ideal for:

- **Data Governance Teams**: Quick exploration of metadata relationships
- **Business Users**: Self-service access to data lineage and ownership information
- **Data Stewards**: Monitoring and managing data assets and responsibilities
- **Compliance Teams**: Auditing data governance policies and implementations