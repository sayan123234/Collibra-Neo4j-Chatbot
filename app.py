import streamlit as st
import logging
import time
from datetime import datetime
from typing import Dict, Any
from src.nl_to_cypher import NLToCypherQuery
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon=Config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': f"# Collibra Assistant {Config.APP_VERSION}\nAI-powered natural language interface for Collibra metadata queries."
    }
)

# Enhanced CSS for better styling with dark theme support
st.markdown("""
<style>
    .stExpander > div:first-child {
        font-weight: bold;
    }
    .metric-container {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(128, 128, 128, 0.3);
    }
    .success-message {
        color: #28a745;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #28a745;
        background-color: rgba(40, 167, 69, 0.1);
    }
    .error-message {
        color: #dc3545;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #dc3545;
        background-color: rgba(220, 53, 69, 0.1);
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
        background-color: rgba(33, 150, 243, 0.1);
    }
    .query-stats {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    /* Fix for dark theme text visibility */
    .stMarkdown {
        color: inherit;
    }
    /* Ensure proper contrast for all text elements */
    div[data-testid="stMarkdownContainer"] {
        color: inherit;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with enhanced tracking
def initialize_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "query_system" not in st.session_state:
        st.session_state.query_system = None
        st.session_state.connection_status = None
        st.session_state.connection_time = None
    
    if "processing_query" not in st.session_state:
        st.session_state.processing_query = False
    
    if "query_stats" not in st.session_state:
        st.session_state.query_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0
        }
    
    if "database_info" not in st.session_state:
        st.session_state.database_info = None

initialize_session_state()

# Enhanced query processing with performance tracking
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_schema():
    """Get cached schema information"""
    if st.session_state.query_system:
        return st.session_state.query_system.get_schema_info()
    return None

def process_query(prompt: str) -> Dict[str, Any]:
    """Process query with enhanced error handling and performance tracking"""
    if not st.session_state.query_system:
        return {"error": "Please initialize connection first!"}
    
    start_time = time.time()
    
    try:
        # Update stats
        st.session_state.query_stats["total_queries"] += 1
        
        # Process the query
        result = st.session_state.query_system.query(prompt)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Update stats based on result
        if "error" in result:
            st.session_state.query_stats["failed_queries"] += 1
        else:
            st.session_state.query_stats["successful_queries"] += 1
        
        # Update average response time
        total_queries = st.session_state.query_stats["total_queries"]
        current_avg = st.session_state.query_stats["avg_response_time"]
        st.session_state.query_stats["avg_response_time"] = (
            (current_avg * (total_queries - 1) + response_time) / total_queries
        )
        
        # Add performance metadata
        result["response_time"] = response_time
        result["timestamp"] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        st.session_state.query_stats["failed_queries"] += 1
        logger.error(f"Unexpected error in process_query: {e}", exc_info=True)
        return {
            "error": f"Unexpected error: {str(e)}",
            "response_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }

def display_query_stats():
    """Display query statistics in sidebar"""
    stats = st.session_state.query_stats
    if stats["total_queries"] > 0:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Queries", stats["total_queries"])
            st.metric("Success Rate", f"{(stats['successful_queries']/stats['total_queries']*100):.1f}%")
        with col2:
            st.metric("Successful", stats["successful_queries"])
            st.metric("Avg Response", f"{stats['avg_response_time']:.2f}s")

# Enhanced sidebar for configuration and controls
with st.sidebar:
    st.title("🔗 Control Panel")
    st.markdown("---")
    
    # Connection Management
    st.subheader("Connection")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔌 Initialize Connection", type="primary", use_container_width=True):
            with st.spinner("Connecting to Neo4j and Groq..."):
                try:
                    start_time = time.time()
                    st.session_state.query_system = NLToCypherQuery()
                    
                    if st.session_state.query_system.test_connection():
                        connection_time = time.time() - start_time
                        st.session_state.connection_status = "✅ Connected"
                        st.session_state.connection_time = connection_time
                        
                        # Get database info
                        st.session_state.database_info = st.session_state.query_system.get_database_info()
                        
                        st.success(f"Connection successful! ({connection_time:.2f}s)")
                    else:
                        st.session_state.connection_status = "❌ Connection Failed"
                        st.error("Connection failed!")
                        
                except Exception as e:
                    st.session_state.connection_status = f"❌ Error: {str(e)}"
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Connection error: {e}", exc_info=True)
    
    with col2:
        if st.button("🔄", help="Refresh Connection"):
            if st.session_state.query_system:
                st.session_state.query_system.graph_service.refresh_schema()
                st.success("Schema refreshed!")
    
    # Display connection status with details
    if st.session_state.connection_status:
        if "Connected" in st.session_state.connection_status:
            st.markdown(f'<div class="success-message">{st.session_state.connection_status}</div>', 
                       unsafe_allow_html=True)
            if st.session_state.connection_time:
                st.caption(f"Connected in {st.session_state.connection_time:.2f}s")
        else:
            st.markdown(f'<div class="error-message">{st.session_state.connection_status}</div>', 
                       unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Database Information
    if st.session_state.database_info and "error" not in st.session_state.database_info:
        st.subheader("📊 Database Info")
        info = st.session_state.database_info
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(Config.SIDEBAR_ASSETS_LABEL, info.get("node_count", "Unknown"))
            st.metric("Relationships", info.get("relationship_count", "Unknown"))
        with col2:
            st.metric(Config.SIDEBAR_ASSET_TYPES_LABEL, len(info.get("node_labels", [])))
            st.metric("Relationship Types", len(info.get("relationship_types", [])))
        
        with st.expander("📋 Schema Details"):
            if info.get("node_labels"):
                st.write(f"**{Config.SIDEBAR_ASSET_TYPES_LABEL}:**")
                st.write(", ".join(info["node_labels"]))
            
            if info.get("relationship_types"):
                st.write("**Relationship Types:**")
                st.write(", ".join(info["relationship_types"]))
        
        st.markdown("---")
    
    # Query Statistics
    if st.session_state.query_stats["total_queries"] > 0:
        st.subheader("📈 Query Stats")
        display_query_stats()
        
        # Cache statistics
        if st.session_state.query_system:
            cache_stats = st.session_state.query_system.get_cache_stats()
            if cache_stats["cached_queries"] > 0:
                st.caption(f"Cached queries: {cache_stats['cached_queries']}")
        
        st.markdown("---")
    
    # Tools and Actions
    st.subheader("🛠️ Tools")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("🧹 Clear Cache", use_container_width=True):
            if st.session_state.query_system:
                st.session_state.query_system.clear_cache()
                st.success("Cache cleared!")
    
    # Advanced schema viewer
    if st.button("📋 View Full Schema", use_container_width=True):
        if st.session_state.query_system:
            with st.spinner("Fetching schema..."):
                try:
                    schema = get_cached_schema()
                    if schema:
                        st.text_area("Graph Schema", value=str(schema), height=300, key="schema_viewer")
                    else:
                        st.warning("No schema available")
                except Exception as e:
                    st.error(f"Error fetching schema: {e}")
                    logger.error(f"Schema fetch error: {e}")
        else:
            st.warning("Please initialize connection first!")
    
    st.markdown("---")
    
    # Help and Information
    with st.expander("ℹ️ Help & Tips"):
        st.markdown("""
        **Sample Questions:**
        - "How many assets are there?"
        - "Who owns the Customer table?"
        - "Show me all data concepts"
        - "What assets are in the Finance domain?"
        - "List all technical stewards"
        
        **Tips:**
        - Be specific in your questions
        - Use proper names for assets
        - Ask about ownership, stewardship, domains
        """)
    
    # Footer with version info
    st.markdown("---")
    st.caption(f"{Config.APP_ICON} Collibra Assistant {Config.APP_VERSION}")
    st.caption("Powered by LangChain & Streamlit")

# Enhanced main chat interface
st.title(f"{Config.APP_ICON} {Config.APP_TITLE}")
st.markdown("*AI-powered natural language interface for your Collibra metadata*")

# Connection status banner
if not st.session_state.query_system:
    st.markdown("""
    <div class="info-box">
        <h4>🚀 Getting Started</h4>
        <p>Initialize the connection using the sidebar to start exploring your Collibra data governance landscape!</p>
        <ul>
            <li>Click "Initialize Connection" in the sidebar</li>
            <li>Wait for the connection to establish</li>
            <li>Start asking questions about your metadata</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
else:
    # Connection established - show quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("🟢 Connected & Ready")
    with col2:
        if st.session_state.database_info and "node_count" in st.session_state.database_info:
            st.info(f"📊 {st.session_state.database_info['node_count']} nodes available")
    with col3:
        if st.session_state.query_stats["total_queries"] > 0:
            success_rate = (st.session_state.query_stats["successful_queries"] / 
                          st.session_state.query_stats["total_queries"] * 100)
            st.info(f"📈 {success_rate:.0f}% success rate")

# Enhanced chat message display
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            # Main response
            st.write(message["content"])
            
            # Performance and metadata info
            if "details" in message:
                details = message["details"]
                
                # Show query performance
                if "response_time" in details:
                    st.markdown(f'<div class="query-stats">⏱️ Response time: {details["response_time"]:.2f}s</div>', 
                               unsafe_allow_html=True)
                
                # Enhanced query details expander
                with st.expander("🔍 Technical Details", expanded=False):
                    # Cypher query with syntax highlighting
                    if "cypher_query" in details and details["cypher_query"]:
                        st.write("**Generated Cypher Query:**")
                        st.code(details["cypher_query"], language="cypher")
                        
                        # Query validation info
                        if "validation" in details and details["validation"]:
                            validation = details["validation"]
                            if validation.get("valid", True):
                                st.success("✅ Query syntax validated")
                            else:
                                st.warning(f"⚠️ Validation warning: {validation.get('message', 'Unknown issue')}")
                    
                    # Raw results with better formatting
                    if "query_results" in details and details["query_results"]:
                        st.write("**Query Results:**")
                        results = details["query_results"]
                        
                        # Show results count
                        st.caption(f"Returned {len(results)} result(s)")
                        
                        # Display results in a more readable format
                        if len(results) <= 10:  # Show all for small result sets
                            st.json(results)
                        else:  # Show sample for large result sets
                            st.json(results[:5])
                            st.caption(f"Showing first 5 of {len(results)} results...")
                    
                    # Timestamp
                    if "timestamp" in details:
                        st.caption(f"Query executed at: {details['timestamp']}")
            
            # Error handling display
            elif "error" in message:
                st.error(f"❌ Error: {message['error']}")
                if "details" in message and "response_time" in message["details"]:
                    st.caption(f"Failed after {message['details']['response_time']:.2f}s")

# Enhanced chat input with suggestions and validation
if not st.session_state.query_system:
    st.chat_input("Please initialize connection first...", disabled=True)
else:
    # Sample questions for new users
    if len(st.session_state.messages) == 0:
        st.markdown("**💡 Try asking:**")
        sample_questions = Config.SAMPLE_QUESTIONS
        
        cols = st.columns(len(sample_questions))
        for i, question in enumerate(sample_questions):
            with cols[i]:
                if st.button(question, key=f"sample_{i}", use_container_width=True):
                    # Add user message to chat
                    st.session_state.messages.append({"role": "user", "content": question})
                    
                    # Process the query immediately
                    with st.chat_message("user"):
                        st.write(question)
                    
                    with st.chat_message("assistant"):
                        with st.spinner("🔍 Processing your question..."):
                            result = process_query(question)
                        
                        if "error" in result:
                            error_msg = f"❌ **Error:** {result['error']}"
                            st.error(error_msg)
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": error_msg,
                                "error": result["error"],
                                "details": {
                                    "response_time": result.get("response_time", 0),
                                    "timestamp": result.get("timestamp", "")
                                }
                            })
                        else:
                            answer = result.get("answer", "No answer generated")
                            st.write(answer)
                            
                            # Show performance info
                            if "response_time" in result:
                                st.markdown(f'<div class="query-stats">⏱️ Response time: {result["response_time"]:.2f}s</div>', 
                                           unsafe_allow_html=True)
                            
                            # Add to session state with all details
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer,
                                "details": {
                                    "cypher_query": result.get("cypher_query", ""),
                                    "query_results": result.get("query_results", []),
                                    "response_time": result.get("response_time", 0),
                                    "timestamp": result.get("timestamp", ""),
                                    "validation": result.get("validation", {})
                                }
                            })
                    
                    st.rerun()
    
    # Main chat input
    if prompt := st.chat_input("Ask me anything about your Collibra metadata..."):
        # Validate input
        if len(prompt.strip()) < 3:
            st.error("Please enter a more detailed question.")
        else:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message immediately
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate response with enhanced UI
            with st.chat_message("assistant"):
                # Create placeholder for dynamic updates
                response_placeholder = st.empty()
                details_placeholder = st.empty()
                
                with response_placeholder:
                    with st.spinner("🔍 Analyzing your question..."):
                        time.sleep(0.5)  # Brief pause for UX
                    
                    with st.spinner("🧠 Generating Cypher query..."):
                        time.sleep(0.5)
                    
                    with st.spinner("⚡ Executing query and processing results..."):
                        result = process_query(prompt)
                
                # Clear placeholders and show final result
                response_placeholder.empty()
                
                if "error" in result:
                    error_msg = f"❌ **Error:** {result['error']}"
                    st.error(error_msg)
                    
                    # Show error details if available
                    if "response_time" in result:
                        st.caption(f"Failed after {result['response_time']:.2f}s")
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg,
                        "error": result["error"],
                        "details": {
                            "response_time": result.get("response_time", 0),
                            "timestamp": result.get("timestamp", "")
                        }
                    })
                else:
                    answer = result.get("answer", "No answer generated")
                    st.write(answer)
                    
                    # Show performance info
                    if "response_time" in result:
                        st.markdown(f'<div class="query-stats">⏱️ Response time: {result["response_time"]:.2f}s</div>', 
                                   unsafe_allow_html=True)
                    
                    # Enhanced query details
                    with st.expander("🔍 Technical Details", expanded=False):
                        if "cypher_query" in result and result["cypher_query"]:
                            st.write("**Generated Cypher Query:**")
                            st.code(result["cypher_query"], language="cypher")
                            
                            # Query validation
                            if "validation" in result and result["validation"]:
                                validation = result["validation"]
                                if validation.get("valid", True):
                                    st.success("✅ Query syntax validated")
                                else:
                                    st.warning(f"⚠️ Validation: {validation.get('message', 'Unknown issue')}")
                        
                        if "query_results" in result and result["query_results"]:
                            st.write("**Query Results:**")
                            results = result["query_results"]
                            st.caption(f"Returned {len(results)} result(s)")
                            
                            if len(results) <= 10:
                                st.json(results)
                            else:
                                st.json(results[:5])
                                st.caption(f"Showing first 5 of {len(results)} results...")
                        
                        if "timestamp" in result:
                            st.caption(f"Query executed at: {result['timestamp']}")
                    
                    # Add to session state with all details
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "details": {
                            "cypher_query": result.get("cypher_query", ""),
                            "query_results": result.get("query_results", []),
                            "response_time": result.get("response_time", 0),
                            "timestamp": result.get("timestamp", ""),
                            "validation": result.get("validation", {})
                        }
                    })

# Enhanced footer with additional information
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"**{Config.APP_ICON} Collibra Assistant {Config.APP_VERSION}**")
    st.caption("AI-powered metadata exploration")

with col2:
    st.markdown("**🛠️ Powered by:**")
    st.caption("LangChain • Streamlit • Neo4j • Groq")

with col3:
    if st.session_state.query_stats["total_queries"] > 0:
        st.markdown("**📊 Session Stats:**")
        st.caption(f"{st.session_state.query_stats['total_queries']} queries • "
                  f"{st.session_state.query_stats['avg_response_time']:.1f}s avg")