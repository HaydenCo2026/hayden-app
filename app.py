import streamlit as st
import anthropic
import base64
import os

# --- 1. DESIGN & BRANDING (Logo and Center Styling) ---
st.set_page_config(page_title="Hayden", page_icon="logo.jpg", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, header, footer {
        visibility: hidden; display: none !important;
    }
    .stApp { background-color: #000000; }
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    .logo-container {
        display: flex; justify-content: center; align-items: center;
        width: 100%; padding-top: 2rem; padding-bottom: 2rem;
    }
    .center-text { text-align: center; color: white; font-family: 'Inter', sans-serif; }
    [data-testid="stChatMessage"] { background-color: transparent !important; padding-left: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE CONNECTION ---
if "ANTHROPIC_API_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
SYSTEM_PROMPT = "You are Hayden. Only reference evidence-based curriculum from the Hayden Childcare Certification."

# --- 3. THE HEADER LOGO ---
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{data}" width="280"></div>', unsafe_allow_html=True)

st.markdown("<h1 class='center-text'>Are your children safe?</h1>", unsafe_allow_html=True)

# --- 4. THE ONBOARDING LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    intro = (
        "Hi, I am Hayden—nice to meet you! My purpose is to help you answer questions "
        "after you have passed the Hayden Childcare Certification. Let's get started. "
        "**How would you like me to address you?**"
    )
    st.session_state.messages.append({"role": "assistant", "content": intro})

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. THE CHAT FLOW ---
if prompt := st.chat_input("Message Hayden..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    
    with st.chat_message("assistant"):
        # UPDATED: Using the 2026-safe models
        current_model = "claude-3-5-haiku-20241022" if msg_count < 5 else "claude-3-5-sonnet-20241022"
        
        if msg_count == 1:
            response = "Thank you. And **what is your role** (Mother, Father, or Caregiver)?"
        elif msg_count == 2:
            response = "Understood. **How old are you?**"
        elif msg_count == 3:
            response = "**Who is in your care, and how old are they?**"
        elif msg_count == 4:
            response = (
                "**What is your main concern today?** \n\n"
                "*I want you to understand that I will only reference evidence-based, medically proven, "
                "and relevant curriculum found in the Hayden Childcare Certification.*"
            )
        else:
            try:
                # The 'Atomic' call: only sends current message to stay under Tier 1 limits
                api_response = client.messages.create(
                    model=current_model,
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = api_response.content[0].text
            except Exception as e:
                st.error(f"Status Check: {str(e)}")
                response = "Hayden is briefly at capacity. Please try again in 30 seconds."
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})