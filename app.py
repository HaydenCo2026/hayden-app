import os
import base64
import streamlit as st
import anthropic
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- DATA LOADING ---

def read_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    import pypdf
    text = ""
    with open(file_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def read_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    import docx
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def read_txt(file_path: str) -> str:
    """Read text from a plain text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_context(data_folder: str = "data") -> str:
    """Load all documents from the data folder into a single context string."""
    context_parts = []
    data_path = Path(data_folder)

    if not data_path.exists():
        st.warning(f"Data folder '{data_folder}' not found. Creating it...")
        data_path.mkdir(parents=True, exist_ok=True)
        return ""

    for file_path in data_path.iterdir():
        if file_path.is_file():
            suffix = file_path.suffix.lower()
            try:
                if suffix == ".pdf":
                    content = read_pdf(str(file_path))
                elif suffix == ".docx":
                    content = read_docx(str(file_path))
                elif suffix == ".txt":
                    content = read_txt(str(file_path))
                else:
                    continue

                if content.strip():
                    context_parts.append(f"--- {file_path.name} ---\n{content}")
            except Exception as e:
                st.error(f"Error reading {file_path.name}: {e}")

    return "\n\n".join(context_parts)


# --- CLAUDE API ---

def get_claude_response(user_query: str, context: str, image_base64: str = None) -> str:
    """Get a personalized answer from Claude using the provided context and optional image."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    profile = st.session_state.user_data

    # Capture age context
    child_age = profile.get('child_age', 'unknown')
    caregiver_age = profile.get('user_age', 'unknown')
    caregiver_name = profile.get('name', 'User')

    # Define persona based on specific role
    role_lower = profile['role'].lower()

    if any(word in role_lower for word in ["father", "dad", "papa"]):
        persona_instruction = """
        TONE: Calm, objective, and father-centric.
        STRUCTURE: Use numerical steps, data points, and logic-based outcomes.
        LANGUAGE: Focus on 'Mission/Action'—what are the specific 1, 2, 3 steps to take?
        """
    elif any(word in role_lower for word in ["mother", "mom", "mama"]):
        persona_instruction = """
        TONE: Empathetic, reassuring, and mother-centric.
        STRUCTURE: Use reason-based logic. Explain the 'Why' behind the protocol.
        LANGUAGE: Focus on 'Reasoning/Observation'—connect the child's symptoms to the logic of the care required.
        """
    else:
        persona_instruction = """
        TONE: Professional and protocol-oriented.
        STRUCTURE: Clear, direct certification standards.
        LANGUAGE: Focus on 'Compliance/Safety'—address the child as 'the child in your care'.
        """

    system_instruction = f"""
    You are Hayden, a personalized Childcare Certification Support assistant.

    PRIMARY FILTER:
    The user's child is {child_age} old.
    You MUST prioritize sections of the context that apply to this specific age.
    If the context provides advice for 'Newborns' and the child is '3.5 years old', you must IGNORE
    the newborn advice and look for toddler-specific protocols.

    USER PROFILE:
    - Caregiver: {caregiver_name} (Age: {caregiver_age})
    - Role: {profile['role']}
    - Child Age: {child_age}

    STYLE/TONE RULES:
    {persona_instruction}

    RESPONSE STRUCTURE:
    Return your response using '|||' as a delimiter in exactly this order:
    PART 1 (Medical Script): A 2-sentence script for a doctor, OR 'NONE' if no escalation is needed.
    PART 2 (Rationale): The evidence-based reasoning for a {child_age} old.
    PART 3 (Protocol): The step-by-step instructions (Father: Numerical, Mother: Reason-based).

    IMPORTANT: Never use the word 'advice'. Use 'Evidence-Based Guidance'.

    VISUAL ANALYSIS:
    If an image is provided, analyze it specifically for safety hazards or symptoms mentioned in the curriculum.
    Cross-reference the visual evidence (e.g., 'red raised bumps') against the Evidence-Based Reasoning in the context.

    FACTUAL GROUNDING:
    Answer ONLY using the provided PROPRIETARY CONTEXT. If no age-appropriate
    information exists for a {child_age} old, reply 'NOT_FOUND'.

    PROPRIETARY CONTEXT:
    {context}
    """

    # Build message content (text + optional image)
    messages = []
    if image_base64:
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64,
                    },
                },
                {"type": "text", "text": user_query},
            ],
        })
    else:
        messages.append({"role": "user", "content": user_query})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_instruction,
        messages=messages,
    )

    raw = response.content[0].text

    # Parse structured response
    if raw.strip() == "NOT_FOUND":
        return raw

    parts = raw.split("|||")
    formatted = ""

    if len(parts) >= 3:
        medical_script = parts[0].strip()
        rationale = parts[1].strip()
        protocol = parts[2].strip()

        # Only show medical script if escalation is needed
        if medical_script.upper() != "NONE":
            formatted += f"**Communication for your Medical Professional:**\n{medical_script}\n\n---\n\n"

        formatted += f"**Evidence-Based Rationale:**\n{rationale}\n\n"
        formatted += f"**Protocol:**\n{protocol}"
    else:
        # Fallback if Claude didn't use the delimiter
        formatted = raw

    return formatted


