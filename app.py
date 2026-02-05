import streamlit as st
import anthropic
import base64
import os

# --- 1. DESIGN & BRANDING (Force Black/Centered) ---
st.set_page_config(page_title="Hayden", page_icon="logo.jpg", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, header, footer { visibility: hidden; display: none !important; }
    .stApp { background-color: #000000; }
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { display: none !important; }
    .logo-container { display: flex; justify-content: center; align-items: center; width: 100%; padding-top: 2rem; padding-bottom: 2rem; }
    .center-text { text-align: center; color: white; font-family: 'Inter', sans-serif; }
    [data-testid="stChatMessage"] { background-color: transparent !important; padding-left: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Short, punchy prompt to save tokens
SYSTEM_PROMPT = "You are Hayden. Only reference evidence-based curriculum from the Hayden Childcare Certification."

# --- 2. HEADER ---
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if os.path.exists(logo_path):
    st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}" width="280"></div>', unsafe_allow_html=True)

# --- 3. ONBOARDING & CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    intro = "Hi, I am Hayden—nice to meet you! My purpose is to help you answer questions after you have passed the Hayden Childcare Certification. **How would you like me to address you?**"
    st.session_state.messages.append({"role": "assistant", "content": intro})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message Hayden..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])

    with st.chat_message("assistant"):
        # Model selection based on Tier 1 limits
        current_model = "claude-3-haiku-20240307" if msg_count < 5 else "claude-3-5-sonnet-20240620"

        if msg_count == 1:
            response = "Thank you. And **what is your role** (Mother, Father, or Caregiver)?"
        elif msg_count == 2:
            response = "Understood. **How old are you?**"
        elif msg_count == 3:
            response = "**Who is in your care, and how old are they?**"
        elif msg_count == 4:
            response = "**What is your main concern today?**"
        else:
            # TRIGGER FOR PHOTO SCAN
            vision_keywords = ["check", "see", "photo", "crib", "safety", "look"]
            uploaded_file = None
            if any(word in prompt.lower() for word in vision_keywords):
                uploaded_file = st.file_uploader("Upload safety photo/video", type=["jpg", "png", "mp4"])
                response = "I'm ready to review that for you. Please upload the media above."

            try:
                # TOKEN SAVER: We only send the CURRENT message to stay under 30K
                api_response = client.messages.create(
                    model=current_model,
                    max_tokens=800,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = api_response.content[0].text
            except Exception as e:
                # Clearer error for you to see
                st.error(f"Tier 1 Limit Hit: {str(e)}")
                response = "Hayden is briefly at capacity. Please try your question again in 30 seconds."

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
