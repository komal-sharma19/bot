import os
import tempfile
import asyncio
import uuid
import pytz

import edge_tts  # type: ignore
import streamlit as st  # type: ignore
from dotenv import load_dotenv  # type: ignore
from langdetect import detect  # type: ignore
from groq import Groq  # type: ignore
from tools import get_tool_schemas, dispatch_tool_call
import json

# -----------------------------
# Init
# -----------------------------
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="SkillVerse",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

COUNTRY_LANGUAGE_MAP = {
    "India": {
        "English": "en",
        "Hindi": "hi",
        "Marathi": "mr",
        "Gujarati": "gu",
        "Kannada": "kn",
        "Rajasthani": "raj",
        "Bhojpuri": "bho",
    },
    "Germany": {
        "German": "de",
    },
    "France": {
        "French": "fr",
    },
    "Italy": {
        "Italian": "it",
    },
    "Switzerland": {
        "Romansh": "rm",
    },
}

# -----------------------------
# Custom Styling
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 45%, #fdf2f8 100%);
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }

    .hero-card {
        background: rgba(255,255,255,0.72);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.5);
        padding: 28px 30px;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.35rem;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: #475569;
        line-height: 1.6;
    }

    .section-label {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #7c3aed;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .chat-shell {
        background: rgba(255,255,255,0.62);
        border: 1px solid rgba(255,255,255,0.45);
        backdrop-filter: blur(14px);
        border-radius: 24px;
        padding: 18px;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
        min-height: 62vh;
    }

    .user-bubble {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        padding: 14px 16px;
        border-radius: 18px 18px 6px 18px;
        margin: 10px 0 10px auto;
        max-width: 78%;
        width: fit-content;
        box-shadow: 0 8px 18px rgba(79, 70, 229, 0.22);
        font-size: 0.98rem;
        line-height: 1.5;
    }

    .bot-bubble {
        background: #ffffff;
        color: #1e293b;
        padding: 14px 16px;
        border-radius: 18px 18px 18px 6px;
        margin: 10px auto 10px 0;
        max-width: 78%;
        width: fit-content;
        border: 1px solid #e2e8f0;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
        font-size: 0.98rem;
        line-height: 1.5;
    }

    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #64748b;
    }

    .empty-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 0.4rem;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 1rem;
        justify-content: center;
    }

    .chip {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 10px 14px;
        border-radius: 999px;
        color: #334155;
        font-size: 0.92rem;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        border-right: 1px solid #e5e7eb;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .sidebar-brand {
        padding: 0.4rem 0.2rem 1rem 0.2rem;
        margin-bottom: 0.6rem;
    }

    .sidebar-brand-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.25rem;
        letter-spacing: -0.5px;
    }

    .sidebar-brand-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        line-height: 1.5;
    }

    .sidebar-card {
        background: rgba(255,255,255,0.88);
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 16px 14px 14px 14px;
        margin-bottom: 14px;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
    }

    .sidebar-heading {
        font-size: 0.98rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 12px;
    }

    section[data-testid="stSidebar"] label {
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #334155 !important;
    }

    section[data-testid="stSidebar"] .stSelectbox,
    section[data-testid="stSidebar"] .stRadio,
    section[data-testid="stSidebar"] .stCheckbox {
        margin-bottom: 0.55rem;
    }

    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        border-radius: 12px !important;
        height: 42px;
        border: 1px solid #d1d5db !important;
        background: white !important;
        color: #0f172a !important;
        font-weight: 600 !important;
    }

    .sidebar-footer {
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid #e5e7eb;
        font-size: 0.82rem;
        color: #64748b;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)



# NOTE: Some voices may not exist on all systems.
# If any voice fails, we fall back to English.
VOICE_MAP = {
    "en": "en-IN-NeerjaNeural",
    "hi": "hi-IN-SwaraNeural",
    "mr": "mr-IN-AarohiNeural",
    "gu": "gu-IN-DhwaniNeural",
    "kn": "kn-IN-SapnaNeural",
    "de": "de-DE-KatjaNeural",
    "fr": "fr-FR-DeniseNeural",
    "it": "it-IT-ElsaNeural",

    # fallbacks
    "rm": "de-DE-KatjaNeural",
    "bho": "hi-IN-SwaraNeural",
    "raj": "hi-IN-SwaraNeural",
}

def get_voice_for_lang(lang_code: str) -> str:
    return VOICE_MAP.get(lang_code, "en-IN-NeerjaNeural")

async def _tts_save_async(text: str, voice: str, out_path: str):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(out_path)

def tts_to_mp3(text: str, lang_code: str) -> str:
    """
    Generate TTS mp3 and return the file path.
    Handles environments where an event loop may already be running.
    """
    voice = get_voice_for_lang(lang_code)
    out_path = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex}.mp3")

    try:
        asyncio.run(_tts_save_async(text, voice, out_path))
    except RuntimeError:
        # If an event loop is already running, create a new loop
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_tts_save_async(text, voice, out_path))
        finally:
            loop.close()

    return out_path

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.markdown("""
<div style="
    padding: 6px 4px 14px 4px;
    margin-bottom: 8px;
">
    <div style="
        font-size: 2.35rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 4px;
    ">💬 SkillVerse</div>
    <div style="
        font-size: 0.88rem;
        color: #64748b;
        line-height: 1.5;
    ">
        Your multilingual chat companion
    </div>
</div>
""", unsafe_allow_html=True)

