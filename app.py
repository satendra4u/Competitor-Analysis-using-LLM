import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()

# Set page config
st.set_page_config(
    layout="wide", 
    page_title="AI Assistant Pro", 
    page_icon="🚀"
)

# Enhanced Custom CSS with modern design
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Modern dark theme variables */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --bg-primary: #0a0e1a;
        --bg-secondary: #1a1f2e;
        --bg-tertiary: #252b3b;
        --text-primary: #ffffff;
        --text-secondary: #b4bcd0;
        --text-muted: #6b7280;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-green: #10b981;
        --border-color: #374151;
        --shadow-light: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-medium: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-heavy: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
    
    /* Base styles */
    html, body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* Main app container */
    .stApp {
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* Header section - compact */
    .header-section {
        background: var(--primary-gradient);
        padding: 1rem;
        margin: -1rem -1rem 1rem -1rem;
        border-radius: 0 0 16px 16px;
        text-align: center;
        position: relative;
    }
    
    .header-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Chat container */
    .chat-container {
        background: rgba(26, 31, 46, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 100px;
        max-height: calc(100vh - 220px);
        overflow-y: auto;
        box-shadow: var(--shadow-medium);
    }
    
    /* Message bubbles */
    .message {
        padding: 0.8rem 1rem;
        border-radius: 16px;
        margin-bottom: 0.8rem;
        font-size: 0.9rem;
        line-height: 1.5;
        box-shadow: var(--shadow-light);
        max-width: fit-content;
        animation: messageSlideIn 0.3s ease-out;
    }
    
    .user-message {
        background: var(--primary-gradient);
        color: white;
        margin-left: auto;
        max-width: 75%;
    }
    
    .bot-message {
        background: rgba(37, 43, 59, 0.9);
        color: var(--text-primary);
        margin-right: auto;
        max-width: 85%;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Message labels */
    .message strong {
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.8;
    }
    
    /* Fixed input container at bottom */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(26, 31, 46, 0.95);
        backdrop-filter: blur(20px);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem;
        z-index: 1000;
    }
    
    /* Input wrapper with send button inside */
    .input-wrapper {
        max-width: 1200px;
        margin: 0 auto;
        position: relative;
        display: flex;
        align-items: center;
    }
    
    /* Enhanced input field */
    .stTextInput > div > div > input {
        background: rgba(37, 43, 59, 0.9) !important;
        border: 2px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 25px !important;
        color: var(--text-primary) !important;
        padding: 0.8rem 3rem 0.8rem 1.2rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
        width: 100% !important;
    }
    
    .stTextInput > div > div > input:focus {
        outline: none !important;
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* Send button inside input */
    .send-button {
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        background: var(--primary-gradient);
        border: none;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        z-index: 10;
    }
    
    .send-button:hover {
        transform: translateY(-50%) scale(1.05);
        box-shadow: var(--shadow-medium);
    }
    
    .send-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    /* Tips section */
    .tips-section {
        background: rgba(37, 43, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }
    
    .tips-section h4 {
        color: var(--accent-blue);
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .tips-section p {
        color: var(--text-secondary);
        font-size: 0.8rem;
        line-height: 1.4;
        margin-bottom: 0.3rem;
    }
    
    .tips-section code {
        background: rgba(59, 130, 246, 0.1);
        color: var(--accent-blue);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        padding: 0.5rem !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: var(--secondary-gradient) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        width: 100% !important;
        border: none !important;
        color: white !important;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.2rem 0.5rem;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-openai {
        background: rgba(16, 185, 129, 0.1);
        color: var(--accent-green);
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .status-gemini {
        background: rgba(139, 92, 246, 0.1);
        color: var(--accent-purple);
        border: 1px solid rgba(139, 92, 246, 0.2);
    }
    
    /* Loading indicator */
    .loading-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--text-secondary);
        font-size: 0.85rem;
        margin: 1rem 0;
        justify-content: center;
    }
    
    .loading-dots {
        display: flex;
        gap: 3px;
    }
    
    .loading-dots div {
        width: 5px;
        height: 5px;
        background: var(--accent-blue);
        border-radius: 50%;
        animation: pulse 1.4s infinite;
    }
    
    .loading-dots div:nth-child(2) { animation-delay: 0.2s; }
    .loading-dots div:nth-child(3) { animation-delay: 0.4s; }
    
    /* Enhanced scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--accent-blue), var(--accent-purple));
        border-radius: 10px;
    }
    
    /* Animations */
    @keyframes messageSlideIn {
        from {
            opacity: 0;
            transform: translateY(15px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 1.5rem;
        }
        
        .user-message, .bot-message {
            max-width: 90%;
        }
        
        .chat-container {
            padding: 1rem;
            margin-bottom: 80px;
        }
        
        .input-container {
            padding: 0.8rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Function to calculate matching score based on format
def calculate_format_score(response, is_competitor_query=False):
    if not response:
        return 0.0
    
    score = 0.0
    max_score = 100.0
    
    if is_competitor_query:
        regions = [
            "North America", "Europe", "Asia-Pacific", "Middle East", "Latin America", "Africa"
        ]
        
        if re.search(r"^[^\n#]+\n", response):
            score += 20.0
        
        headers_found = sum(1 for region in regions if f"## {region}" in response)
        score += (headers_found / len(regions)) * 30.0
        
        bullet_pattern = r"^\s*[-*]\s+([^\(]+)\s*\(([^\)]+)\)\s*–\s*([^\n]+)$"
        bullets = re.findall(bullet_pattern, response, re.MULTILINE)
        if bullets:
            score += min(len(bullets) / 5, 1.0) * 30.0
        
        if re.search(r"\n\n[^\n#]+$", response):
            score += 20.0
            
    else:
        paragraphs = [p.strip() for p in response.split("\n\n") if p.strip()]
        if paragraphs:
            score += min(len(paragraphs), 3) * 20.0
            if len(response.split()) > 50:
                score += 20.0
            if not re.search(r"^[#-*]", response, re.MULTILINE):
                score += 20.0
                
    return score / max_score * 100

# Enhanced conversation chains with detailed prompt
@st.cache_resource
def get_conversation_chains():
    enhanced_prompt_template = PromptTemplate(
        input_variables=["input", "history"],
        template="""You are an expert AI assistant with deep knowledge across all domains. Your responses should be comprehensive, well-structured, and highly informative.

**RESPONSE GUIDELINES:**

**For Competitor Analysis Queries:**
When a user asks about competitors of any company, provide an extremely detailed and comprehensive analysis following this EXACT structure:

1. **Introduction (2-3 sentences):** Briefly introduce the company and the competitive landscape overview.

2. **Regional Analysis:** Organize competitors by these geographical regions:
   - **North America** (US, Canada, Mexico)
   - **Europe** (EU countries, UK, Norway, Switzerland, etc.)
   - **Asia-Pacific** (China, Japan, India, South Korea, Australia, Southeast Asia)
   - **Middle East & North Africa** (UAE, Saudi Arabia, Israel, Egypt, etc.)
   - **Latin America** (Brazil, Argentina, Chile, Colombia, etc.)
   - **Sub-Saharan Africa** (South Africa, Nigeria, Kenya, etc.)
   - **Russia & CIS** (Russia, Kazakhstan, Ukraine, etc.)

3. **Format for each region:**
   ```
   ## [Region Name]
   [2-3 sentence description of the competitive landscape in this region, market characteristics, and key trends]
   
   - **[Company Name] ([Country])** – [Detailed description of company focus, specialties, market position, key products/services, and competitive advantages. Include revenue size if known (small/medium/large), founding year, and any notable achievements or market share information]
   - **[Next company]** – [Similar detailed description]
   ```

4. **For regions with no competitors:** Still include the region header and state: "No significant competitors identified in this region based on current market analysis."

5. **Conclusion (2-3 sentences):** Summarize the global competitive landscape and key market dynamics.

**For General Queries:**
Provide comprehensive, well-researched responses with:
- Clear structure with logical flow
- Detailed explanations with context
- Multiple perspectives when relevant
- Practical examples and applications
- Current industry insights when applicable
- Professional yet conversational tone

**QUALITY STANDARDS:**
- Use specific details, numbers, and facts whenever possible
- Include recent developments and market trends
- Explain technical concepts clearly
- Provide actionable insights
- Maintain accuracy and cite general knowledge appropriately
- Use professional language with appropriate technical terminology
- Elaborate on subtopics and provide comprehensive coverage of all aspects

**Conversation History:** {history}

**User Query:** {input}

**Your Response:**"""
    )
    
    try:
        chains = {}
        
        # Initialize OpenAI if API key is available
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            openai_llm = ChatOpenAI(
                model_name="gpt-3.5-turbo", 
                temperature=0.3, 
                openai_api_key=openai_key,
                max_tokens=20000
            )
            openai_memory = ConversationBufferMemory(return_messages=True)
            chains["OpenAI"] = ConversationChain(
                llm=openai_llm,
                memory=openai_memory,
                verbose=False,
                prompt=enhanced_prompt_template
            )
        
        # Initialize Gemini if API key is available
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            gemini_llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", 
                temperature=0.3, 
                google_api_key=google_key,
                max_output_tokens=20000
            )
            gemini_memory = ConversationBufferMemory(return_messages=True)
            chains["Gemini"] = ConversationChain(
                llm=gemini_llm,
                memory=gemini_memory,
                verbose=False,
                prompt=enhanced_prompt_template
            )
        
        return chains
    except Exception as e:
        st.error(f"Error initializing conversation chains: {str(e)}")
        return {}

# Compact header section
st.markdown("""
    <div class="header-section">
        <h1 class="header-title">🚀 AI Assistant Pro</h1>
    </div>
""", unsafe_allow_html=True)

# Main layout with columns
col1, col2 = st.columns([3, 1])

with col2:
    # Pro Tips section on the right
    st.markdown("""
        <div class="tips-section">
            <h4>💡 Pro Tips</h4>
            <p><strong>🎯 Competitor Analysis:</strong> Ask <code>"What are the competitors of [Company]?"</code></p>
            <p><strong>📊 Market Research:</strong> Request industry analysis and trends</p>
            <p><strong>🔍 Deep Dive:</strong> Ask follow-up questions for details</p>
            <p><strong>💼 Examples:</strong> "Tesla competitors", "Boeing rivals"</p>
        </div>
    """, unsafe_allow_html=True)

# Sidebar for API keys (only if not in .env)
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Check and handle API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    # Only show input if key not found in .env
    if not openai_key:
        openai_input = st.text_input(
            "OpenAI API Key:", 
            type="password",
            help="Get your API key from https://platform.openai.com/api-keys",
            placeholder="sk-..."
        )
        if openai_input:
            os.environ["OPENAI_API_KEY"] = openai_input
    
    if not google_key:
        google_input = st.text_input(
            "Google API Key:", 
            type="password",
            help="Get your API key from https://ai.google.dev/",
            placeholder="AIza..."
        )
        if google_input:
            os.environ["GOOGLE_API_KEY"] = google_input
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", help="Start fresh", use_container_width=True):
        st.session_state.chat_history = []
        if 'conversation_chains' in st.session_state:
            st.session_state.conversation_chains = get_conversation_chains()
        st.session_state.input_key = st.session_state.get('input_key', 0) + 1
        st.rerun()
    
    # Model status
    st.markdown("### 🤖 Models")
    openai_status = "🟢 Ready" if os.getenv("OPENAI_API_KEY") else "🔴 No Key"
    google_status = "🟢 Ready" if os.getenv("GOOGLE_API_KEY") else "🔴 No Key"
    st.markdown(f"**OpenAI:** {openai_status}")
    st.markdown(f"**Gemini:** {google_status}")

with col1:
    # Initialize session state
    if "conversation_chains" not in st.session_state:
        st.session_state.conversation_chains = get_conversation_chains()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False

    # Chat history display
    if st.session_state.chat_history:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for chat in st.session_state.chat_history:
            # User message
            st.markdown(f'''
                <div class="message user-message">
                    <strong>You</strong><br>
                    {chat["user"]}
                </div>
            ''', unsafe_allow_html=True)
            
            # Bot message with model indicator
            model_indicator = f'<span class="status-indicator status-{chat["llm"].lower()}">{chat["llm"]}</span>'
            st.markdown(f'''
                <div class="message bot-message">
                    <strong>AI Assistant {model_indicator}</strong><br>
                    {chat["bot"]}
                </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Welcome message
        st.markdown('''
            <div class="chat-container">
                <div class="message bot-message" style="margin: 2rem auto; text-align: center; max-width: 500px;">
                    <strong>👋 Welcome to AI Assistant Pro!</strong><br><br>
                    I'm here to help with competitor analysis, market research, and detailed insights across any industry or topic.
                    <br><br>
                    Try asking about competitors of your favorite companies!
                </div>
            </div>
        ''', unsafe_allow_html=True)

    # Processing indicator
    if st.session_state.is_processing:
        st.markdown('''
            <div class="loading-indicator">
                <span>🤖 AI is thinking</span>
                <div class="loading-dots">
                    <div></div>
                    <div></div>
                    <div></div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

# Fixed input container at bottom
st.markdown('<div class="input-container">', unsafe_allow_html=True)
st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)

# Input field
user_input = st.text_input(
    "Message",
    key=f"input_{st.session_state.input_key}",
    label_visibility="collapsed",
    placeholder="Ask about competitors, market analysis, or anything else...",
    disabled=st.session_state.is_processing
)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Handle input processing
if user_input and user_input.strip() and not st.session_state.is_processing:
    # Check if API keys are available
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        st.error("⚠️ Please provide at least one API key to continue.")
    else:
        st.session_state.is_processing = True
        
        try:
            # Check if the query is about competitors
            is_competitor_query = any(keyword in user_input.lower() for keyword in [
                "competitor", "competition", "rival", "versus", "vs", "compare", "competing"
            ])
            
            # Get responses from available LLMs
            responses = {}
            
            for llm_name, chain in st.session_state.conversation_chains.items():
                try:
                    if ((llm_name == "OpenAI" and os.getenv("OPENAI_API_KEY")) or 
                        (llm_name == "Gemini" and os.getenv("GOOGLE_API_KEY"))):
                        response = chain.predict(input=user_input)
                        responses[llm_name] = response
                except Exception as e:
                    st.error(f"Error with {llm_name}: {str(e)}")
            
            if responses:
                # Calculate format matching scores
                scores = {}
                for llm_name, response in responses.items():
                    score = calculate_format_score(response, is_competitor_query)
                    scores[llm_name] = score
                
                # Select the response with the highest score
                best_llm = max(scores, key=scores.get)
                best_response = responses[best_llm]
                
                # Append to chat history
                st.session_state.chat_history.append({
                    "user": user_input,
                    "bot": best_response,
                    "llm": best_llm
                })
                
                # Clear input by updating key
                st.session_state.input_key += 1
        
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
        
        finally:
            st.session_state.is_processing = False
            st.rerun()

# JavaScript for Enter key and auto-scroll
st.markdown("""
    <script>
    function handleEnterKey() {
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.target.tagName === 'INPUT' && e.target.type === 'text') {
                e.preventDefault();
                // Trigger Streamlit to process the input
                e.target.blur();
                e.target.focus();
            }
        });
    }
    
    function scrollToBottom() {
        setTimeout(function() {
            const chatContainer = document.querySelector('.chat-container');
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }, 100);
    }
    
    // Initialize
    document.addEventListener('DOMContentLoaded', function() {
        handleEnterKey();
        scrollToBottom();
    });
    
    // Handle Streamlit updates
    window.addEventListener('load', function() {
        handleEnterKey();
        scrollToBottom();
    });
    </script>
""", unsafe_allow_html=True)
