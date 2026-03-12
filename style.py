import streamlit as st

STYLE = """
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(139, 92, 246, 0.08), transparent 28%),
            radial-gradient(circle at top right, rgba(236, 72, 153, 0.08), transparent 24%),
            linear-gradient(180deg, #f8fafc 0%, #f5f3ff 100%);
    }

    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
        max-width: 1180px;
    }

    .user-bubble {
        background: linear-gradient(135deg, #5b4df7, #7c3aed);
        color: white;
        padding: 14px 16px;
        border-radius: 18px 18px 8px 18px;
        margin: 10px 0 10px auto;
        max-width: 76%;
        width: fit-content;
        box-shadow: 0 10px 22px rgba(91, 77, 247, 0.22);
        font-size: 0.98rem;
        line-height: 1.55;
    }

    .bot-bubble {
        background: rgba(255,255,255,0.96);
        color: #1f2937;
        padding: 14px 16px;
        border-radius: 18px 18px 18px 8px;
        margin: 10px auto 10px 0;
        max-width: 76%;
        width: fit-content;
        border: 1px solid #e7e5f4;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
        font-size: 0.98rem;
        line-height: 1.55;
    }

    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #64748b;
    }

    .empty-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 0.45rem;
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

    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        border-radius: 12px !important;
        height: 42px;
        border: 1px solid #d1d5db !important;
        background: white !important;
        color: #0f172a !important;
        font-weight: 600 !important;
    }

    .voice-wrap {
        max-width: 760px;
        margin: 0 auto;
        padding-top: 0.6rem;
    }

    .voice-card {
        background: rgba(255,255,255,0.72);
        backdrop-filter: blur(18px);
        border: 1px solid rgba(255,255,255,0.7);
        border-radius: 28px;
        box-shadow: 0 18px 40px rgba(88, 68, 173, 0.10);
        padding: 26px 24px 20px 24px;
    }

    .voice-topline {
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #8b5cf6;
        text-align: center;
        margin-bottom: 0.45rem;
    }

    .voice-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1f2937;
        text-align: center;
        margin-bottom: 0.35rem;
    }

    .voice-subtitle {
        font-size: 0.98rem;
        color: #64748b;
        text-align: center;
        line-height: 1.6;
        margin-bottom: 1.4rem;
    }

    .voice-shell {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1.2rem 0 1.1rem 0;
    }

    .voice-orb {
        width: 124px;
        height: 124px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #a78bfa, #6d56f6 55%, #4f46e5 100%);
        box-shadow:
            0 0 0 12px rgba(124, 58, 237, 0.08),
            0 18px 40px rgba(91, 77, 247, 0.24);
        position: relative;
    }

    .voice-orb.idle {
        animation: breathe 3s ease-in-out infinite;
    }

    .voice-orb.listening {
        animation: listenPulse 1.2s ease-in-out infinite;
    }

    .voice-orb.thinking {
        animation: thinkFloat 1.9s ease-in-out infinite;
    }

    .voice-orb.speaking {
        animation: speakPulse 0.9s ease-in-out infinite;
    }

    .voice-status {
        text-align: center;
        font-size: 1rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.35rem;
    }

    .voice-status-sub {
        text-align: center;
        font-size: 0.93rem;
        color: #64748b;
        margin-bottom: 1rem;
    }

    .voice-panel {
        background: rgba(248, 250, 252, 0.85);
        border: 1px solid #e9e5fb;
        border-radius: 18px;
        padding: 14px 16px;
        margin-top: 1rem;
    }

    .voice-label {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8b5cf6;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .voice-text {
        color: #334155;
        line-height: 1.6;
        font-size: 0.97rem;
    }

    .voice-hint {
        text-align: center;
        color: #94a3b8;
        font-size: 0.88rem;
        margin-top: 0.8rem;
    }

    .chat-voice-block {
        background: rgba(255,255,255,0.7);
        border: 1px solid #ece9fb;
        border-radius: 18px;
        padding: 14px 14px 8px 14px;
        margin-top: 12px;
        margin-bottom: 10px;
    }

    .chat-voice-title {
        font-size: 0.96rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 0.2rem;
    }

    .chat-voice-sub {
        font-size: 0.88rem;
        color: #64748b;
        margin-bottom: 0.65rem;
    }

    @keyframes breathe {
        0% { transform: scale(1); }
        50% { transform: scale(1.04); }
        100% { transform: scale(1); }
    }

    @keyframes listenPulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(124, 58, 237, 0.18), 0 18px 40px rgba(91, 77, 247, 0.24); }
        70% { transform: scale(1.08); box-shadow: 0 0 0 18px rgba(124, 58, 237, 0.03), 0 18px 40px rgba(91, 77, 247, 0.24); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(124, 58, 237, 0.00), 0 18px 40px rgba(91, 77, 247, 0.24); }
    }

    @keyframes thinkFloat {
        0% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-6px) scale(1.03); }
        100% { transform: translateY(0px) scale(1); }
    }

    @keyframes speakPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.11); }
        100% { transform: scale(1); }
    }
#     /* make mic recorder small */
# [data-testid="stAudioInput"] {
#     max-width: 50px;
# }

# /* remove label spacing */
# [data-testid="stAudioInput"] label {
#     display:none;
# }

# /* align input row */
# .stTextInput input {
#     border-radius: 14px !important;
#     height: 44px !important;
# }

# /* send button */
# .stButton button {
#     height: 44px !important;
#     border-radius: 12px !important;
# }
# /* bottom chat row spacing */
# div[data-testid="column"] {
#     display: flex;
#     align-items: end;
# }

# /* text input look */
# .stTextInput input {
#     height: 46px !important;
#     border-radius: 14px !important;
#     padding-left: 14px !important;
# }

# /* small mic */
# [data-testid="stAudioInput"] {
#     max-width: 46px !important;
#     margin-top: 0 !important;
# }

# [data-testid="stAudioInput"] label {
#     display: none !important;
# }

# /* send button */
# .stButton button {
#     height: 46px !important;
#     border-radius: 12px !important;
#     min-width: 46px !important;
#     padding: 0 !important;
# }
# @keyframes breathe {
#         0% { transform: scale(1); }
#         50% { transform: scale(1.04); }
#         100% { transform: scale(1); }
#     }

#     @keyframes listenPulse {
#         0% {
#             transform: scale(1);
#             box-shadow: 0 0 0 0 rgba(124, 58, 237, 0.18), 0 18px 40px rgba(91, 77, 247, 0.24);
#         }
#         70% {
#             transform: scale(1.08);
#             box-shadow: 0 0 0 18px rgba(124, 58, 237, 0.03), 0 18px 40px rgba(91, 77, 247, 0.24);
#         }
#         100% {
#             transform: scale(1);
#             box-shadow: 0 0 0 0 rgba(124, 58, 237, 0), 0 18px 40px rgba(91, 77, 247, 0.24);
#         }
#     }

#     @keyframes thinkFloat {
#         0% { transform: translateY(0) scale(1); }
#         50% { transform: translateY(-6px) scale(1.03); }
#         100% { transform: translateY(0) scale(1); }
#     }

#     @keyframes speakPulse {
#         0% { transform: scale(1); }
#         50% { transform: scale(1.11); }
#         100% { transform: scale(1); }
#     }
# /* mic overlay inside voice orb */
#     .mic-container {
#     display: flex;
#     justify-content: center;
#     align-items: center;
#     margin-top: -130px;
#     margin-bottom: 130px;
#     position: relative;
#     z-index: 30;
# }

# [data-testid="stAudioInput"] {
#     display: flex !important;
#     justify-content: center !important;
#     align-items: center !important;
#     width: 100% !important;
#     max-width: none !important;
#     margin: 0 !important;
#     padding: 0 !important;
# }

# [data-testid="stAudioInput"] label {
#     display: none !important;
# }

# [data-testid="stAudioInput"] button {
#     width: 80px !important;
#     height: 80px !important;
#     border-radius: 50% !important;
#     border: none !important;
#     box-shadow: 0 12px 28px rgba(79, 70, 229, 0.28) !important;
#     background: rgba(255, 255, 255, 0.95) !important;
#     cursor: pointer !important;
# }

# [data-testid="stAudioInput"] button:hover {
#     background: white !important;
#     box-shadow: 0 14px 32px rgba(79, 70, 229, 0.35) !important;
# }
#     .voice-orb.listening {
#     animation: listenPulse 1s infinite;
# }
# /* Chat input container */
# .chat-input-row {
#     position: sticky;
#     bottom: 0;
#     padding: 10px;
# }

# /* Text input style */
# div[data-testid="stTextInput"] input {
#     height: 52px !important;
#     border-radius: 16px !important;
#     padding-left: 16px !important;
# }

# /* Send button */
# .stButton button {
#     height: 52px !important;
#     width: 52px !important;
#     border-radius: 12px !important;
#     font-size: 18px !important;
# }

# /* Mic button same size as send */
# [data-testid="stAudioInput"] button {
#     height: 52px !important;
#     width: 52px !important;
#     border-radius: 12px !important;
# }

# /* Center mic icon */
# [data-testid="stAudioInput"] svg {
#     width: 18px !important;
#     height: 18px !important;
#}

/* -----------------------------
   CHAT AUDIO INPUT
------------------------------ */
.chat-audio-wrap [data-testid="stAudioInput"] {
    max-width: 56px !important;
    margin: 0 !important;
    padding: 0 !important;
}

.chat-audio-wrap [data-testid="stAudioInput"] label {
    display: none !important;
}

.chat-audio-wrap [data-testid="stAudioInput"] button {
    width: 48px !important;
    height: 48px !important;
    border-radius: 12px !important;
    border: none !important;
    background: rgba(255, 255, 255, 0.95) !important;
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08) !important;
}

.chat-audio-wrap [data-testid="stAudioInput"] button:hover {
    background: white !important;
}

/* -----------------------------
   CHAT TEXT INPUT / SEND BUTTON
------------------------------ */
div[data-testid="stTextInput"] input {
    height: 48px !important;
    border-radius: 14px !important;
    padding-left: 14px !important;
}

.stButton button {
    height: 48px !important;
    min-width: 48px !important;
    border-radius: 12px !important;
    padding: 0 14px !important;
}

/* -----------------------------
   VOICE ORB AUDIO INPUT
------------------------------ */
.voice-mic-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: -102px;
    margin-bottom: 46px;
    position: relative;
    z-index: 20;
}

.voice-mic-wrap [data-testid="stAudioInput"] {
    width: auto !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

.voice-mic-wrap [data-testid="stAudioInput"] label {
    display: none !important;
}

.voice-mic-wrap [data-testid="stAudioInput"] button {
    width: 84px !important;
    height: 84px !important;
    border-radius: 50% !important;
    border: none !important;
    background: rgba(255, 255, 255, 0.96) !important;
    box-shadow: 0 12px 28px rgba(79, 70, 229, 0.28) !important;
}

.voice-mic-wrap [data-testid="stAudioInput"] button:hover {
    background: white !important;
    box-shadow: 0 14px 32px rgba(79, 70, 229, 0.35) !important;
}

.voice-mic-wrap [data-testid="stAudioInput"] svg {
    width: 22px !important;
    height: 22px !important;
}
</style>
"""




