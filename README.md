# Collibra Neo4j Chatbot

This project is a Streamlit-based chatbot designed to interact with a Collibra knowledge graph stored in a Neo4j database. It leverages Large Language Models (LLMs) via the Groq API and LangChain to translate natural language questions into Cypher queries, execute them against the graph, and return user-friendly answers.

 <!-- It's recommended to add a screenshot of your app here -->

## 🚀 Features

- **Natural Language Interface:** Ask questions about your Collibra metadata in plain English.
- **Dynamic Cypher Generation:** Automatically converts your questions into executable Cypher queries.
- **Interactive Chat:** A familiar chat interface for a seamless user experience, powered by Streamlit.
- **Query Transparency:** View the generated Cypher query and the raw JSON results for each answer.
- **Schema Inspector:** Easily view the Neo4j graph schema directly from the application's sidebar.
- **Connection Management:** Simple controls to initialize the connection to backend services and clear the chat history.

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend/LLM Orchestration:** [LangChain](https://www.langchain.com/)
- **LLM Provider:** [Groq](https://groq.com/)
- **Database:** [Neo4j](https://neo4j.com/)

## 📋 Prerequisites

Before you begin, ensure you have the following:

- Python 3.8+
- Access to a running Neo4j instance containing your Collibra data.
- A Groq API Key.

## ⚙️ Setup and Installation

Follow these steps to get the application running locally.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd Collibra-Neo4j-Chatbot
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Create a `requirements.txt` file in the root of the project with the following content:

```txt
streamlit
langchain
langchain-groq
langchain-neo4j
python-dotenv
```

Then, install the packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a file named `.env` in the root directory of the project. This file will store your secret keys and connection details. Add the following variables, replacing the placeholder values with your actual credentials.

```env
# Neo4j Credentials
NEO4J_URI="bolt://localhost:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your_neo4j_password"
NEO4J_DATABASE="your_neo4j_database_name"

# Groq API Key
GROQ_API_KEY="your_groq_api_key"
GROQ_MODEL_NAME="your_groq_model_name"
```

**Note:** The `src/nl_to_cypher.py` file must be updated to load these environment variables (e.g., using `load_dotenv()` from the `dotenv` package).

## ▶️ Running the Application

Once the setup is complete, you can run the Streamlit application with the following command:

```bash
streamlit run app.py
```

The application will open in your default web browser.

## 📖 Usage

1.  Open the application in your browser.
2.  In the sidebar, click the **🔌 Initialize Connection** button to connect to Neo4j and Groq.
3.  Wait for the "✅ Connected" status to appear.
4.  (Optional) Click **📋 View Graph Schema** to inspect the database schema.
5.  Start asking questions about your Collibra graph in the chat input at the bottom of the page.