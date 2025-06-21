import streamlit as st
from src.nl_to_cypher import NLToCypherQuery
import time

# Page configuration
st.set_page_config(
    page_title="Collibra Assistant",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS for basic styling
st.markdown("""
<style>
    .stExpander > div:first-child {
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_system" not in st.session_state:
    st.session_state.query_system = None
    st.session_state.connection_status = None

if "processing_query" not in st.session_state:
    st.session_state.processing_query = False

# Function to process query
def process_query(prompt):
    if not st.session_state.query_system:
        return {"error": "Please initialize connection first!"}
    
    try:
        result = st.session_state.query_system.query(prompt)
        return result
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

# Sidebar for configuration and controls
with st.sidebar:
    st.title("Settings")
    st.markdown("---")
    
    # Connection status
    if st.button("🔌 Initialize Connection", type="primary"):
        with st.spinner("Connecting to Neo4j and Groq..."):
            try:
                st.session_state.query_system = NLToCypherQuery()
                if st.session_state.query_system.test_connection():
                    st.session_state.connection_status = "✅ Connected"
                    st.success("Connection successful!")
                else:
                    st.session_state.connection_status = "❌ Connection Failed"
                    st.error("Connection failed!")
            except Exception as e:
                st.session_state.connection_status = f"❌ Error: {str(e)}"
                st.error(f"Error: {str(e)}")
    
    # Display connection status
    if st.session_state.connection_status:
        st.write(f"**Status:** {st.session_state.connection_status}")
    
    st.markdown("---")
    
    # Schema viewer
    if st.button("📋 View Graph Schema"):
        if st.session_state.query_system:
            with st.spinner("Fetching schema..."):
                try:
                    schema = st.session_state.query_system.get_schema_info()
                    st.text_area("Graph Schema", value=str(schema), height=200)
                except Exception as e:
                    st.error(f"Error fetching schema: {e}")
        else:
            st.warning("Please initialize connection first!")
    
    st.markdown("---")
    
    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")

# Main chat interface
st.title("🔗 Sayan's Personal Assistant for Collibra")

# Check if connection is established
if not st.session_state.query_system:
    st.info("👈 Please initialize the connection using the sidebar to start chatting!")
else:
    st.success("Ready to chat! Ask questions about your own Collibra landscape.")

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])
            
            # Show additional details if available
            if "details" in message:
                with st.expander("🔍 Query Details"):
                    if "cypher_query" in message["details"] and message["details"]["cypher_query"]:
                        st.write("**Generated Cypher Query:**")
                        st.code(message["details"]["cypher_query"], language="cypher")
                    
                    if "query_results" in message["details"] and message["details"]["query_results"]:
                        st.write("**Raw Query Results:**")
                        st.json(message["details"]["query_results"])

# Chat input
if prompt := st.chat_input("Ask me anything about your DGC instance's metadata"):
    if not st.session_state.query_system:
        st.error("Please initialize the connection first!")
    else:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Generating Cypher query and fetching results..."):
                result = process_query(prompt)
                
                if "error" in result:
                    error_msg = f"❌ **Error:** {result['error']}"
                    st.write(error_msg)
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
                else:
                    answer = result.get("answer", "No answer generated")
                    st.write(answer)
                    
                    # Show query details in expander
                    with st.expander("🔍 Query Details"):
                        if "cypher_query" in result and result["cypher_query"]:
                            st.write("**Generated Cypher Query:**")
                            st.code(result["cypher_query"], language="cypher")
                        
                        if "query_results" in result and result["query_results"]:
                            st.write("**Raw Query Results:**")
                            st.json(result["query_results"])
                    
                    # Add to session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "details": {
                            "cypher_query": result.get("cypher_query", ""),
                            "query_results": result.get("query_results", [])
                        }
                    })

# Footer
st.markdown("---")
st.markdown("🔗 Collibra Chatbot | Powered by LangChain", 
           help="This assistant converts natural language to help you query your Collibra's instance metadata knowledge graph")