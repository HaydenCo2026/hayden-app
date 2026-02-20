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
    .user-message { color: #4CAF50 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if "ANTHROPIC_API_KEY" not in st.secrets:
    st.error("MISSING API KEY: Go to Streamlit Settings > Secrets and add your key.")
    st.stop()

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# --- ROLE-BASED SYSTEM PROMPTS ---
BASE_PROMPT = "You are Hayden. Only reference evidence-based curriculum from the Hayden Childcare Certification."

PARENT_PROMPT = f"""{BASE_PROMPT}

You are speaking with a parent. Use college-level vocabulary and analysis. You can use technical terms,
cite research directly, and provide nuanced explanations. Assume they can handle complexity and want
depth in your answers."""

CAREGIVER_PROMPT = f"""{BASE_PROMPT}

You are speaking with a caregiver (this includes nannies, babysitters, grandparents, aunts, uncles,
siblings, or any non-parent caring for a child). Use clear, accessible language at a 10th-grade reading level.
Avoid jargon and technical terms—if you must use them, explain them simply. Focus on practical,
actionable advice. Keep sentences shorter and explanations straightforward."""

# --- 3. THE HEADER LOGO ---
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{data}" width="280"></div>', unsafe_allow_html=True)

st.markdown("<h1 class='center-text'>Are your children safe?</h1>", unsafe_allow_html=True)

# --- 4. ONBOARDING & CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.user_profile = {
        "name": None,
        "role": None,           # "parent" or "caregiver"
        "role_title": None,     # Original response (e.g., "Mother", "Nanny")
        "age": None,
        "children": None,
        "main_concern": None
    }
    intro = "Hi, I am Hayden—nice to meet you! My purpose is to help you answer questions after you have passed the Hayden Childcare Certification. **How would you like me to address you?**"
    st.session_state.messages.append({"role": "assistant", "content": intro})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f'<span class="user-message">{message["content"]}</span>', unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("Message Hayden..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f'<span class="user-message">{prompt}</span>', unsafe_allow_html=True)

    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    
    with st.chat_message("assistant"):
        # MODEL SELECTION: FORCED TO HAIKU FOR TESTING
        current_model = "claude-3-haiku-20240307"
        
        if msg_count == 1:
            # Store name
            st.session_state.user_profile["name"] = prompt.strip()
            response = "Thank you. And **what is your role** (Mother, Father, or Caregiver)?"
        elif msg_count == 2:
            # Detect and store role
            role_input = prompt.lower()
            st.session_state.user_profile["role_title"] = prompt.strip()
            if "mother" in role_input or "father" in role_input or "mom" in role_input or "dad" in role_input or "parent" in role_input:
                st.session_state.user_profile["role"] = "parent"
            else:
                st.session_state.user_profile["role"] = "caregiver"
            response = "Understood. **How old are you?**"
        elif msg_count == 3:
            # Store age
            st.session_state.user_profile["age"] = prompt.strip()
            response = "**Who is in your care, and how old are they?**"
        elif msg_count == 4:
            # Store children info
            st.session_state.user_profile["children"] = prompt.strip()
            response = "**What is your main concern today?**"
        elif msg_count == 5:
            # Store main concern and give first AI response
            st.session_state.user_profile["main_concern"] = prompt.strip()
        if msg_count >= 5:
            try:
                # Build profile context
                profile = st.session_state.user_profile
                profile_context = f"""
USER PROFILE:
- Name: {profile['name']}
- Role: {profile['role_title']}
- Age: {profile['age']}
- Children in care: {profile['children']}
- Main concern: {profile['main_concern']}

Always address the user by their name ({profile['name']}). Personalize your responses using their profile information."""

                # Select base prompt based on user role
                if profile["role"] == "parent":
                    base_prompt = PARENT_PROMPT
                else:
                    base_prompt = CAREGIVER_PROMPT

                # Combine base prompt with profile context
                system_prompt = f"{base_prompt}\n\n{profile_context}"

                # The Request to Haiku
                api_response = client.messages.create(
                    model=current_model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = api_response.content[0].text
            except Exception as e:
                # This will print the exact reason for the red box on the screen
                st.error(f"HAYDEN TEST STATUS: {str(e)}")
                response = "Connection test in progress..."
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})