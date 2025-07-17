# Collibra Data Governance Assistant

An AI-powered natural language interface for querying Collibra metadata stored in Neo4j. This Streamlit application converts natural language questions into Cypher queries using LangChain and Groq LLM, providing an intuitive way to explore your data governance landscape.

## 🎯 What This Project Does

This application serves as an intelligent bridge between users and their Collibra data governance metadata by:

- **Converting natural language to Cypher queries** using advanced LLM technology
- **Executing queries against Neo4j** containing Collibra metadata
- **Providing conversational responses** with comprehensive conversation history tracking
- **Offering real-time schema exploration** and database statistics
- **Caching queries** for improved performance and user experience
- **Maintaining conversation context** for better follow-up question handling


## 🚀 Key Features

### Core Functionality

- **Natural Language Processing**: Ask questions in plain English about your Collibra assets, stewardship, domains, and relationships
- **Intelligent Query Generation**: Advanced prompt engineering for accurate Cypher query creation
- **Real-time Execution**: Direct query execution against Neo4j with performance monitoring
- **Context-Aware Responses**: Conversation history integration for better follow-up questions
- **Smart Response Formatting**: Enhanced answer generation with proper data governance terminology


### Enhanced User Experience

- **Interactive Chat Interface**: Modern Streamlit-powered conversational UI with enhanced styling
- **Conversation History**: Complete conversation tracking with export functionality
- **Query Transparency**: View generated Cypher queries, execution results, and validation status
- **Performance Metrics**: Response times, success rates, and comprehensive query statistics
- **Quick Action Buttons**: Pre-configured sample questions for common data governance queries
- **Conversation Management**: New chat creation, history export, and conversation context display


### Technical Features

- **Connection Management**: Robust connection handling with detailed diagnostics
- **Schema Caching**: Optimized schema retrieval with refresh capabilities
- **Error Handling**: Comprehensive error reporting and recovery mechanisms
- **Query Validation**: Syntax checking and optimization for generated queries
- **Session Management**: Enhanced session state with conversation metadata tracking
- **Performance Optimization**: Query result pagination and connection pooling


## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :-- | :-- | :-- |
| **Frontend** | [Streamlit](https://streamlit.io/) | Interactive web interface with enhanced styling |
| **LLM Orchestration** | [LangChain](https://www.langchain.com/) | AI workflow management |
| **Language Model** | [Groq](https://groq.com/) | Fast LLM inference |
| **Database** | [Neo4j](https://neo4j.com/) | Graph database for Collibra metadata |
| **Configuration** | Python-dotenv | Environment variable management |
| **Conversation Management** | Custom Implementation | Context-aware conversation tracking |

## 📋 Prerequisites

- **Python 3.8+** with pip package manager
- **Neo4j Database** containing Collibra metadata (local or cloud instance)
- **Groq API Key** for LLM access
- **Environment Variables** configured for database and API connections


## ⚙️ Installation \& Setup

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
2. **Verify Status**: Wait for "✅ Connected" confirmation with enhanced status indicators
3. **Explore Database**: Review database statistics and schema information
4. **Start Conversing**: Use sample questions, quick action buttons, or type your own queries

### New Conversation Features

- **Context-Aware Queries**: Follow-up questions now consider previous conversation context
- **Conversation History**: View your recent interactions in the sidebar
- **Export Conversations**: Download your conversation history as JSON files
- **New Chat Sessions**: Start fresh conversations while maintaining history
- **Quick Actions**: Use pre-configured buttons for common data governance questions


### Sample Questions

- "How many assets are in the database?"
- "Who owns the Customer table?"
- "Show me all data concepts in the Finance domain"
- "List technical stewards for database assets"
- "What are the different asset types available?"
- "Tell me more about the assets we discussed earlier" (context-aware)


### Advanced Features

- **Enhanced Schema Viewer**: Inspect node labels and relationship types with improved formatting
- **Query Cache**: Automatic caching for repeated questions with cache statistics
- **Performance Monitoring**: Track response times, success rates, and conversation metrics
- **Technical Details**: View generated Cypher queries and raw results in expandable sections
- **Conversation Export**: Download complete conversation history with metadata


## 🏗️ Project Structure

```
├── app.py                 # Main Streamlit application with enhanced UI
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation (this file)
├── .env                  # Environment variables (create this)
├── src/
│   ├── __init__.py       # Package initialization
│   ├── config.py         # Configuration management
│   ├── graph_service.py  # Neo4j and LLM service layer with pagination
│   ├── nl_to_cypher.py   # Natural language to Cypher conversion
│   └── prompts.py        # LLM prompt templates
└── example/
    └── example_cypher_query_to_replicate_real_collibra_data.txt
```


## 🔧 Configuration Options

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

- **Data Governance Teams**: Interactive exploration of metadata relationships with conversation history
- **Business Users**: Self-service access to data lineage and ownership information with context-aware assistance
- **Data Stewards**: Monitoring and managing data assets with conversational follow-ups
- **Compliance Teams**: Auditing data governance policies with comprehensive conversation tracking
- **Training \& Documentation**: Export conversation histories for knowledge sharing and training purposes


## 🆕 Latest Updates (Version 2.0)

### New Features

- **Conversational History**: Complete conversation tracking with context-aware responses
- **Enhanced UI**: Modern styling with gradient backgrounds and improved message display
- **Export Functionality**: Download conversation history as JSON files
- **Quick Actions**: Pre-configured buttons for common queries
- **Performance Metrics**: Enhanced statistics tracking and display
- **Session Management**: Improved session state with conversation metadata
- **Context-Aware Processing**: Follow-up questions consider conversation history


### Technical Improvements

- **Query Result Pagination**: Better handling of large result sets
- **Connection Pooling**: Improved Neo4j connection management
- **Enhanced Error Handling**: More robust error reporting and recovery
- **Conversation Management**: Custom ConversationManager class for context tracking
- **Performance Optimization**: Caching and query optimization improvements


### UI Enhancements

- **Status Indicators**: Visual connection status with badges
- **Expandable Details**: Query details in collapsible sections
- **Conversation Controls**: New chat, export, and history management
- **Modern Styling**: Gradient backgrounds and improved visual hierarchy
- **Interactive Elements**: Enhanced buttons and input components


## 🚀 Getting Started Quickly

1. **First Time Setup**: Follow the installation steps above
2. **Quick Test**: Use the "How many assets are there?" quick action button
3. **Explore Features**: Try the conversation history and export functionality
4. **Advanced Usage**: Use follow-up questions to test context-aware responses

## 📊 Performance \& Monitoring

The application now includes comprehensive performance monitoring:

- **Response Time Tracking**: Monitor query execution times
- **Success Rate Metrics**: Track successful vs. failed queries
- **Cache Statistics**: View query caching effectiveness
- **Conversation Metrics**: Track conversation length and interaction patterns


## 🔒 Security \& Privacy

- **Session Isolation**: Each conversation session is isolated
- **Data Privacy**: Conversation history is stored locally during session
- **Connection Security**: Secure Neo4j and Groq API connections
- **Export Control**: Users control their conversation data export

This enhanced version of the Collibra Data Governance Assistant provides a significantly improved user experience with conversation history, context-aware responses, and modern UI design while maintaining all the core functionality for data governance exploration.