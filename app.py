import streamlit as st
import anthropic
import base64
import os

# 1. AUTH & SETUP
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# --- THE DESIGN FIXES ---
st.set_page_config(
    page_title="Hayden",
    page_icon="logo.jpg", # Fixes Point #4
    layout="centered"
)

# Custom CSS to force a Black Background and Large Logo (Fixes Point #1 & #2)
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
    }
    [data-testid="stImage"] img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 250px !important; /* Forces Logo to be Large */
    }
    .main-text {
        text-align: center;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

SYSTEM_PROMPT = """
You are Hayden. You are NOT an AI. You are a family-founded support tool grounded in
world-class medical research that pediatricians across the globe stand behind.
Tone: Supportive and factual. Never claim trust; emphasize trust is earned through evidence.
"""

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# --- HEADER & INTRO (Fixes Point #3) ---
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if os.path.exists(logo_path):
    st.image(logo_path) # Centered and sized via CSS above

st.markdown("<h1 class='main-text'>Are your children safe?</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-text' style='color: #888; font-size: 1.2rem;'>Trust isn't claimed. It's earned.</p>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial Greeting/Qualification (Fixes Point #3)
    intro = "What qualifies anyone to care for a child? Trust is earned. Hayden is mom-created, family-founded, and grounded in world-class medical research that pediatricians across the globe stand behind. How can I help you today?"
    st.session_state.messages.append({"role": "assistant", "content": intro})

# 2. CHAT DISPLAY
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. INTERACTIVE CHAT
if prompt := st.chat_input("Ask Hayden..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Option 3: Visual Check trigger
    vision_keywords = ["check", "see", "photo", "crib", "car seat", "rash", "safety", "video", "look"]
    uploaded_file = None
    if any(word in prompt.lower() for word in vision_keywords):
        with st.chat_message("assistant"):
            st.write("I can provide an evidence-based safety check. Please upload your photo or video:")
            uploaded_file = st.file_uploader("Upload safety media", type=["jpg", "png", "jpeg", "mp4"])

    with st.chat_message("assistant"):
        limited_history = st.session_state.messages[-2:]
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