# import streamlit as st
# STYLE="""
# <style>
#     .stApp {
#         background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 45%, #fdf2f8 100%);
#     }

#     .main .block-container {
#         padding-top: 1.5rem;
#         padding-bottom: 1rem;
#         max-width: 1200px;
#     }

#     .hero-card {
#         background: rgba(255,255,255,0.72);
#         backdrop-filter: blur(14px);
#         border: 1px solid rgba(255,255,255,0.5);
#         padding: 28px 30px;
#         border-radius: 24px;
#         box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
#         margin-bottom: 18px;
#     }

#     .hero-title {
#         font-size: 2.4rem;
#         font-weight: 800;
#         color: #1e293b;
#         margin-bottom: 0.35rem;
#         letter-spacing: -0.5px;
#     }

#     .hero-subtitle {
#         font-size: 1rem;
#         color: #475569;
#         line-height: 1.6;
#     }

#     .section-label {
#         font-size: 0.82rem;
#         text-transform: uppercase;
#         letter-spacing: 0.08em;
#         color: #7c3aed;
#         font-weight: 700;
#         margin-bottom: 0.3rem;
#     }

#     .chat-shell {
#         background: rgba(255,255,255,0.62);
#         border: 1px solid rgba(255,255,255,0.45);
#         backdrop-filter: blur(14px);
#         border-radius: 24px;
#         padding: 18px;
#         box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
#         min-height: 62vh;
#     }

