import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_perplexity import ChatPerplexity  # Hypothetical for Perplexity
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set wide layout
st.set_page_config(layout="wide", page_title="AI Chatbot", page_icon="🤖")

# Custom CSS for dark mode chat styling
st.markdown("""
    <style>
    /* Dark mode colors */
    :root {
        --bg-color: #0f172a;
        --card-color: #1e293b;
        --text-color: #e2e8f0;
        --user-msg-color: #3b82f6;
        --bot-msg-color: #334155;
        --input-bg: #1e293b;
        --input-border: #475569;
        --sidebar-bg: #1e293b;
        --button-bg: #3b82f6;
        --button-hover: #2563eb;
        --clear-btn-bg: #7f1d1d;
        --clear-btn-hover: #991b1b;
    }
    
    /* Main container styling */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
    }
    
    /* Chat container */
    .chat-container {
        max-height: calc(100vh - 180px);
        overflow-y: auto;
        padding: 20px;
        background-color: var(--card-color);
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin-bottom: 90px;
    }
    
    /* Message bubbles */
    .message {
        padding: 12px 16px;
        border-radius: 18px;
        margin-bottom: 12px;
        word-wrap: break-word;
        line-height: 1.5;
        position: relative;
        font-size: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        max-width: fit-content;
    }
    
    .user-message {
        background-color: var(--user-msg-color);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
        max-width: 75%;
    }
    
    .bot-message {
        background-color: var(--bot-msg-color);
        color: var(--text-color);
        margin-right: auto;
        border-bottom-left-radius: 4px;
        max-width: 85%;
    }
    
    /* Input area - updated for inline button */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: var(--card-color);
        padding: 15px;
        display: flex;
        align-items: center;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
        z-index: 100;
        gap: 10px;
    }
    
    /* Input field - updated for inline button */
    .stTextInput > div > div > input {
        background-color: var(--input-bg);
        border: 1px solid var(--input-border);
        border-radius: 24px;
        color: var(--text-color);
        padding: 12px 20px;
        font-size: 15px;
        transition: all 0.3s;
        flex-grow: 1;
        margin-right: 10px;
    }
    
    .stTextInput > div > div > input:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
        border-color: var(--user-msg-color);
    }
    
    /* Send button - updated for inline positioning */
    .stButton > button {
        background-color: var(--button-bg);
        color: white;
        border: none;
        border-radius: 24px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s;
        height: 48px;
        white-space: nowrap;
    }
    
    .stButton > button:hover {
        background-color: var(--button-hover);
        transform: translateY(-1px);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
    }
    
    /* Title styling */
    .title {
        color: var(--text-color);
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    /* Animation for messages */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .message {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* Clear button styling */
    .clear-btn {
        background-color: var(--clear-btn-bg) !important;
        color: white !important;
        border: none !important;
    }
    
    .clear-btn:hover {
        background-color: var(--clear-btn-hover) !important;
    }
    
    /* API key input styling */
    .stTextInput > div > div > input[type="password"] {
        background-color: var(--input-bg);
        border: 1px solid var(--input-border);
        border-radius: 8px;
        padding: 10px 15px;
        color: var(--text-color);
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .user-message {
            max-width: 85%;
        }
        .bot-message {
            max-width: 90%;
        }
        .stButton > button {
            padding: 12px 16px;
        }
    }
    
    /* Add some spacing between messages */
    .message + .message {
        margin-top: 8px;
    }
    </style>
    <script>
    // Auto-scroll to bottom of chat
    function scrollToBottom() {
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    // Handle Enter key press
    function setupEnterKey() {
        const input = document.querySelector('.stTextInput input');
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const sendButton = document.querySelector('.stButton button');
                    if (sendButton) {
                        sendButton.click();
                    }
                }
            });
        }
    }
    
    // Initialize when page loads
    document.addEventListener('DOMContentLoaded', function() {
        scrollToBottom();
        setupEnterKey();
        
        // Also scroll when messages are added
        const observer = new MutationObserver(function() {
            scrollToBottom();
            setupEnterKey(); // Re-setup in case Streamlit recreates elements
        });
        
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            observer.observe(chatContainer, { childList: true, subtree: true });
        }
    });
    
    // Re-setup when Streamlit reruns
    if (typeof Streamlit !== 'undefined') {
        Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, function() {
            setupEnterKey();
        });
    }
    </script>
""", unsafe_allow_html=True)

