# import asyncio
# import json
# import os
# import tempfile
# import uuid
# from typing import Any

# import edge_tts  # type: ignore
# import streamlit as st  # type: ignore
# from dotenv import load_dotenv  # type: ignore
# from groq import Groq  # type: ignore
# from langdetect import detect  # type: ignore

# from prompts import build_system_prompt
# from style import STYLE
# from tools import dispatch_tool_call, get_tool_schemas


# # -----------------------------
# # App setup
# # -----------------------------
# load_dotenv()
# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# st.set_page_config(
#     page_title="SkillVerse",
#     page_icon="💬",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# COUNTRY_LANGUAGE_MAP = {
#     "India": {
#         "English": "en",
#         "Hindi": "hi",
#         "Marathi": "mr",
#         "Gujarati": "gu",
#         "Kannada": "kn",
#         "Rajasthani": "raj",
#     },
#     "Switzerland": {
#         "Romansh": "rm",
#         "Italian": "it",
#         "French": "fr",
#         "German": "de",
#         "English": "en",
#     },
#     "South Africa": {
#         "English": "en",
#         "Afrikaans": "af",
#         "Zulu": "zu",
#         "Xhosa": "xh",
#     },
# }

# VOICE_MAP = {
#     "en": "en-US-JennyNeural",
#     "hi": "hi-IN-SwaraNeural",
#     "mr": "mr-IN-AarohiNeural",
#     "gu": "gu-IN-DhwaniNeural",
#     "kn": "kn-IN-SapnaNeural",
#     "de": "de-DE-KatjaNeural",
#     "fr": "fr-FR-DeniseNeural",
#     "it": "it-IT-ElsaNeural",
#     "zu": "zu-ZA-ThandoNeural",
#     "xh": "xh-ZA-ThandoNeural",
#     "rm": "de-DE-KatjaNeural",  # fallback to German
#     "raj": "hi-IN-SwaraNeural",  # fallback to Hindi
# }

# st.markdown(STYLE, unsafe_allow_html=True)


# # -----------------------------
# # Helpers
# # -----------------------------
# def get_voice_for_lang(lang_code: str) -> str:
#     return VOICE_MAP.get(lang_code, "en-IN-NeerjaNeural")


# async def _tts_save_async(text: str, voice: str, out_path: str) -> None:
#     communicator = edge_tts.Communicate(text=text, voice=voice)
#     await communicator.save(out_path)


# def tts_to_mp3(text: str, lang_code: str) -> bytes:
#     """Generate TTS bytes for the given text."""
#     voice = get_voice_for_lang(lang_code)
#     out_path = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex}.mp3")

#     try:
#         asyncio.run(_tts_save_async(text, voice, out_path))
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#         try:
#             loop.run_until_complete(_tts_save_async(text, voice, out_path))
#         finally:
#             loop.close()

#     try:
#         with open(out_path, "rb") as file_obj:
#             audio_bytes = file_obj.read()
#     finally:
#         try:
#             os.remove(out_path)
#         except OSError:
#             pass

#     return audio_bytes


# def detect_language_hint(text: str, auto_detect: bool) -> str:
#     if not auto_detect or not text.strip():
#         return ""

#     try:
#         detected = detect(text)
#         return f"\n(Developer note: detected input language: {detected})"
#     except Exception:
#         return ""


# def build_messages(
#     system_prompt: str,
#     history: list[dict[str, Any]],
#     final_language_name: str,
#     detection_hint: str = "",
#     user_message: str | None = None,
# ) -> list[dict[str, Any]]:
#     messages: list[dict[str, Any]] = [
#         {"role": "system", "content": system_prompt + detection_hint}
#     ]
#     messages += history[-8:]

#     if user_message is not None:
#         messages.append({"role": "user", "content": user_message})

#     messages.append(
#         {
#             "role": "system",
#             "content": f"FINAL INSTRUCTION: Reply ONLY in {final_language_name}.",
#         }
#     )
#     return messages


# def run_agent_with_tools(
#     messages_for_api: list[dict[str, Any]],
#     model_name: str,
#     tools: list[dict[str, Any]],
#     temperature: float = 0.3,
# ):
#     """Call the model, execute tool calls if needed, and stream final output."""
#     response = client.chat.completions.create(
#         model=model_name,
#         messages=messages_for_api,
#         tools=tools,
#         tool_choice="auto",
#         temperature=temperature,
#     )

#     message = response.choices[0].message

