import streamlit as st
import anthropic
import base64
import os

# --- 1. DESIGN & BRANDING ---
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

# --- 2. THE HANDSHAKE ---
# If this fails, the red box will contain a "Detailed Status"
try:
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
except Exception as e:
    st.error(f"AUTHENTICATION ERROR: Check your Streamlit Secrets. {str(e)}")
    st.stop()

SYSTEM_PROMPT = "You are Hayden. Only reference evidence-based curriculum from the Hayden Childcare Certification."

# --- 3. HEADER & LOGO ---
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{data}" width="280"></div>', unsafe_allow_html=True)

st.markdown("<h1 class='center-text'>Are your children safe?</h1>", unsafe_allow_html=True)

# --- 4. ONBOARDING & CHAT ---
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
        # MODEL SELECTION: 2026 Tier 1 standard
        current_model = "claude-3-5-sonnet-latest"
        
        if msg_count == 1:
            response = "Thank you. And **what is your role** (Mother, Father, or Caregiver)?"
        elif msg_count == 2:
            response = "Understood. **How old are you?**"
        elif msg_count == 3:
            response = "**Who is in your care, and how old are they?**"
        elif msg_count == 4:
            response = "**What is your main concern today?**"
        else:
            try:
                # The Request
                api_response = client.messages.create(
                    model=current_model,
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = api_response.content[0].text
            except Exception as e:
                # THIS WILL KILL THE SILENT RED BOX:
                st.error(f"HAYDEN SYSTEM STATUS: {str(e)}")
                response = "I am currently updating my records. Please try again in 30 seconds."
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})