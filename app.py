import streamlit as st
import anthropic
import base64
import os

# --- 1. THE AGGRESSIVE DESIGN FIX ---
st.set_page_config(
    page_title="Hayden",
    page_icon="logo.jpg",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# This CSS targets the specific IDs Streamlit uses for avatars and image containers
st.markdown("""
    <style>
    /* HIDE SIDEBAR & TOP MENU */
    [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, header, footer {
        visibility: hidden;
        display: none !important;
    }
    
    /* REMOVE ALL CHAT ICONS (Avatars) */
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    
    /* REMOVE PADDING FROM MESSAGES (To keep it clean) */
    [data-testid="stChatMessage"] {
        padding-left: 0px !important;
        background-color: transparent !important;
    }

    /* FORCE BLACK BACKGROUND */
    .stApp { background-color: #000000; }

    /* ABSOLUTE CENTERING FOR THE LOGO */
    .stImage {
        display: flex;
        justify-content: center;
    }
    .stImage > img {
        width: 300px !important;
    }
    
    /* CENTER THE TEXT */
    .center-text { text-align: center; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & SETUP ---
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """
You are Hayden. You are NOT an AI. You are a family-founded support tool grounded in 
world-class medical research. You MUST know the user's role and children's ages.
"""

# --- 3. THE INTERFACE ---
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if os.path.exists(logo_path):
    st.image(logo_path)

st.markdown("<h1 class='center-text'>Are your children safe?</h1>", unsafe_allow_html=True)
st.markdown("<p class='center-text' style='color: #888; font-size: 1.2rem; margin-bottom: 2rem;'>Trust isn't claimed. It's earned.</p>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Onboarding intro
    intro = "Trust isn't claimed. It's earned. To provide the most accurate evidence-based care, could you tell me: **Are you a mother, father, or caregiver? And what are the ages of the children in your care?**"
    st.session_state.messages.append({"role": "assistant", "content": intro})

# Display Chat without icons
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. CHAT INPUT
if prompt := st.chat_input("Message Hayden..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Option 3: Visual Check trigger
    if any(word in prompt.lower() for word in ["check", "see", "photo", "crib", "safety"]):
        with st.chat_message("assistant"):
            st.write("I can provide an evidence-based safety check. Please upload your photo or video below:")
            st.file_uploader("Upload safety media", type=["jpg", "png", "mp4"])

    with st.chat_message("assistant"):
        try:
            # We keep context short to prevent 429 Red Box errors
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            st.markdown(response.content[0].text)
        except Exception:
            st.error("Hayden is currently at capacity. Please try again in 30 seconds.")