#     if getattr(message, "tool_calls", None):
#         messages_for_api.append(message)

#         for tool_call in message.tool_calls:
#             tool_name = tool_call.function.name
#             raw_args = tool_call.function.arguments
#             args = json.loads(raw_args) if raw_args else {}
#             if args is None:
#                 args = {}

#             result = dispatch_tool_call(tool_name, args)
#             messages_for_api.append(
#                 {
#                     "role": "tool",
#                     "tool_call_id": tool_call.id,
#                     "content": json.dumps(result, ensure_ascii=False),
#                 }
#             )

#     return client.chat.completions.create(
#         model=model_name,
#         messages=messages_for_api,
#         temperature=temperature,
#         stream=True,
#     )


# def transcribe_audio_bytes(raw_audio: bytes) -> str:
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
#         tmp_file.write(raw_audio)
#         audio_path = tmp_file.name

#     try:
#         with open(audio_path, "rb") as audio_file:
#             transcription = client.audio.transcriptions.create(
#                 file=audio_file,
#                 model="whisper-large-v3-turbo",
#             )
#     finally:
#         try:
#             os.remove(audio_path)
#         except OSError:
#             pass

#     return (transcription.text or "").strip()


# def stream_answer(messages_for_api: list[dict[str, Any]], model_name: str) -> str:
#     tools = get_tool_schemas()
#     stream = run_agent_with_tools(
#         messages_for_api=messages_for_api,
#         model_name=model_name,
#         tools=tools,
#         temperature=0.3,
#     )

#     collected = ""
#     for chunk in stream:
#         delta = ""
#         if chunk.choices and chunk.choices[0].delta:
#             delta = chunk.choices[0].delta.content or ""
#         if delta:
#             collected += delta
#     return collected.strip()


# # -----------------------------
# # Sidebar
# # -----------------------------
# st.sidebar.markdown(
#     """
# <div style="padding: 6px 4px 14px 4px; margin-bottom: 8px;">
#     <div style="font-size: 2.35rem; font-weight: 800; color: #1e293b; margin-bottom: 4px;">💬 SkillVerse</div>
#     <div style="font-size: 0.88rem; color: #64748b; line-height: 1.5;">
#         Your multilingual chat companion
#     </div>
# </div>
# """,
#     unsafe_allow_html=True,
# )

# selected_country = st.sidebar.selectbox(
#     "Select country",
#     list(COUNTRY_LANGUAGE_MAP.keys()),
#     index=0,
# )
# available_languages = COUNTRY_LANGUAGE_MAP[selected_country]

# ui_language_name = st.sidebar.selectbox(
#     "Select language",
#     list(available_languages.keys()),
#     index=0,
# )
# ui_language_code = available_languages[ui_language_name]

# auto_detect = st.sidebar.checkbox("Auto-detect user input language", value=True)
# model = st.sidebar.selectbox(
#     "Model",
#     ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
#     index=0,
# )
# app_mode = st.sidebar.radio("Mode", ["Chat Assistant", "Voice Assistant"])
# voice_output = st.sidebar.checkbox("Voice output (TTS)", value=True)
# typing_effect = st.sidebar.checkbox("Typing effect (stream)", value=True)
# clear_chat = st.sidebar.button("Clear conversation", use_container_width=True)


# # -----------------------------
# # Session state
# # -----------------------------
# def initialize_state() -> None:
#     defaults = {
#         "messages": [],
#         "pending_reply": False,
#         "last_audio_bytes": None,
#         "latest_tts_audio": None,
#         "voice_state": "idle",
#         "voice_messages": [],
#         "voice_input_key": 0,
#     }
#     for key, value in defaults.items():
#         if key not in st.session_state:
#             st.session_state[key] = value


# initialize_state()


# # -----------------------------
# # Chat history rendering
# # -----------------------------
# if app_mode == "Chat Assistant":
#     if not st.session_state.messages:
#         st.markdown(
#             """
#         <div class="empty-state">
#             <div class="empty-title">Start a more natural conversation</div>
#             <div>Ask questions, translate text, check the current time, solve math, write emails, explain topics, or talk using voice — all in your preferred language.</div>
#             <div class="chip-row">
#                 <div class="chip">Translate this to Hindi</div>
#                 <div class="chip">What’s the current time?</div>
#                 <div class="chip">Help me write a professional email</div>
#                 <div class="chip">Explain this in simple words</div>
#                 <div class="chip">Solve 25 × 4</div>
#             </div>
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )
#     else:
#         for message in st.session_state.messages:
#             bubble_class = "user-bubble" if message["role"] == "user" else "bot-bubble"
#             st.markdown(
#                 f'<div class="{bubble_class}">{message["content"]}</div>',
#                 unsafe_allow_html=True,
#             )