#     .user-bubble {
#         background: linear-gradient(135deg, #4f46e5, #7c3aed);
#         color: white;
#         padding: 14px 16px;
#         border-radius: 18px 18px 6px 18px;
#         margin: 10px 0 10px auto;
#         max-width: 78%;
#         width: fit-content;
#         box-shadow: 0 8px 18px rgba(79, 70, 229, 0.22);
#         font-size: 0.98rem;
#         line-height: 1.5;
#     }

#     .bot-bubble {
#         background: #ffffff;
#         color: #1e293b;
#         padding: 14px 16px;
#         border-radius: 18px 18px 18px 6px;
#         margin: 10px auto 10px 0;
#         max-width: 78%;
#         width: fit-content;
#         border: 1px solid #e2e8f0;
#         box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
#         font-size: 0.98rem;
#         line-height: 1.5;
#     }

#     .empty-state {
#         text-align: center;
#         padding: 3rem 1rem;
#         color: #64748b;
#     }

#     .empty-title {
#         font-size: 1.3rem;
#         font-weight: 700;
#         color: #334155;
#         margin-bottom: 0.4rem;
#     }

#     .chip-row {
#         display: flex;
#         flex-wrap: wrap;
#         gap: 10px;
#         margin-top: 1rem;
#         justify-content: center;
#     }

