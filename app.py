import streamlit as st
import logging
import time
from datetime import datetime
from typing import Dict, Any
from src.nl_to_cypher import NLToCypherQuery
from src.config import Config
import json
import random

class ConversationManager:
    """Enhanced conversation management with context tracking"""

    def __init__(self):
        self.history = []
        self.context = {}

    def add_interaction(
        self, user_input: str, assistant_response: dict, context: dict = None
    ):
        """Add interaction to conversation history"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "assistant_response": assistant_response,
            "context": context or {},
            "session_id": st.session_state.current_conversation_id,
        }

        self.history.append(interaction)
        self._update_context(user_input, assistant_response)

        # Limit history size for performance
        if len(self.history) > 100:
            self.history = self.history[-100:]

    def _update_context(self, user_input: str, response: dict):
        """Update conversation context for better follow-up questions"""
        if "query_results" in response:
            results = response["query_results"]
            if results:
                # Store recent entities for context
                self.context["recent_entities"] = results[-10:]  # Keep last 10

        # Track query patterns
        if "cypher_query" in response:
            self.context["last_query_type"] = response["cypher_query"]

    def get_conversation_context(self) -> str:
        """Get formatted conversation context for LLM"""
        if not self.history:
            return ""

        recent_interactions = self.history[-3:]  # Last 3 interactions
        context_parts = []

        for interaction in recent_interactions:
            context_parts.append(f"User: {interaction['user_input']}")
            if "answer" in interaction["assistant_response"]:
                context_parts.append(
                    f"Assistant: {interaction['assistant_response']['answer']}"
                )

        return "\n".join(context_parts)

    def export_conversation(self) -> dict:
        """Export conversation for download"""
        return {
            "conversation_id": st.session_state.current_conversation_id,
            "exported_at": datetime.now().isoformat(),
            "total_interactions": len(self.history),
            "history": self.history,
            "context": self.context,
        }


def display_message(message, is_user=False):
    """Enhanced message display with better formatting"""
    message_class = "user-message" if is_user else "assistant-message"
    role = "You" if is_user else "Assistant"

    st.markdown(
        f"""
    <div class="chat-message {message_class}">
        <strong>{role}:</strong><br>
        {message}
    </div>
    """,
        unsafe_allow_html=True,
    )


def display_query_result(result):
    """Enhanced query result display"""
    if "error" in result:
        st.error(f"Error: {result['error']}")
        return

    with st.expander("🔍 Query Details", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.code(result.get("cypher_query", ""), language="cypher")

        with col2:
            if "response_time" in result:
                st.metric("Response Time", f"{result['response_time']:.2f}s")
            if "query_results" in result:
                st.metric("Results Count", len(result["query_results"]))


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
        "Get Help": "https://github.com/your-repo",
        "Report a bug": "https://github.com/your-repo/issues",
        "About": f"# Collibra Assistant {Config.APP_VERSION}\nAI-powered natural language interface for Collibra metadata queries.",
    },
)

# Enhanced CSS for better styling with dark theme support
# Enhanced CSS with modern design system
st.markdown(
    """
