import streamlit as st
import anthropic
import base64
import os

# --- 1. BRANDED DESIGN ---
st.set_page_config(page_title="Hayden", page_icon="logo.jpg", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, header, footer { visibility: hidden; display: none !important; }
    .stApp { background-color: #000000; }
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { display: none !important; }
    .logo-container { display: flex; justify-content: center; align-items: center; width: 100%; padding-top: 2rem; padding-bottom: 2rem; }
    .center-text { text-align: center; color: white; }
    [data-testid="stChatMessage"] { background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE CONNECTION ---
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# --- 3. HEADER ---
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if os.path.exists(logo_path):
    st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}" width="280"></div>', unsafe_allow_html=True)

st.markdown("<h1 class='center-text'>Are your children safe?</h1>", unsafe_allow_html=True)

# --- 4. ONBOARDING ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    intro = "Hi, I am Hayden—nice to meet you! My purpose is to help you answer questions after you have passed the Hayden Childcare Certification. **How would you like me to address you?**"
    st.session_state.messages.append({"role": "assistant", "content": intro})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. THE STRIPPED-DOWN CHAT ---
if prompt := st.chat_input("Message Hayden..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    
    with st.chat_message("assistant"):
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
                # FORCING CLAUDE 3 HAIKU (Most stable for Tier 1)
                api_response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = api_response.content[0].text
            except Exception as e:
                st.error(f"Error Details: {str(e)}")
                response = "Connection issue. Please check your API key in Secrets."
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})