#     .chip {
#         background: white;
#         border: 1px solid #e2e8f0;
#         padding: 10px 14px;
#         border-radius: 999px;
#         color: #334155;
#         font-size: 0.92rem;
#         box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
#     }

#     section[data-testid="stSidebar"] {
#         background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
#         border-right: 1px solid #e5e7eb;
#     }

#     section[data-testid="stSidebar"] .block-container {
#         padding-top: 1.2rem;
#         padding-bottom: 1rem;
#         padding-left: 1rem;
#         padding-right: 1rem;
#     }

#     .sidebar-brand {
#         padding: 0.4rem 0.2rem 1rem 0.2rem;
#         margin-bottom: 0.6rem;
#     }

#     .sidebar-brand-title {
#         font-size: 1.9rem;
#         font-weight: 800;
#         color: #0f172a;
#         margin-bottom: 0.25rem;
#         letter-spacing: -0.5px;
#     }

#     .sidebar-brand-subtitle {
#         font-size: 0.9rem;
#         color: #64748b;
#         line-height: 1.5;
#     }

#     .sidebar-card {
#         background: rgba(255,255,255,0.88);
#         border: 1px solid #e5e7eb;
#         border-radius: 18px;
#         padding: 16px 14px 14px 14px;
#         margin-bottom: 14px;
#         box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
#     }

#     .sidebar-heading {
#         font-size: 0.98rem;
#         font-weight: 700;
#         color: #0f172a;
#         margin-bottom: 12px;
#     }

#     section[data-testid="stSidebar"] label {
#         font-size: 0.88rem !important;
#         font-weight: 500 !important;
#         color: #334155 !important;
#     }

#     section[data-testid="stSidebar"] .stSelectbox,
#     section[data-testid="stSidebar"] .stRadio,
#     section[data-testid="stSidebar"] .stCheckbox {
#         margin-bottom: 0.55rem;
#     }

#     section[data-testid="stSidebar"] .stButton button {
#         width: 100%;
#         border-radius: 12px !important;
#         height: 42px;
#         border: 1px solid #d1d5db !important;
#         background: white !important;
#         color: #0f172a !important;
#         font-weight: 600 !important;
#     }

#     .sidebar-footer {
#         margin-top: 10px;
#         padding-top: 10px;
#         border-top: 1px solid #e5e7eb;
#         font-size: 0.82rem;
#         color: #64748b;
#         text-align: center;
#     }
#     .voice-shell {
#     display:flex;
#     justify-content:center;
#     align-items:center;
#     margin-top:40px;
# }

# .voice-orb {
#     width:120px;
#     height:120px;
#     border-radius:50%;
#     background: radial-gradient(circle at 30% 30%, #8b5cf6, #4f46e5);
#     animation:pulse 1.8s infinite;
# }

# @keyframes pulse {
#     0% {transform:scale(1);}
#     50% {transform:scale(1.1);}
#     100% {transform:scale(1);}
# }
# </style>
# """