#st.sidebar.markdown('<div class="sidebar-card"><div class="sidebar-heading">🌐 Language & Model</div>', unsafe_allow_html=True)

selected_country = st.sidebar.selectbox(
    "Select country",
    list(COUNTRY_LANGUAGE_MAP.keys()),
    index=0
)

available_languages = COUNTRY_LANGUAGE_MAP[selected_country]

ui_language_name = st.sidebar.selectbox(
    "Select language",
    list(available_languages.keys()),
    index=0
)

ui_language_code = available_languages[ui_language_name]

auto_detect = st.sidebar.checkbox("Auto-detect user input language", value=True)

model = st.sidebar.selectbox(
    "Model",
    [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ],
    index=0,
)

#st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-card"><div class="sidebar-heading">Interaction</div>', unsafe_allow_html=True)

input_mode = st.sidebar.radio("Input Mode", ["Text", "Voice"], index=0)
voice_output = st.sidebar.checkbox("Voice output (TTS)", value=True)
typing_effect = st.sidebar.checkbox("Typing effect (stream)", value=True)

st.sidebar.markdown('</div>', unsafe_allow_html=True)

#st.sidebar.markdown('<div class="sidebar-card"><div class="sidebar-heading">🧹 Session</div>', unsafe_allow_html=True)
clear_chat = st.sidebar.button("Clear conversation", use_container_width=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Session state
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "pending_reply" not in st.session_state:
    st.session_state.pending_reply = False

if "last_audio_bytes" not in st.session_state:
    st.session_state.last_audio_bytes = None
    
if "latest_tts_audio" not in st.session_state:
    st.session_state.latest_tts_audio = None
    
    

def build_system_prompt(target_lang_name: str, target_lang_code: str) -> str:
    return f"""
You are a helpful multilingual assistant.

CRITICAL RULE:
- Always reply ONLY in {target_lang_name} (language code: {target_lang_code}).
- Even if the user writes in a different language, you MUST still reply in {target_lang_name}.
- If the user asks about current time or date, use the get_current_time tool.
- If the user asks for math or calculation, you MUST use the available calculator tool.
- Do not invent tool arguments unless required by the tool schema.

OUTPUT RULES:
- Your reply MUST be in {target_lang_name}.
- Your reply MUST be concise and to the point.
- Avoid using special symbols like #, *, _, `, >, [], (), {{}}.
- Your response should be in natural spoken sentences.

Other rules:
- Use tools whenever real-time information is required.
- Sound warm, natural, and conversational.
- Avoid robotic phrasing.
- Reply like a helpful human assistant.
- Use short, friendly sentences unless detail is needed.
- Keep answers clear and structured.
- If user asks for translation, translate accurately.
- If the user message is unclear, ask 1 short clarifying question (in {target_lang_name}).
- If user asks for code, provide code snippets in markdown with proper syntax highlighting and comments in {target_lang_name}.
""".strip()

def run_agent_with_tools(messages_for_api, model, tools, temperature=0.3):
    """
    Agent loop:
    1. First call the model with tools enabled
    2. If the model calls a tool → execute it
    3. Send tool result back to model
    4. Stream final response
    """

    # STEP 1: Ask model if it wants to use tools
    resp = client.chat.completions.create(
        model=model,
        messages=messages_for_api,
        tools=tools,
        tool_choice="auto",
        temperature=temperature,
    )

    msg = resp.choices[0].message

    # STEP 2: If tool was requested
    if getattr(msg, "tool_calls", None):

        messages_for_api.append(msg)

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            raw_args = tc.function.arguments

            if not raw_args:
                args = {}
            else:
                args = json.loads(raw_args)
                if args is None:
                    args = {}

            # Run Python tool
            result = dispatch_tool_call(tool_name, args)

            # Send result back to model
            messages_for_api.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, ensure_ascii=False)
            })

    # STEP 3: Stream final answer
    stream = client.chat.completions.create(
        model=model,
        messages=messages_for_api,
        temperature=temperature,
        stream=True
    )

    return stream

