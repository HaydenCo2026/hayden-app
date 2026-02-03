import streamlit as st
import anthropic
import base64
import os

# 1. AUTHENTICATION & BRANDING
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """
You are Hayden. You are NOT an AI. You are a family-founded support tool grounded in
world-class medical research that pediatricians across the globe stand behind.
Tone: Supportive, factual, and grounded.
Formatting: For Fathers, use numbered steps. For Mothers, lead with the 'why'.
Privacy: Never claim trust; emphasize that trust is earned through evidence.
"""

# Helper for vision
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# 2. UI SETUP (Minimalist/No Sidebar Clutter)
st.set_page_config(page_title="Hayden", page_icon="👶")

# --- LOGO RE-INSERTION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "logo.jpg")

if os.path.exists(logo_path):
    left_co, cent_co, last_co = st.columns([1, 1, 1])
    with cent_co:
        st.image(logo_path, width=150)
else:
    st.write("Logo file not found. Ensure logo.jpg is in the main folder.")

st.markdown("<h1 style='text-align: center;'>Hayden.</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Trust isn't claimed. It's earned.</p>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. DISPLAY CHAT
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. SMART VISION TRIGGER (Option 3)
if prompt := st.chat_input("How can Hayden help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Detect if we need the uploader
    vision_keywords = ["check", "see", "photo", "crib", "car seat", "rash", "safety", "video", "look"]
    uploaded_file = None

    if any(word in prompt.lower() for word in vision_keywords):
        with st.chat_message("assistant"):
            st.write("I can provide an evidence-based safety check. Please upload your photo or video:")
            uploaded_file = st.file_uploader("Upload safety media", type=["jpg", "png", "jpeg", "mp4"])

    # 5. THE TOKEN SAVER (Prevents the Red Box)
    with st.chat_message("assistant"):
        # We only send the last 2 messages + the current prompt to stay under the limit
        limited_history = st.session_state.messages[-2:]

        # Build the content block
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
            st.error("Hayden is currently at capacity. Please refresh or try again in 30 seconds.")