# Initialize the LLM and conversation chain
@st.cache_resource
def get_conversation_chain(llm_type):
    if llm_type == "OpenAI":
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    elif llm_type == "Gemini":
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, google_api_key=os.getenv("GOOGLE_API_KEY"))
    elif llm_type == "Perplexity":
        llm = ChatPerplexity(model="sonar", temperature=0.7, api_key=os.getenv("PERPLEXITY_API_KEY"))  # Hypothetical
    memory = ConversationBufferMemory()
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False,
        prompt=PromptTemplate(
            input_variables=["input", "history"],
            template="""You are a helpful assistant, answer in as detail as possible. If the user asks for competitors of a company, provide a detailed list of competitors organized by the following geographical regions: North America, Latin America, Europe, Asia-Pacific (APAC), Middle East and North Africa (MENA), Sub-Saharan Africa, and Russia and CIS. For each competitor, include the company name, country, and a brief description of their focus (e.g., aerospace, defense, etc.). If no competitors are identified in a region, list the regions and explicitly state: "No competitors available in this region to the best of my knowledge." Format the response using markdown with region headers (e.g., ## Region Name) and bullet points for each competitor. For all other queries, respond naturally and concisely as a conversational AI. Use the current conversation history: {history}\nUser input: {input}\nAssistant response:"""
        )
    )
    return conversation

# Sidebar for LLM selection
with st.sidebar:
    st.markdown("<h2 style='color: var(--text-color);'>Settings ⚙️</h2>", unsafe_allow_html=True)
    llm_option = st.selectbox(
        "Select AI Model", 
        ["OpenAI", "Gemini", "Perplexity"],
        key="llm_selector"
    )
    
    # Set API keys from environment variables
    if llm_option == "OpenAI":
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or st.text_input(
            "OpenAI API Key:", 
            type="password",
            help="Get your API key from https://platform.openai.com/api-keys"
        )
    elif llm_option == "Gemini":
        os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY") or st.text_input(
            "Google API Key:", 
            type="password",
            help="Get your API key from https://ai.google.dev/"
        )
    elif llm_option == "Perplexity":
        os.environ["PERPLEXITY_API_KEY"] = os.getenv("PERPLEXITY_API_KEY") or st.text_input(
            "Perplexity API Key:", 
            type="password",
            help="Get your API key from https://www.perplexity.ai/"
        )

    # Add clear chat history button in the sidebar
    if st.button("Clear Chat History", key="clear_chat", help="Start a new conversation"):
        st.session_state.chat_history = []
        st.session_state.conversation = get_conversation_chain(llm_option)
        st.session_state.input_key += 1
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
        <div style="color: #94a3b8; font-size: 14px;">
        <p><strong>Tip:</strong> Ask about company competitors to get a detailed regional analysis.</p>
        <p>Example: "What are the competitors of Boeing?"</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")


# Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "selected_llm" not in st.session_state:
    st.session_state.selected_llm = llm_option

# Update conversation chain if LLM changes
if st.session_state.selected_llm != llm_option:
    st.session_state.selected_llm = llm_option
    st.session_state.conversation = get_conversation_chain(llm_option)

# Load or initialize conversation chain
if st.session_state.conversation is None:
    st.session_state.conversation = get_conversation_chain(llm_option)

# Main app area
st.markdown(f"<h1 class='title'>AI Chat Assistant with {llm_option} 🤖</h1>", unsafe_allow_html=True)

# Chat history display
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for chat in st.session_state.chat_history:
        st.markdown(f'<div class="message user-message"><strong>You:</strong> {chat["user"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="message bot-message"><strong>Assistant:</strong> {chat["bot"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Input container at bottom - now with inline button
with st.container():
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    # Create columns for input and button (3:1 ratio)
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message...",
            key=f"input_{st.session_state.input_key}",
            label_visibility="collapsed",
            placeholder="Ask about company competitors or anything else..."
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Handle user input
if (send_button or st.session_state.get("enter_pressed", False)) and user_input:
    try:
        # Get response from the conversation chain
        response = st.session_state.conversation.predict(input=user_input)
        
        # Append to chat history
        st.session_state.chat_history.append({"user": user_input, "bot": response})
        
        # Clear input by updating key
        st.session_state.input_key += 1
        st.session_state.enter_pressed = False
        st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