# -----------------------------
# Show chat history
# -----------------------------
# st.markdown('<div class="chat-shell">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-title">Start a more natural conversation</div>
        <div>Ask questions, translate text, check the current time, solve math, write emails, explain topics, or talk using voice — all in your preferred language.</div>
        <div class="chip-row">
            <div class="chip">Translate this to Hindi</div>
            <div class="chip">What’s the current time?</div>
            <div class="chip">Help me write a professional email</div>
            <div class="chip">Explain this in simple words</div>
            <div class="chip">Solve 25 × 4</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
            
            
if voice_output and st.session_state.latest_tts_audio:
    st.audio(st.session_state.latest_tts_audio, format="audio/mp3", autoplay=True)

#st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Input (User chooses Text or Voice)
# -----------------------------
user_text = None

if input_mode == "Voice":
    st.caption("🎙️ Speak your message")

    audio_file = st.audio_input("Tap mic and speak", sample_rate=16000, key="voice_input")

    if audio_file is not None:

        raw = audio_file.getvalue()

        # prevent processing same audio again
        if raw != st.session_state.last_audio_bytes:

            st.session_state.last_audio_bytes = raw

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(raw)
                audio_path = f.name

            with st.spinner("Transcribing audio..."):
                transcription = client.audio.transcriptions.create(
                    file=open(audio_path, "rb"),
                    model="whisper-large-v3-turbo",
                )

            user_text = transcription.text

            st.info(f"Transcribed: {user_text}")

else:
    user_text = st.chat_input("Message SkillVerse... ask, translate, or speak naturally", key="typed_chat_input")

# -----------------------------
# Chat completion flow
# -----------------------------

# Step 1: when user sends a message, save it and rerun immediately
if user_text and not st.session_state.pending_reply:
    st.session_state.messages.append({"role": "user", "content": user_text})
    st.session_state.pending_reply = True
    st.rerun()

# Step 2: after rerun, generate assistant reply
if st.session_state.pending_reply:
    last_user_message = st.session_state.messages[-1]["content"]

    detected = None
    if auto_detect:
        try:
            detected = detect(last_user_message)
        except Exception:
            detected = None

    system_prompt = build_system_prompt(ui_language_name, ui_language_code)

    detection_hint = ""
    if auto_detect and detected:
        detection_hint = f"\n(Developer note: detected input language: {detected})"

    messages_for_api = [{"role": "system", "content": system_prompt + detection_hint}]
    messages_for_api += st.session_state.messages[-8:]
    messages_for_api.append({
        "role": "system",
        "content": f"FINAL INSTRUCTION: Reply ONLY in {ui_language_name}."
    })

    tools = get_tool_schemas()

    assistant_box = st.empty()
    collected = ""

    with st.spinner("Thinking..."):
        if typing_effect:
            stream = run_agent_with_tools(
                messages_for_api=messages_for_api,
                model=model,
                tools=tools,
                temperature=0.3,
            )

            for chunk in stream:
                delta = ""
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta.content or ""
                if delta:
                    collected += delta
                    assistant_box.markdown(
                        f'<div class="bot-bubble">{collected}</div>',
                        unsafe_allow_html=True
                    )

            answer = collected.strip()

        else:
            resp = client.chat.completions.create(
                model=model,
                messages=messages_for_api,
                tools=tools,
                tool_choice="auto",
                temperature=0.3,
            )

            msg = resp.choices[0].message

            if getattr(msg, "tool_calls", None):
                messages_for_api.append(msg)

                for tc in msg.tool_calls:
                    tool_name = tc.function.name
                    args = json.loads(tc.function.arguments or "{}")

                    result = dispatch_tool_call(tool_name, args)

                    messages_for_api.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })

                resp = client.chat.completions.create(
                    model=model,
                    messages=messages_for_api,
                    temperature=0.3,
                )
                answer = resp.choices[0].message.content.strip()
            else:
                answer = msg.content.strip()

            assistant_box.markdown(
                f'<div class="bot-bubble">{answer}</div>',
                unsafe_allow_html=True
            )

        if voice_output and answer:
            try:
                mp3_path = tts_to_mp3(answer, ui_language_code)
                with open(mp3_path, "rb") as f:
                    st.session_state.latest_tts_audio = f.read()                
            except Exception as e:
                st.warning(f"TTS failed: {e}")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.pending_reply = False    
    st.rerun()
# -----------------------------
# Clear chat
# -----------------------------
if clear_chat:
    st.session_state.messages = []
    st.session_state.pending_reply = False
    st.session_state.latest_tts_audio = None
    st.rerun()