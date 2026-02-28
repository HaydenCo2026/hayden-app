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
BASE_PROMPT = """You are Hayden. First, try to answer using evidence-based curriculum from the Hayden Childcare Certification.

If the answer is not available in the Hayden Curriculum, do NOT guess or make up an answer. Instead, respond with:
"Based on the Hayden Curriculum, I do not have this specific answer. Are you comfortable with me accessing the wider vetted medical, government and deeply researched findings?"

Only after the user confirms should you provide an answer from broader knowledge sources."""

PARENT_PROMPT = f"""{BASE_PROMPT}

You are speaking with a parent. Use college-level vocabulary and analysis. You can use technical terms,
cite research directly, and provide nuanced explanations. Assume they can handle complexity and want
depth in your answers."""

CAREGIVER_PROMPT = f"""{BASE_PROMPT}

You are speaking with a caregiver. Use clear, accessible language at a 10th-grade reading level.
Avoid jargon and technical terms—if you must use them, explain them simply. Focus on practical,
actionable advice. Keep sentences shorter and explanations straightforward."""

# --- PERSONA-SPECIFIC GUIDANCE ---
PERSONA_GUIDANCE = {
    "nanny": "They are a professional nanny/au pair. Respect their training and experience. Use professional language appropriate for an employer-employee context.",
    "babysitter": "They are a babysitter, possibly younger or less experienced. Keep guidance very simple and actionable. Reassure them they're doing well.",
    "grandparent": "They are a grandparent. Honor their experience while gently sharing current guidelines. They may have outdated knowledge but deep love and investment.",
    "aunt_uncle": "They are an aunt or uncle. They want to do right by their sibling's children. Balance respect for the parents' wishes with practical help.",
    "sibling": "They are an older sibling caring for younger ones. Keep it very simple. They may feel scared or overwhelmed. Encourage them and give clear, easy steps.",
    "daycare": "They work in daycare/childcare. They may be managing multiple children. Focus on efficiency and group management tips.",
    "foster": "They are a foster parent. Be sensitive to trauma-informed care. They may be navigating complex systems and building trust with the child.",
    "stepparent": "They are a stepparent. Be sensitive to blended family dynamics. They may be earning trust and navigating boundaries with biological parents.",
    "family_friend": "They are a godparent or family friend. They want to honor the parents' wishes. Help them feel confident in occasional caregiving.",
    "relative": "They are a live-in relative (cousin, in-law, etc.). They have daily involvement and household dynamics to navigate."
}

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
    st.session_state.onboarding_step = "name"  # name -> role -> persona (caregivers only) -> age -> children -> concern -> chat
    st.session_state.user_profile = {
        "name": None,
        "role": None,           # "parent" or "caregiver"
        "role_title": None,     # Original response (e.g., "Mother", "Nanny")
        "persona": None,        # Specific caregiver type (e.g., "grandparent", "nanny")
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

    step = st.session_state.onboarding_step

    with st.chat_message("assistant"):
        # MODEL SELECTION: FORCED TO HAIKU FOR TESTING
        current_model = "claude-3-haiku-20240307"

        if step == "name":
            st.session_state.user_profile["name"] = prompt.strip()
            st.session_state.onboarding_step = "role"
            response = "Thank you. And **what is your role** (Mother, Father, or Caregiver)?"

        elif step == "role":
            role_input = prompt.lower()
            st.session_state.user_profile["role_title"] = prompt.strip()
            if "mother" in role_input or "father" in role_input or "mom" in role_input or "dad" in role_input or "parent" in role_input:
                st.session_state.user_profile["role"] = "parent"
                st.session_state.onboarding_step = "age"
                response = "Understood. **How old are you?**"
            else:
                st.session_state.user_profile["role"] = "caregiver"
                st.session_state.onboarding_step = "persona"
                response = """Thank you! To better assist you, **which best describes you?**

1. Nanny / Au Pair
2. Babysitter
3. Grandparent
4. Aunt / Uncle
5. Older Sibling
6. Daycare Worker
7. Foster Parent
8. Stepparent
9. Godparent / Family Friend
10. Other Relative (cousin, in-law, etc.)"""

        elif step == "persona":
            # Map response to persona key
            persona_input = prompt.lower()
            if "1" in persona_input or "nanny" in persona_input or "au pair" in persona_input:
                st.session_state.user_profile["persona"] = "nanny"
            elif "2" in persona_input or "babysit" in persona_input:
                st.session_state.user_profile["persona"] = "babysitter"
            elif "3" in persona_input or "grandp" in persona_input or "grandm" in persona_input or "grandf" in persona_input:
                st.session_state.user_profile["persona"] = "grandparent"
            elif "4" in persona_input or "aunt" in persona_input or "uncle" in persona_input:
                st.session_state.user_profile["persona"] = "aunt_uncle"
            elif "5" in persona_input or "sibling" in persona_input or "brother" in persona_input or "sister" in persona_input:
                st.session_state.user_profile["persona"] = "sibling"
            elif "6" in persona_input or "daycare" in persona_input:
                st.session_state.user_profile["persona"] = "daycare"
            elif "7" in persona_input or "foster" in persona_input:
                st.session_state.user_profile["persona"] = "foster"
            elif "8" in persona_input or "step" in persona_input:
                st.session_state.user_profile["persona"] = "stepparent"
            elif "9" in persona_input or "godp" in persona_input or "friend" in persona_input:
                st.session_state.user_profile["persona"] = "family_friend"
            else:
                st.session_state.user_profile["persona"] = "relative"
            st.session_state.onboarding_step = "age"
            response = "Understood. **How old are you?**"

        elif step == "age":
            st.session_state.user_profile["age"] = prompt.strip()
            st.session_state.onboarding_step = "children"
            response = "**Who is in your care, and how old are they?**"

        elif step == "children":
            st.session_state.user_profile["children"] = prompt.strip()
            st.session_state.onboarding_step = "concern"
            response = "**What is your main concern today?**"

        elif step == "concern":
            st.session_state.user_profile["main_concern"] = prompt.strip()
            st.session_state.onboarding_step = "chat"

        if step == "concern" or st.session_state.onboarding_step == "chat":
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
                    # Add persona-specific guidance for caregivers
                    if profile["persona"] and profile["persona"] in PERSONA_GUIDANCE:
                        profile_context += f"\n\nPERSONA GUIDANCE: {PERSONA_GUIDANCE[profile['persona']]}"

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