# # -----------------------------
# # Voice assistant
# # -----------------------------
# def render_voice_assistant() -> None:
#     state = st.session_state.voice_state

#     status_map = {
#         "idle": ("Tap record when you want to talk", "The assistant is ready and waiting."),
#         "listening": ("Listening carefully...", "Speak naturally. We’ll capture your message."),
#         "thinking": ("Thinking about your request...", "Just a moment while I prepare the reply."),
#         "speaking": ("Replying softly...", "Audio reply is ready below."),
#     }
#     title_text, sub_text = status_map.get(state, status_map["idle"])

#     st.markdown(
#         f"""<div class="voice-wrap">
# <div class="voice-card">
# <div class="voice-topline">Voice conversation</div>
# <div class="voice-title">Talk naturally</div>
# <div class="voice-subtitle">A calmer, more human voice experience for quick conversations.</div>
# <div class="voice-shell">
# <div class="voice-orb {state}"></div>
# </div>
# <div class="voice-status">{title_text}</div>
# <div class="voice-status-sub">{sub_text}</div>
# </div>
# </div>""",
#         unsafe_allow_html=True,
#     )

#     if st.session_state.latest_tts_audio:
#         st.audio(st.session_state.latest_tts_audio, format="audio/mp3", autoplay=True)
#         st.session_state.latest_tts_audio = None

#     mic_left, mic_center, mic_right = st.columns([1, 1, 1])

#     with mic_center:
#         st.markdown('<div class="mic-container">', unsafe_allow_html=True)
#         audio_file = st.audio_input(
#             "Record your voice",
#             sample_rate=16000,
#             key=f"voice_mode_{st.session_state.voice_input_key}"
#         )
#         st.markdown('</div>', unsafe_allow_html=True)

#     st.markdown(
#         """
#         <div class="voice-hint">
#             Record, stop, and wait for the audio reply below.
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

#     if audio_file is None:
#         return

#     raw_audio = audio_file.getvalue()
#     if not raw_audio or raw_audio == st.session_state.last_audio_bytes:
#         return

#     st.session_state.last_audio_bytes = raw_audio
#     st.session_state.voice_state = "listening"

#     with st.spinner("Transcribing..."):
#         user_text = transcribe_audio_bytes(raw_audio)

#     if not user_text or user_text in {".", ",", "?", "!"}:
#         st.warning("I could not clearly hear anything. Please record again.")
#         st.session_state.voice_state = "idle"
#         return

#     st.session_state.voice_state = "thinking"
#     system_prompt = build_system_prompt(ui_language_name, ui_language_code)
#     detection_hint = detect_language_hint(user_text, auto_detect)
#     voice_memory = st.session_state.get("voice_messages", [])

#     messages_for_api = build_messages(
#         system_prompt=system_prompt,
#         history=voice_memory,
#         final_language_name=ui_language_name,
#         detection_hint=detection_hint,
#         user_message=user_text,
#     )

#     with st.spinner("Thinking..."):
#         answer = stream_answer(messages_for_api=messages_for_api, model_name=model)

#     st.session_state.voice_messages = voice_memory + [
#         {"role": "user", "content": user_text},
#         {"role": "assistant", "content": answer},
#     ]

#     if voice_output and answer:
#         try:
#             st.session_state.voice_state = "speaking"
#             st.session_state.latest_tts_audio = tts_to_mp3(answer, ui_language_code)
#         except Exception as exc:
#             st.warning(f"TTS failed: {exc}")
#             st.session_state.latest_tts_audio = None

#     st.session_state.voice_state = "idle"
#     st.session_state.voice_input_key += 1
#     st.rerun()


# # -----------------------------
# # Inputs
# # -----------------------------
# user_text: str | None = None

# if app_mode == "Voice Assistant":
#     render_voice_assistant()
# else:
#     st.markdown(
#         """
#         <div class="chat-voice-block">
#             <div class="chat-voice-title">Type or speak</div>
#             <div class="chat-voice-sub">You can type your message below or record a quick voice input.</div>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

#     chat_audio_file = st.audio_input(
#         "Optional voice message",
#         sample_rate=16000,
#         key="chat_voice_mode",
#     )
#     typed_text = st.chat_input("Message SkillVerse...", key="typed_chat_input")
#     user_text = typed_text

