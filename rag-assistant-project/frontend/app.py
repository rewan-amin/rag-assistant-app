import streamlit as st
from api_client import check_health, ask_question

# Configure page layout and title
st.set_page_config(
    page_title="FloraCare | AI Plant Disease & Crop Health Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling to enforce crystal-clear contrast and match the requested botanical aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400;1,600;1,700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Global Body and Background */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #f8faf6 !important;
        background: #f8faf6 !important;
        color: #14281b !important;
    }

    .stApp {
        background-image: 
            radial-gradient(circle at 50% 100px, rgba(167, 243, 208, 0.45) 0%, rgba(248, 250, 246, 0) 65%),
            radial-gradient(circle at 85% 260px, rgba(187, 247, 208, 0.25) 0%, rgba(248, 250, 246, 0) 50%) !important;
    }

    /* Optimal container padding to eliminate dead top/bottom space */
    .stMainBlockContainer,
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 5.5rem !important;
        max-width: 960px !important;
        margin: 0 auto !important;
    }

    /* Hide standard Streamlit header & toolbar clutter */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px !important;
    }
    #MainMenu, footer {visibility: hidden;}

    /* Top Navigation Bar */
    .top-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 20px;
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(12px);
        border: 1px solid #dce8dd;
        border-radius: 9999px;
        margin: 0 auto 16px auto;
        box-shadow: 0 3px 14px -2px rgba(31, 78, 56, 0.05);
    }

    .nav-brand {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 700;
        font-size: 17px;
        color: #1f4e38;
        letter-spacing: -0.3px;
    }

    .nav-brand-leaf {
        background: #e8f5e9;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
        border: 1px solid #c8e6c9;
    }

    .nav-links {
        display: flex;
        gap: 16px;
        font-size: 13px;
        font-weight: 500;
        color: #4a5d4f;
    }

    .nav-badge-pill {
        background-color: #1f4e38;
        color: #ffffff !important;
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(31, 78, 56, 0.15);
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }

    /* Hero Section */
    .hero-container {
        text-align: center;
        max-width: 800px;
        margin: 4px auto 18px auto;
        padding: 0 12px;
    }

    .hero-eyebrow {
        display: inline-block;
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 1.3px;
        text-transform: uppercase;
        color: #2e7d32;
        background: #e8f5e9;
        border: 1px solid #c8e6c9;
        padding: 3px 12px;
        border-radius: 9999px;
        margin-bottom: 10px;
    }

    .hero-title {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: 42px;
        line-height: 1.16;
        font-weight: 700;
        color: #112217;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }

    .hero-title span.accent-italic {
        color: #2e7d32;
        font-style: italic;
        font-weight: 600;
    }

    .hero-subtitle {
        font-size: 14.5px;
        line-height: 1.55;
        color: #4f6354;
        max-width: 650px;
        margin: 0 auto 16px auto;
    }

    /* Feature Highlights Grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin: 20px 0 24px 0;
    }

    .feature-card {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid #dce8dd;
        border-radius: 14px;
        padding: 16px 14px;
        text-align: left;
        box-shadow: 0 2px 8px rgba(31, 78, 56, 0.04);
        transition: transform 0.2s ease;
    }

    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(31, 78, 56, 0.08);
    }

    .feature-icon {
        font-size: 20px;
        margin-bottom: 6px;
    }

    .feature-title {
        font-size: 13.5px;
        font-weight: 700;
        color: #1f4e38;
        margin-bottom: 4px;
    }

    .feature-desc {
        font-size: 12px;
        line-height: 1.45;
        color: #55685a;
    }

    /* Quick Query Section */
    .chips-label {
        font-size: 11.5px;
        font-weight: 700;
        color: #4f6354;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 8px;
        text-align: center;
    }

    /* Fix Streamlit Buttons (Quick Prompts) */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #1f4e38 !important;
        border: 1.5px solid #2e7d32 !important;
        border-radius: 9999px !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        box-shadow: 0 2px 5px rgba(31, 78, 56, 0.04) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }

    div.stButton > button:hover {
        background-color: #1f4e38 !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(31, 78, 56, 0.18) !important;
    }

    /* Refined Chat Message Container & Visual Depth */
    div[data-testid="stChatMessage"] {
        padding: 14px 20px !important;
        border-radius: 16px !important;
        margin-bottom: 16px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }

    /* User Message: Crisp, Distinctive, and Clean */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]),
    div[data-testid="stChatMessage"]:has(.stChatMessageAvatarUser) {
        background-color: #edf6ef !important;
        border: 1px solid #c8e4cd !important;
        border-left: 4.5px solid #2e7d32 !important;
        box-shadow: 0 3px 10px rgba(31, 78, 56, 0.05) !important;
    }

    /* Output / Assistant Message: POPs off the page with layered depth & shadow */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]),
    div[data-testid="stChatMessage"]:has(.stChatMessageAvatarAssistant) {
        background-color: #ffffff !important;
        border: 1px solid #d3e7d6 !important;
        border-left: 4.5px solid #1f4e38 !important;
        box-shadow: 0 12px 28px -4px rgba(31, 78, 56, 0.12), 0 4px 10px -2px rgba(31, 78, 56, 0.06) !important;
    }

    /* Ensure all text inside chat messages is clear dark text */
    div[data-testid="stChatMessage"] * {
        color: #112217 !important;
        -webkit-text-fill-color: #112217 !important;
    }

    div[data-testid="stChatMessage"] p {
        font-size: 15px !important;
        line-height: 1.6 !important;
        color: #112217 !important;
        -webkit-text-fill-color: #112217 !important;
        margin-bottom: 6px !important;
    }

    div[data-testid="stChatMessage"] strong {
        color: #0b1c11 !important;
        font-weight: 700 !important;
    }

    /* Seamlessly Integrated Source Citation Container (No Awkward Nested Box) */
    .source-box {
        background: transparent !important;
        border: none !important;
        border-top: 1px dashed #d5e8d8 !important;
        border-radius: 0 !important;
        padding: 8px 0 2px 0 !important;
        margin-top: 10px !important;
        width: 100% !important;
    }

    .source-header {
        font-weight: 700;
        font-size: 11.5px;
        color: #24583e !important;
        -webkit-text-fill-color: #24583e !important;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 5px;
        letter-spacing: 0.2px;
        text-transform: uppercase;
    }

    .source-chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: #f0f7f1;
        color: #1b5e20 !important;
        -webkit-text-fill-color: #1b5e20 !important;
        border: 1px solid #c2e2ca;
        border-radius: 9999px;
        padding: 3px 11px;
        font-size: 11.5px;
        font-weight: 600;
        margin: 3px 5px 3px 0;
        box-shadow: 0 1px 3px rgba(31, 78, 56, 0.04);
        transition: all 0.2s ease;
    }

    .source-chip:hover {
        background: #e2f0e4;
        border-color: #9ecc9f;
        transform: translateY(-1px);
    }

    /* Completely Eliminate the Dark Bottom Bar */
    footer,
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div,
    div[data-testid="stBottomBlockContainer"] {
        background-color: #f8faf6 !important;
        background: #f8faf6 !important;
        border-top: 1px solid #dce8dd !important;
    }

    /* Custom Chat Input Box */
    div[data-testid="stChatInput"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border: 1.5px solid #2e7d32 !important;
        border-radius: 9999px !important;
        box-shadow: 0 4px 16px rgba(46, 125, 50, 0.08) !important;
        padding: 2px 6px !important;
    }

    div[data-testid="stChatInput"] > div {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: #14281b !important;
        -webkit-text-fill-color: #14281b !important;
        background-color: transparent !important;
        background: transparent !important;
        font-size: 14px !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #6d8272 !important;
        -webkit-text-fill-color: #6d8272 !important;
    }

    /* Send Button */
    div[data-testid="stChatInput"] button {
        background-color: #1f4e38 !important;
        color: #ffffff !important;
        border-radius: 50% !important;
        border: none !important;
        transition: background-color 0.2s ease !important;
    }

    div[data-testid="stChatInput"] button:hover {
        background-color: #2e7d32 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f1f6f0 !important;
        border-right: 1px solid #dbe7dc !important;
    }

    section[data-testid="stSidebar"] * {
        color: #19271d !important;
        -webkit-text-fill-color: #19271d !important;
    }

    .status-badge-active {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 11px;
        border-radius: 9999px;
        background-color: #e8f5e9;
        color: #2e7d32 !important;
        -webkit-text-fill-color: #2e7d32 !important;
        border: 1px solid #c8e6c9;
        font-size: 12px;
        font-weight: 700;
    }

    .status-badge-inactive {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 11px;
        border-radius: 9999px;
        background-color: #ffebee;
        color: #c62828 !important;
        -webkit-text-fill-color: #c62828 !important;
        border: 1px solid #ffcdd2;
        font-size: 12px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Top Navigation Bar
st.markdown("""
<div class="top-navbar">
    <div class="nav-brand">
        <div class="nav-brand-leaf">🌱</div>
        <span>FloraCare AI</span>
    </div>
    <div class="nav-links">
        <span>Plant Pathology RAG</span>
        <span>Agricultural Guides</span>
        <span>Gemini Reasoning</span>
    </div>
    <div class="nav-badge-pill">
        🌿 PlantWise Advisor
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar: System Health & Diagnostic Controls
with st.sidebar:
    st.markdown("### 🌿 Diagnostic Assistant")
    is_online = check_health()
    if is_online:
        st.markdown('<div class="status-badge-active">● RAG Engine Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge-inactive">○ Backend Offline (Start FastAPI)</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    
    with st.expander("📚 Knowledge Repository", expanded=True):
        st.markdown("""
        - **Domain**: Plant Pathology & Crop Protection
        - **Embeddings**: `Qwen3-Embedding-0.6B`
        - **LLM Reasoning**: `Gemini Flash`
        - **Grounded Guides**: Plantwise Field Diagnostic Guide, Cereal Diseases Guide
        """)

    st.markdown("### ⚙️ Retrieval Hyperparameters")
    top_k_val = st.slider("Retrieved Context Chunks (Top-K)", min_value=1, max_value=8, value=4)
    st.caption("Controls how many scientific evidence excerpts are retrieved per question.")

    if st.button("🗑️ Reset Chat History"):
        st.session_state.messages = []
        st.rerun()

# Hero Header
st.markdown("""
<div class="hero-container">
    <div class="hero-eyebrow">AI Plant Disease & Crop Health RAG</div>
    <div class="hero-title">Diagnose your crops <span class="accent-italic">like a farm expert.</span></div>
    <div class="hero-subtitle">
        Understand plant symptoms, pinpoint pathogens, and discover verified field treatment protocols — 
        all grounded directly in trusted agricultural diagnostic guides with verified citations.
    </div>
</div>
""", unsafe_allow_html=True)

# Quick Diagnostic Query Buttons
st.markdown("<div class='chips-label'>💡 Quick Diagnostic Queries:</div>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

selected_sample = None
with col1:
    if st.button("🍅 Tomato Late Blight", key="btn_tomato"):
        selected_sample = "What are the symptoms and treatments of tomato late blight?"
with col2:
    if st.button("🌾 Cereal Leaf Rust", key="btn_rust"):
        selected_sample = "How do I identify and manage rust diseases in cereal crops?"
with col3:
    if st.button("🧪 Fungicide Thresholds", key="btn_fungicide"):
        selected_sample = "What fungicides and economic injury thresholds are recommended for fungal diseases?"
with col4:
    if st.button("🌱 Powdery Mildew", key="btn_mildew"):
        selected_sample = "What cultural controls and treatments exist for powdery mildew?"

# Initialize chat session history
if "messages" not in st.session_state:
    st.session_state.messages = []

# When no messages yet, display feature cards to elegantly fill the central area
if not st.session_state.messages:
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🔬</div>
            <div class="feature-title">Foliar & Soil Blights</div>
            <div class="feature-desc">Identify late blight, wilts, damping-off, and fungal lesions with verified visual indicators.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🧪</div>
            <div class="feature-title">Chemical & Bio Controls</div>
            <div class="feature-desc">Recommended active ingredients, application timing, and economic damage thresholds.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📖</div>
            <div class="feature-title">Grounded Evidence</div>
            <div class="feature-desc">Strict zero-hallucination answers backed directly by official agricultural field manuals.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render Conversation Messages
for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role, avatar="🌱" if role == "assistant" else "👤"):
        st.markdown(msg["content"])
        if msg.get("sources") and "does not contain enough information" not in msg["content"]:
            chips_html = "".join([f'<span class="source-chip">📄 {src}</span>' for src in msg["sources"]])
            source_html = f"""
            <div class="source-box">
                <div class="source-header">📖 Verified Reference Sources:</div>
                <div>{chips_html}</div>
            </div>
            """
            st.markdown(source_html, unsafe_allow_html=True)

# Handle Question from chat input or sample button
query_text = selected_sample or st.chat_input("Ask about crop symptoms, pathogens, or treatments...")

if query_text:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": query_text})
    with st.chat_message("user", avatar="👤"):
        st.markdown(query_text)

    # Call Backend and Generate Answer
    with st.chat_message("assistant", avatar="🌱"):
        with st.spinner("🔍 Consulting plant pathology vector store & synthesizing diagnosis..."):
            try:
                response = ask_question(question=query_text, top_k=top_k_val)
                answer = response.get("answer", "No response received.")
                sources = response.get("sources", [])

                st.markdown(answer)

                if sources and "does not contain enough information" not in answer:
                    chips_html = "".join([f'<span class="source-chip">📄 {src}</span>' for src in sources])
                    source_html = f"""
                    <div class="source-box">
                        <div class="source-header">📖 Verified Reference Sources:</div>
                        <div>{chips_html}</div>
                    </div>
                    """
                    st.markdown(source_html, unsafe_allow_html=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            except Exception as e:
                err_msg = f"⚠️ **Could not complete diagnosis:** {str(e)}"
                st.error(err_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": err_msg
                })
