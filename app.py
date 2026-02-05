import streamlit as st
import anthropic
import base64
import os

# --- BRANDING ---
st.set_page_config(page_title="Hayden", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<style>.stApp { background-color: #000000; } .center-text { text-align: center; color: white; }</style>", unsafe_allow_html=True)

# --- THE HANDSHAKE ---
if "ANTHROPIC_API_KEY" not in st.secrets:
    st.error("MISSING KEY: Go to Streamlit Settings > Secrets and add: ANTHROPIC_API_KEY = 'your-key'")
    st.stop()

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# --- HEADER ---
st.markdown("<h1 class='center-text'>Hayden Status Check</h1>", unsafe_allow_html=True)

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hi! I'm Hayden. Type 'test' to check my connection."})

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Using the absolute most basic model to guarantee a response
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.content[0].text
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            # THIS IS THE KEY: It will print the EXACT error in red
            st.error(f"DETAILED ERROR: {str(e)}")