#     if chat_audio_file is not None and not typed_text:
#         raw_audio = chat_audio_file.getvalue()
#         if raw_audio and raw_audio != st.session_state.last_audio_bytes:
#             st.session_state.last_audio_bytes = raw_audio
#             with st.spinner("Transcribing voice message..."):
#                 transcribed_text = transcribe_audio_bytes(raw_audio)

#             if transcribed_text and transcribed_text not in {".", ",", "?", "!"}:
#                 user_text = transcribed_text
#                 st.info(f"Voice input: {transcribed_text}")


# # -----------------------------
# # Chat completion flow
# # -----------------------------
# if user_text and not st.session_state.pending_reply:
#     st.session_state.messages.append({"role": "user", "content": user_text})
#     st.session_state.pending_reply = True
#     st.rerun()

# if st.session_state.pending_reply:
#     last_user_message = st.session_state.messages[-1]["content"]
#     system_prompt = build_system_prompt(ui_language_name, ui_language_code)
#     detection_hint = detect_language_hint(last_user_message, auto_detect)

#     messages_for_api = build_messages(
#         system_prompt=system_prompt,
#         history=st.session_state.messages[:-1],
#         final_language_name=ui_language_name,
#         detection_hint=detection_hint,
#         user_message=last_user_message,
#     )

#     assistant_box = st.empty()
#     collected = ""

#     with st.spinner("Thinking..."):
#         if typing_effect:
#             tools = get_tool_schemas()
#             stream = run_agent_with_tools(
#                 messages_for_api=messages_for_api,
#                 model_name=model,
#                 tools=tools,
#                 temperature=0.3,
#             )

#             for chunk in stream:
#                 delta = ""
#                 if chunk.choices and chunk.choices[0].delta:
#                     delta = chunk.choices[0].delta.content or ""
#                 if delta:
#                     collected += delta
#                     assistant_box.markdown(
#                         f'<div class="bot-bubble">{collected}</div>',
#                         unsafe_allow_html=True,
#                     )
#             answer = collected.strip()
#         else:
#             response = client.chat.completions.create(
#                 model=model,
#                 messages=messages_for_api,
#                 temperature=0.3,
#             )
#             answer = (response.choices[0].message.content or "").strip()
#             assistant_box.markdown(
#                 f'<div class="bot-bubble">{answer}</div>',
#                 unsafe_allow_html=True,
#             )

#     st.session_state.messages.append({"role": "assistant", "content": answer})
#     st.session_state.pending_reply = False
#     st.rerun()


# # -----------------------------
# # Clear chat
# # -----------------------------
# if clear_chat:
#     st.session_state.messages = []
#     st.session_state.pending_reply = False
#     st.session_state.last_audio_bytes = None
#     st.session_state.latest_tts_audio = None
#     st.session_state.voice_state = "idle"
#     st.session_state.voice_messages = []
#     st.session_state.voice_input_key = 0
#     st.rerun()



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

from style import STYLE
from prompts import build_system_prompt

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
        "Rajasthani": "raj",
    },
    "Switzerland": {
        "Romansh": "rm",
        "Italian": "it",
        "French": "fr",
        "German": "de",
        "English": "en",
    },
    "South Africa": {
        "English": "en",
        "Afrikaans": "af",
        "Zulu": "zu",
        "Xhosa": "xh"
    }
}

# -----------------------------
# Custom Styling
# -----------------------------
st.markdown(STYLE, unsafe_allow_html=True)