# --- FALLBACK LOGIC ---

def handle_not_found(query: str):
    """Handle NOT_FOUND responses with branded message and email simulation."""
    profile = st.session_state.user_data

    st.markdown(
        f"**Hayden:** Let me get back to you, {profile['name']}! "
        "I don't have that specific information in my current curriculum, "
        "so I've forwarded your question to our expert team at Hayden."
    )

    email_body = f"""
    -----------------------------------------
    NEW INQUIRY FOR TEAM HAYDEN
    -----------------------------------------
    FROM: {profile['name']} ({profile['role']})
    CAREGIVER AGE: {profile['user_age']}
    CHILD CONTEXT: {profile['child_age']}
    SPECIFIC NEEDS: {profile['needs']}

    USER QUESTION: "{query}"
    -----------------------------------------
    """
    print(email_body)


# --- STREAMLIT UI ---

st.set_page_config(
    page_title="Hayden | Child Safety & Care",
    page_icon="logo.jpg",
    layout="centered",
)

# Custom CSS for seamless black theme and hidden avatars
st.markdown("""
    <style>
    /* Hide default Streamlit chat avatars */
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="stChatMessageAvatarUser"] {
        display: none;
    }

    /* Full width messages since icons are gone */
    [data-testid="stChatMessageContent"] {
        margin-left: 0px;
    }

    .stApp {
        background-color: #000000;
    }
    [data-testid="stHeader"] {
        background-color: #000000;
    }

    /* White text for contrast */
    .stMarkdown, .stTitle, .stCaption, p, h1, h2, h3, span {
        color: #FFFFFF !important;
    }

    [data-testid="stImage"] {
        background-color: #000000;
    }
    [data-testid="stImage"] img {
        background-color: #000000;
    }

    [data-testid="stChatMessage"] {
        background-color: #1a1a1a;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Display logo
st.image("logo.jpg", width=150)

st.title("Welcome to Hayden")
st.caption("Childcare Certification Support")

# --- PHOTO SUPPORT SIDEBAR ---
with st.sidebar:
    st.header("Visual Safety Check")
    uploaded_file = st.file_uploader(
        "Upload a photo of a rash, product, or safety concern",
        type=["jpg", "jpeg", "png"],
    )
    camera_photo = st.camera_input("Take a photo")

image_to_process = uploaded_file if uploaded_file else camera_photo

if "current_image" not in st.session_state:
    st.session_state.current_image = None

if image_to_process:
    bytes_data = image_to_process.getvalue()
    st.session_state.current_image = base64.b64encode(bytes_data).decode("utf-8")
    st.success("Photo received! Ask Hayden your question about this image below.")

# --- SESSION STATE INITIALIZATION ---
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 0
    st.session_state.onboarding_complete = False
    st.session_state.user_data = {}
    st.session_state.onboarding_messages = []

# Load context once
if "context" not in st.session_state:
    with st.spinner("Loading knowledge base..."):
        st.session_state.context = load_context()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Onboarding question sequence
ONBOARDING_QUESTIONS = [
    "Welcome to Hayden: Certified Caregiver Support. What would you like to be called while you are here?",
    "What is your role with caring for the child? (e.g., Parent, Nanny, Grandparent)",
    "How old are you? (This helps me provide age-appropriate advice for you as well.)",
    "How old is the child (or children) you are caring for?",
    "Are there specific safety or care needs we should focus on? (e.g., allergies, mobility concerns, specific milestones)",
]
ONBOARDING_KEYS = ["name", "role", "user_age", "child_age", "needs"]
TOTAL_STEPS = len(ONBOARDING_QUESTIONS)

# --- ONBOARDING UI (conversational with progress bar) ---
if not st.session_state.onboarding_complete:
    # Progress bar
    progress_value = st.session_state.onboarding_step / TOTAL_STEPS
    progress_percentage = int(progress_value * 100)
    st.progress(progress_value, text=f"Profile Setup: {progress_percentage}% Complete")

    # Display conversation history so far
    for i, msg in enumerate(st.session_state.onboarding_messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                # No label for the very first welcome message
                label = "" if i == 0 else "**Hayden:** "
                st.markdown(f"{label}{msg['content']}")

    # Ask the current question
    current_idx = st.session_state.onboarding_step
    if current_idx < TOTAL_STEPS:
        with st.chat_message("assistant"):
            # No label for the first question (welcome message)
            if current_idx == 0:
                st.markdown(ONBOARDING_QUESTIONS[current_idx])
            else:
                st.markdown(f"**Hayden:** {ONBOARDING_QUESTIONS[current_idx]}")

        # Capture the response
        if user_input := st.chat_input("Type your response..."):
            # Store in conversation history
            st.session_state.onboarding_messages.append(
                {"role": "assistant", "content": ONBOARDING_QUESTIONS[current_idx]}
            )
            st.session_state.onboarding_messages.append(
                {"role": "user", "content": user_input}
            )

            # Store the data
            st.session_state.user_data[ONBOARDING_KEYS[current_idx]] = user_input

            # Advance to next question
            st.session_state.onboarding_step += 1

            # If that was the last question, mark complete
            if st.session_state.onboarding_step >= TOTAL_STEPS:
                st.session_state.onboarding_complete = True

            st.rerun()

# --- MAIN CHAT INTERFACE ---
else:
    st.success("Profile Complete! Hayden is now customized for your needs.")

    if not st.session_state.context:
        st.info("No documents found in the 'data/' folder. Add PDF, DOCX, or TXT files to get started.")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            label = "You: " if message["role"] == "user" else "Hayden: "
            st.markdown(f"**{label}** {message['content']}")

    # Chat input
    if prompt := st.chat_input("Ask a safety question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"**You:** {prompt}")

        if not st.session_state.context:
            with st.chat_message("assistant"):
                response = "No knowledge base loaded. Please add documents to the 'data/' folder."
                st.markdown(f"**Hayden:** {response}")
        else:
            with st.spinner("Thinking..."):
                try:
                    response = get_claude_response(
                        prompt, st.session_state.context, st.session_state.current_image
                    )
                    # Clear image after use
                    st.session_state.current_image = None
                except Exception as e:
                    response = f"Error: {e}"

            if response.strip() == "NOT_FOUND":
                with st.chat_message("assistant"):
                    handle_not_found(prompt)
                response = f"Let me get back to you, {st.session_state.user_data['name']}! I don't have that specific information in my current curriculum, so I've forwarded your question to our expert team at Hayden."
            else:
                with st.chat_message("assistant"):
                    st.markdown(f"**Hayden:** {response}")

        st.session_state.messages.append({"role": "assistant", "content": response})
