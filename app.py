import streamlit as st
import anthropic
import base64
import os

# 1. SETUP & AUTH
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Force a clean, centered layout with a black background
st.set_page_config(
    page_title="Hayden",
    page_icon="logo.jpg",
    layout="centered",
    initial_sidebar_state="collapsed" # Hides the side icons
)

# Custom CSS to force alignment and hide sidebar elements
st.markdown("""
    <style>
    /* Force Black Background */
    .stApp { background-color: #000000; }

    /* Hide the Sidebar entirely */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }

    /* Center and size the Logo */
    [data-testid="stImage"] img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 300px !important;
    }

    /* Center the Text */
    .main-text { text-align: center; color: white; }
    .stChatMessage { background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

SYSTEM_PROMPT = """
You are Hayden. You are NOT an AI. You are a family-founded support tool grounded in
world-class medical research that pediatricians across the globe stand behind.
Tone: Supportive and factual.
Personalization: You MUST know the user's role (Mother/Father/Caregiver) and the ages
of their children to provide safe, evidence-based guidance.
"""

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# --- LOGO & HEADER ---
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if os.path.exists(logo_path):
    st.image(logo_path)

st.markdown("<h1 class='main-text'>Are your children safe?</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-text' style='color: #888; font-size: 1.2rem; margin-bottom: 2rem;'>Trust isn't claimed. It's earned.</p>", unsafe_allow_html=True)

# --- ONBOARDING & CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # The First Step: Identification
    intro = "Trust isn't claimed. It's earned. Hayden is mom-created, family-founded, and grounded in world-class medical research. To provide the most accurate evidence-based care, could you tell me: **Are you a mother, father, or caregiver? And what are the ages of the children in your care?**"
    st.session_state.messages.append({"role": "assistant", "content": intro})

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Interactive Logic
if prompt := st.chat_input("Message Hayden..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Smart Scanner Logic
    vision_keywords = ["check", "see", "photo", "crib", "car seat", "rash", "safety", "video", "look"]
    uploaded_file = None
    if any(word in prompt.lower() for word in vision_keywords):
        with st.chat_message("assistant"):
            st.write("I can provide an evidence-based safety check. Please upload your photo or video:")
            uploaded_file = st.file_uploader("Upload safety media", type=["jpg", "png", "jpeg", "mp4"])

    with st.chat_message("assistant"):
        limited_history = st.session_state.messages[-4:] # Slightly longer to remember role/age
        message_content = [{"type": "text", "text": prompt}]

        if uploaded_file:
            message_content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": "image/jpeg", "data": encode_image(uploaded_file)}
            })

        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": message_content}]
            )
            answer = response.content[0].text
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error("Hayden is currently at capacity. Please try again in 30 seconds.")