# NOTE: Some voices may not exist on all systems.
# If any voice fails, we fall back to English.
VOICE_MAP = {
    # English (neutral / global)
    "en": "en-US-JennyNeural",

    # India
    "hi": "hi-IN-SwaraNeural",
    "mr": "mr-IN-AarohiNeural",
    "gu": "gu-IN-DhwaniNeural",

    # Switzerland
    "de": "de-DE-KatjaNeural",
    "fr": "fr-FR-DeniseNeural",
    "it": "it-IT-ElsaNeural",

    # South Africa
    "zu": "zu-ZA-ThandoNeural",
    "xh": "xh-ZA-ThandoNeural",

    # fallback languages
    "rm": "de-DE-KatjaNeural",   # Romansh fallback to German
    "raj": "hi-IN-SwaraNeural",  # Rajasthani fallback to Hindi
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

# st.sidebar.markdown('<div class="sidebar-card"><div class="sidebar-heading">🌐 Language & Model</div>', unsafe_allow_html=True)

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

#st.sidebar.markdown('<div class="sidebar-card"><div class="sidebar-heading">Interaction</div>', unsafe_allow_html=True)

app_mode = st.sidebar.radio(
    "Mode",
    ["Chat Assistant", "Voice Assistant"]
)
voice_output = st.sidebar.checkbox("Voice output (TTS)", value=True)
typing_effect = st.sidebar.checkbox("Typing effect (stream)", value=True)

st.sidebar.markdown('</div>', unsafe_allow_html=True)

clear_chat = st.sidebar.button("Clear conversation", use_container_width=True)
#st.sidebar.markdown('</div>', unsafe_allow_html=True)

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
    
if "voice_state" not in st.session_state:
    st.session_state.voice_state = "idle"
    
if "voice_messages" not in st.session_state:
    st.session_state.voice_messages = []
    
if "voice_input_key" not in st.session_state:
    st.session_state.voice_input_key = 0
    

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
# Show chat history only for chat assistant
# -----------------------------
if app_mode == "Chat Assistant":
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

# -----------------------------
# Input (User chooses Text or Voice)
# -----------------------------
user_text = None

import re

def is_valid_transcription(text: str) -> bool:
    """
    Accept meaningful voice input while rejecting noise.
    """

    if not text:
        return False

    cleaned = text.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)

    # words that are usually noise
    noise_words = {"uh", "um", "hmm", "hm", "mmm"}

    if cleaned in noise_words:
        return False

    # allow meaningful single-word commands
    allowed_single_words = {
        "help", "hello", "google", "weather", "translate",
        "search", "time", "date", "who", "what"
    }

    words = cleaned.split()

    # single word case
    if len(words) == 1:
        if cleaned in allowed_single_words:
            return True
        if len(cleaned) >= 5:   # long word like "python"
            return True
        return False

    # reject garbage text with very few letters
    letters = sum(ch.isalpha() for ch in cleaned)
    if letters == 0:
        return False

    if letters / max(len(cleaned), 1) < 0.55:
        return False

    return True