<style>
    /* Main container styling */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #0066cc;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left-color: #667eea;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-left-color: #f093fb;
    }
    
    /* Sidebar enhancements */
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* Status indicators */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-connected {
        background: #d4edda;
        color: #155724;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* Query result styling */
    .query-results {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Metrics cards */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Initialize session state with enhanced tracking
def initialize_session_state():
    """Initialize all session state variables with conversation history"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = generate_conversation_id()

    if "conversation_manager" not in st.session_state:
        st.session_state.conversation_manager = ConversationManager()

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
            "avg_response_time": 0,
        }

    if "database_info" not in st.session_state:
        st.session_state.database_info = None


def generate_conversation_id():
    """Generate unique conversation ID"""
    import random

    return (
        f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
    )


initialize_session_state()


# Enhanced query processing with performance tracking
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_schema():
    """Get cached schema information"""
    if st.session_state.query_system:
        return st.session_state.query_system.get_schema_info()
    return None


def process_contextual_query(
    prompt: str, conversation_manager: ConversationManager
) -> Dict[str, Any]:
    """Enhanced query processing with conversation context"""
    if not st.session_state.query_system:
        return {"error": "Please initialize connection first!"}

    # Get conversation context
    context = conversation_manager.get_conversation_context()

    # Enhance prompt with context if available
    if context:
        enhanced_prompt = f"""
        Previous conversation context:
        {context}
        
        Current question: {prompt}
        
        Please consider the previous context when answering this question.
        """
    else:
        enhanced_prompt = prompt

    start_time = time.time()

    try:
        # Update stats
        st.session_state.query_stats["total_queries"] += 1

        # Process with context
        result = st.session_state.query_system.query(enhanced_prompt)

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
            current_avg * (total_queries - 1) + response_time
        ) / total_queries

        # Add performance metadata
        result["response_time"] = response_time
        result["timestamp"] = datetime.now().isoformat()

        # Add to conversation history
        conversation_manager.add_interaction(
            user_input=prompt,
            assistant_response=result,
            context={"processing_time": response_time},
        )

        return result

    except Exception as e:
        st.session_state.query_stats["failed_queries"] += 1
        error_result = {
            "error": f"Unexpected error: {str(e)}",
            "response_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat(),
        }

        conversation_manager.add_interaction(
            user_input=prompt, assistant_response=error_result
        )

        return error_result


def display_query_stats():
    """Display query statistics in sidebar"""
    stats = st.session_state.query_stats
    if stats["total_queries"] > 0:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Queries", stats["total_queries"])
            st.metric(
                "Success Rate",
                f"{(stats['successful_queries']/stats['total_queries']*100):.1f}%",
            )
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
        if st.button(
            "🔌 Initialize Connection", type="primary", use_container_width=True
        ):
            with st.spinner("Connecting to Neo4j and Groq..."):
                try:
                    start_time = time.time()
                    st.session_state.query_system = NLToCypherQuery()

                    if st.session_state.query_system.test_connection():
                        connection_time = time.time() - start_time
                        st.session_state.connection_status = "✅ Connected"
                        st.session_state.connection_time = connection_time

                        # Get database info
                        st.session_state.database_info = (
                            st.session_state.query_system.get_database_info()
                        )

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
            st.markdown(
                f'<div class="success-message">{st.session_state.connection_status}</div>',
                unsafe_allow_html=True,
            )
            if st.session_state.connection_time:
                st.caption(f"Connected in {st.session_state.connection_time:.2f}s")
        else:
            st.markdown(
                f'<div class="error-message">{st.session_state.connection_status}</div>',
                unsafe_allow_html=True,
            )

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
            st.metric(
                Config.SIDEBAR_ASSET_TYPES_LABEL, len(info.get("node_labels", []))
            )
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

    st.markdown("---")
    st.subheader("💬 Conversation")

    # Conversation controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Export Chat", use_container_width=True):
            if hasattr(st.session_state, "conversation_manager"):
                import json

                export_data = (
                    st.session_state.conversation_manager.export_conversation()
                )
                st.download_button(
                    "💾 Download",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"conversation_{st.session_state.current_conversation_id}.json",
                    mime="application/json",
                )

    with col2:
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.current_conversation_id = generate_conversation_id()
            st.session_state.conversation_manager = ConversationManager()
            st.rerun()

    # Conversation history display
    if (
        hasattr(st.session_state, "conversation_manager")
        and st.session_state.conversation_manager.history
    ):
        with st.expander("📜 Chat History", expanded=False):
            history = st.session_state.conversation_manager.history[
                -5:
            ]  # Last 5 interactions
            for i, interaction in enumerate(reversed(history)):
                st.caption(f"**{interaction['timestamp'][:19]}**")
                st.text(f"Q: {interaction['user_input'][:50]}...")
                if "answer" in interaction["assistant_response"]:
                    st.text(f"A: {interaction['assistant_response']['answer'][:50]}...")
                st.divider()

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
                        st.text_area(
                            "Graph Schema",
                            value=str(schema),
                            height=300,
                            key="schema_viewer",
                        )
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
        st.markdown(
            """
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
        """
        )

    # Footer with version info
    st.markdown("---")
    st.caption(f"{Config.APP_ICON} Collibra Assistant {Config.APP_VERSION}")
    st.caption("Powered by LangChain & Streamlit")

# Enhanced main chat interface
st.title(f"{Config.APP_ICON} {Config.APP_TITLE}")
st.markdown("*AI-powered natural language interface with conversation memory*")

# Connection status with enhanced styling
if not st.session_state.query_system:
    st.markdown(
        """
    <div class="status-badge status-error">
        ⚠️ Connection Required
    </div>
    <p>Initialize the connection using the sidebar to start exploring your Collibra data governance landscape!</p>
    """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
    <div class="status-badge status-connected">
        ✅ Connected & Ready
    </div>
    """,
        unsafe_allow_html=True,
    )

# Quick action buttons
st.markdown("### 🚀 Quick Actions")
col1, col2, col3, col4 = st.columns(4)

sample_questions = [
    "How many assets are there?",
    "Show me all domains",
    "Who are the stewards?",
    "What tables exist?",
]

for i, (col, question) in enumerate(zip([col1, col2, col3, col4], sample_questions)):
    with col:
        if st.button(question, key=f"sample_{i}", use_container_width=True):
            st.session_state.quick_question = question

# Chat input with enhanced processing
if prompt := st.chat_input("Ask about your Collibra data governance..."):
    if st.session_state.query_system:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = process_contextual_query(
                    prompt, st.session_state.conversation_manager
                )

                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.markdown(result.get("answer", "No answer generated"))

                    # Display query details in expander
                    with st.expander("🔍 Query Details"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("Generated Query")
                            st.code(result.get("cypher_query", ""), language="cypher")

                        with col2:
                            st.subheader("Metrics")
                            if "response_time" in result:
                                st.metric(
                                    "Response Time", f"{result['response_time']:.2f}s"
                                )
                            if "query_results" in result:
                                st.metric("Results", len(result["query_results"]))

                        # Show raw results if available
                        if result.get("query_results"):
                            st.subheader("Raw Results")
                            st.json(result["query_results"][:3])  # Show first 3 results
    else:
        st.warning("Please initialize the connection first!")

# Handle quick questions
if "quick_question" in st.session_state:
    prompt = st.session_state.quick_question
    del st.session_state.quick_question
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

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": error_msg,
                            "error": result["error"],
                            "details": {
                                "response_time": result.get("response_time", 0),
                                "timestamp": result.get("timestamp", ""),
                            },
                        }
                    )
                else:
                    answer = result.get("answer", "No answer generated")
                    st.write(answer)

                    # Show performance info
                    if "response_time" in result:
                        st.markdown(
                            f'<div class="query-stats">⏱️ Response time: {result["response_time"]:.2f}s</div>',
                            unsafe_allow_html=True,
                        )

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
                                    st.warning(
                                        f"⚠️ Validation: {validation.get('message', 'Unknown issue')}"
                                    )

                        if "query_results" in result and result["query_results"]:
                            st.write("**Query Results:**")
                            results = result["query_results"]
                            st.caption(f"Returned {len(results)} result(s)")

                            if len(results) <= 10:
                                st.json(results)
                            else:
                                st.json(results[:5])
                                st.caption(
                                    f"Showing first 5 of {len(results)} results..."
                                )

                        if "timestamp" in result:
                            st.caption(f"Query executed at: {result['timestamp']}")

                    # Add to session state with all details
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "details": {
                                "cypher_query": result.get("cypher_query", ""),
                                "query_results": result.get("query_results", []),
                                "response_time": result.get("response_time", 0),
                                "timestamp": result.get("timestamp", ""),
                                "validation": result.get("validation", {}),
                            },
                        }
                    )

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
        st.caption(
            f"{st.session_state.query_stats['total_queries']} queries • "
            f"{st.session_state.query_stats['avg_response_time']:.1f}s avg"
        )
