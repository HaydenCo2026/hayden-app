import streamlit as st
import anthropic
import base64
import os

# --- 1. THE ATOMIC DESIGN FIX ---
st.set_page_config(
    page_title="Hayden",
    page_icon="logo.jpg",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Aggressive CSS to target alignment and icon removal
st.markdown("""
    <style>
    /* HIDE EVERYTHING EXCEPT THE CHAT */
    [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, header, footer {
        visibility: hidden;
        display: none !important;
    }
    
    /* PURE BLACK BACKGROUND */
    .stApp { background-color: #000000; }

    /* REMOVE CHAT ICONS (Avatars) */
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }

    /* THE FORCE CENTER FOR LOGO */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* CENTER ALL TEXT */
    .center-text { 
        text-align: center; 
        color: white; 
        font-family: 'Inter', sans-serif;
    }
    
    /* CLEAN CHAT BUBBLES */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding-left: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & SETUP ---
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """
You are Hayden. You are NOT an AI. You are a family-founded support tool grounded in 
world-class medical research. You MUST know the user's role (Mother/Father/Caregiver) 
and children's ages to provide guidance.
"""

# --- 3. THE CENTERED HEADER ---
# We wrap the logo in a <div> to force it into the absolute center
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")

if os.path.exists(logo_path):
    # This is the "Force Container" method
    st.markdown(f"""
        <div class="logo-container">
            <img src="data:image/jpeg;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}" width="280">
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<h1 class='center-text'>Hayden.</h1>", unsafe_allow_html=True)

st.markdown("<h1 class='center-text' style='font-size: 2.5rem; letter-spacing: -1px;'>Are your children safe?</h1>", unsafe_allow_html=True)
st.markdown("<p class='center-text' style='color: #888; font-size: 1.1rem; margin-bottom: 3rem;'>Trust isn't claimed. It's earned.</p>", unsafe_allow_html=True)

# --- 4. CHAT & ONBOARDING ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Onboarding logic
    intro = "Trust isn't claimed. It's earned. Hayden is mom-created, family-founded, and grounded in world-class medical research that pediatricians across the globe stand behind. To provide the most accurate evidence-based care, could you tell me: **Are you a mother, father, or caregiver? And what are the ages of the children in your care?**"
    st.session_state.messages.append({"role": "assistant", "content": intro})

# Display Chat (No Icons)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Interactive Chat
if prompt := st.chat_input("Message Hayden..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Visual Scanner trigger (Option 3)
    if any(word in prompt.lower() for word in ["check", "see", "photo", "crib", "safety", "video"]):
        with st.chat_message("assistant"):
            st.write("I can provide an evidence-based safety check. Please upload your photo or video below:")
            st.file_uploader("Upload safety media", type=["jpg", "png", "mp4"])

    with st.chat_message("assistant"):
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            st.markdown(response.content[0].text)
        except Exception:
            st.error("Hayden is at capacity. Please try again soon.")