def render_voice_assistant():
    state = st.session_state.voice_state

    status_map = {
        "idle": ("Tap record when you want to talk", "The assistant is ready and waiting."),
        "listening": ("Listening carefully...", "Speak naturally. We’ll capture your message."),
        "thinking": ("Thinking about your request...", "Just a moment while I prepare the reply."),
        "speaking": ("Replying softly...", "You can listen and then record again."),
    }

    title_text, sub_text = status_map.get(state, status_map["idle"])

    st.markdown(
        f"""<div class="voice-wrap">
        <div class="voice-card">
        <div class="voice-topline">Voice conversation</div>
        <div class="voice-title">Talk naturally</div>
        <div class="voice-subtitle">A calmer, more human voice experience for quick conversations.</div>
        <div class="voice-shell">
        <div class="voice-orb {state}"></div>
        </div>
        <div class="voice-status">{title_text}</div>
        <div class="voice-status-sub">{sub_text}</div>
        </div>
        </div>""",
            unsafe_allow_html=True
        )
    
    if st.session_state.latest_tts_audio:
        st.audio(st.session_state.latest_tts_audio, format="audio/mp3", autoplay=True)
        st.session_state.latest_tts_audio = None

    # audio_file = st.audio_input(
    #     "Record your voice",
    #     sample_rate=16000,
    #     key=f"voice_mode_{st.session_state.voice_input_key}"
    # )
    st.markdown('<div class="voice-mic-wrap">', unsafe_allow_html=True)

    audio_file = st.audio_input(
        "Record your voice",
        sample_rate=16000,
        key=f"voice_mode_{st.session_state.voice_input_key}"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="voice-hint">
            Use the built-in record and stop control above to send your voice message.
        </div>
        """,
        unsafe_allow_html=True
    )

    if audio_file is None:
        return

    # st.session_state.latest_tts_audio = None
    st.session_state.voice_state = "listening"

    raw = audio_file.getvalue()
    if not raw:
        st.session_state.voice_state = "idle"
        return

    if raw == st.session_state.last_audio_bytes:
        return

    st.session_state.last_audio_bytes = raw

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(raw)
        audio_path = f.name

    with st.spinner("Transcribing..."):
        with open(audio_path, "rb") as f_audio:
            transcription = client.audio.transcriptions.create(
                file=f_audio,
                model="whisper-large-v3-turbo",
            )

    try:
        os.remove(audio_path)
    except Exception:
        pass

    user_text = (transcription.text or "").strip()

    if not user_text or user_text in [".", ",", "?", "!"]:
        st.warning("I could not clearly hear anything. Please record again.")
        st.session_state.voice_state = "idle"
        st.session_state.voice_input_key += 1
        st.rerun()

    st.session_state.voice_state = "thinking"

    system_prompt = build_system_prompt(ui_language_name, ui_language_code)

    voice_memory = st.session_state.get("voice_messages", [])

    detected = None
    detection_hint = ""
    if auto_detect:
        try:
            detected = detect(user_text)
            detection_hint = f"\n(Developer note: detected input language: {detected})"
        except Exception:
            detection_hint = ""

    messages_for_api = [{"role": "system", "content": system_prompt + detection_hint}]
    messages_for_api += voice_memory[-8:]
    messages_for_api.append({
        "role": "user",
        "content": user_text
    })
    messages_for_api.append({
        "role": "system",
        "content": f"FINAL INSTRUCTION: Reply ONLY in {ui_language_name}."
    })

    tools = get_tool_schemas()

    stream = run_agent_with_tools(
        messages_for_api=messages_for_api,
        model=model,
        tools=tools,
        temperature=0.3,
    )

    collected = ""
    for chunk in stream:
        delta = ""
        if chunk.choices and chunk.choices[0].delta:
            delta = chunk.choices[0].delta.content or ""
        if delta:
            collected += delta

    answer = collected.strip()
    st.session_state.voice_state = "speaking"

    st.session_state.voice_messages = voice_memory + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": answer},
    ]

    if voice_output and answer:
        try:
            mp3_path = tts_to_mp3(answer, ui_language_code)

            with open(mp3_path, "rb") as f:
                audio_bytes = f.read()

            st.session_state.latest_tts_audio = audio_bytes
            # st.audio(audio_bytes, format="audio/mp3", autoplay=True)

            try:
                os.remove(mp3_path)
            except Exception:
                pass

        except Exception as e:
            st.warning(f"TTS failed: {e}")

    st.session_state.voice_state = "idle"
    st.session_state.voice_input_key += 1
    st.rerun()
        
if app_mode == "Voice Assistant":
    render_voice_assistant()
else:
    st.markdown(
        """
        <div class="chat-voice-block">
            <div class="chat-voice-title">Type or speak</div>
            <div class="chat-voice-sub">You can type your message below or record a quick voice input.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # chat_audio_file = st.audio_input("Optional voice message", sample_rate=16000, key="chat_voice_mode")
    # typed_text = st.chat_input("Message SkillVerse...", key="typed_chat_input")
    
    st.markdown('<div class="chat-audio-wrap">', unsafe_allow_html=True)

    chat_audio_file = st.audio_input(
        "Optional voice message",
        sample_rate=16000,
        key="chat_voice_mode"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    typed_text = st.chat_input("Message SkillVerse...", key="typed_chat_input")

    user_text = typed_text

    if chat_audio_file is not None and not typed_text:
        raw = chat_audio_file.getvalue()

        if raw != st.session_state.last_audio_bytes:
            st.session_state.last_audio_bytes = raw

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(raw)
                chat_audio_path = f.name

            with st.spinner("Transcribing voice message..."):
                with open(chat_audio_path, "rb") as f_audio:
                    transcription = client.audio.transcriptions.create(
                        file=f_audio,
                        model="whisper-large-v3-turbo",
                    )

            try:
                os.remove(chat_audio_path)
            except Exception:
                pass

            transcribed_text = (transcription.text or "").strip()

            if is_valid_transcription(transcribed_text):
                user_text = transcribed_text
                st.info(f"Voice input: {transcribed_text}")
            else:
                st.warning("The recording was too noisy or unclear. Please record again in a quieter voice.")
    
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
    detection_hint = ""
    if auto_detect:
        try:
            detected = detect(last_user_message)
        except Exception:
            detected = None

    system_prompt = build_system_prompt(ui_language_name, ui_language_code)

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    messages_for_api = [
        {"role": "system", "content": system_prompt + detection_hint},
        *history,
        {"role": "user", "content": last_user_message},
        {
            "role": "system",
            "content": f"FINAL INSTRUCTION: Reply ONLY in {ui_language_name}."
        }
    ]

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
    st.session_state.last_audio_bytes = None
    st.session_state.voice_state = "idle"
    st.rerun()

