# SkillVerse 💬

#### SkillVerse is a Streamlit app that provides multilingual AI chat with real-time language detection, voice input/output, and intelligent tool integration. The app uses Groq's LLaMA models for inference, Whisper for speech-to-text, and Edge TTS for text-to-speech synthesis.

---

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![Groq API](https://img.shields.io/badge/Groq%20API-LLaMA-7C3AED.svg)
![LLaMA 3.3](https://img.shields.io/badge/LLaMA%203.3-70B-1F2937.svg)
![Whisper](https://img.shields.io/badge/Whisper-Speech--to--Text-10B981.svg)
![Edge TTS](https://img.shields.io/badge/Edge%20TTS-Text--to--Speech-0EA5E9.svg)
![langdetect](https://img.shields.io/badge/langdetect-Language%20Detection-orange.svg)
![python-dotenv](https://img.shields.io/badge/python--dotenv-Config-yellow.svg)

**Requirements:** [requirements.txt](requirements.txt)

## 🛠️ Technologies Used

- **[Streamlit](https://streamlit.io)** — Web app framework for UI and interactions
- **[Groq API](https://console.groq.com)** — High-speed LLM inference with LLaMA models
- **[LLaMA 3.3](https://www.llama.com)** — 70B parameter language model
- **[LLaMA 3.1](https://www.llama.com)** — 8B parameter lightweight model
- **[Whisper](https://openai.com/research/whisper)** — Speech-to-text transcription
- **[Edge TTS](https://github.com/reuben/edge-tts)** — Natural text-to-speech synthesis
- **[langdetect](https://github.com/Mimino666/langdetect)** — Automatic language detection
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** — Environment configuration

## 🔧 Features

✨ **Multilingual Support**
- 10+ languages across 5 countries (India, Germany, France, Italy, Switzerland)
- Auto-detect user input language
- Respond in preferred language regardless of input
- Language codes: en, hi, mr, gu, kn, raj, bho, de, fr, it, rm

🎤 **Voice Interaction**
- Record and transcribe voice messages with Whisper
- Natural text-to-speech output with Edge TTS
- Language-specific voice selection
- Microphone input handling

⚡ **Intelligent Features**
- Real-time calculations and math operations
- Current time/date queries with timezone support
- Tool-based agent loop for extended capabilities
- Streaming responses with optional typing effect
- Chat history management

🎨 **Modern UI**
- Glassmorphic design with gradients
- Responsive Streamlit layout
- Real-time chat visualization with bubbles
- Custom CSS styling for enhanced UX

---

## ✅ Prerequisites

- **Python 3.8+** (3.10+ recommended)
- Microphone access for voice input
- Internet connection for API calls
- **Groq API Key** (get it from [console.groq.com](https://console.groq.com))

---

## ⚙️ Installation (Windows PowerShell)

1. Clone or navigate to the repository:

```powershell
cd c:\Users\Komal Sharma\Desktop\BOT
```

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install Python packages:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. Set up environment variables:

Create a `.env` file in the `bot/` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> **Note:** Do not commit `.env` files. Store API keys in `.streamlit/secrets.toml` for production.

---

## 🔐 API Keys / Configuration

The app requires:

- `GROQ_API_KEY` — Groq API access for LLaMA inference and Whisper transcription

For secure local development, create `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "your_groq_api_key_here"
```

Or set environment variables:

```powershell
$env:GROQ_API_KEY = "your_groq_api_key_here"
```

---

## ▶️ Run the App

```powershell
# Activate virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1

# Navigate to bot directory
cd bot

# Start Streamlit app
streamlit run app.py
```

Open the link printed by Streamlit (usually `http://localhost:8501`).

---

## ℹ️ How the App Works / UI Notes

### Main Interface

- **Top Bar**: Technology stack badges (clickable links to documentation)
- **Sidebar**: Language, model, and interaction settings
- **Chat Area**: Message history with user/bot bubbles

### Workflow

1. **Select Configuration** (Sidebar)
   - Choose country and language
   - Pick input mode (Text or Voice)
   - Toggle auto-language detection

2. **Send Message**
   - Type text or record voice
   - Voice is automatically transcribed
   - Language auto-detected if enabled

3. **Receive Response**
   - AI generates contextual reply in selected language
   - Optional streaming with typing effect
   - TTS plays response audio automatically

4. **Tool Usage**
   - Ask for current time → Tool triggered
   - Request calculation → Tool used
   - AI integrates results into response

### Configuration Options

| Section | Option | Purpose |
|---------|--------|---------|
| **Language & Model** | Country | Select region for available languages |
| | Language | Choose UI and response language |
| | Auto-detect | Auto-identify input language |
| | Model | Pick LLaMA 3.3 (powerful) or 3.1 (fast) |
| **Interaction** | Input Mode | Text input or voice recording |
| | Voice Output | Enable/disable TTS responses |
| | Typing Effect | Stream responses with animation |
| **Session** | Clear Conversation | Reset chat history |

---

## 📁 Project Structure

```
BOT/
├── bot/
│   ├── app.py              # Main Streamlit application
│   ├── tools.py            # Tool schemas and execution
│   ├── .env                # API keys (not in version control)
│   └── requirements.txt     # Python dependencies
├── README.md               # This file
└── .gitignore              # Exclude .env and __pycache__
```

### Key Files

**app.py** (580+ lines)
- Streamlit page configuration
- Custom CSS styling
- Sidebar controls
- Chat history display
- Voice input/output handling
- Agent loop with tool calling
- Session state management

**tools.py**
- Tool schema definitions (calculator, time, etc.)
- Tool dispatch and execution logic
- Result formatting

**.env**
- `GROQ_API_KEY` — Your Groq API credentials

---

## 🌐 Supported Languages & Voices

| Country | Languages | Voice Models |
|---------|-----------|--------------|
| **India** | English, Hindi, Marathi, Gujarati, Kannada, Rajasthani, Bhojpuri | Neural voices per language |
| **Germany** | German | de-DE-KatjaNeural |
| **France** | French | fr-FR-DeniseNeural |
| **Italy** | Italian | it-IT-ElsaNeural |
| **Switzerland** | Romansh | de-DE-KatjaNeural (fallback) |

---

## 🎯 Example Use Cases

- **Translation**: "Translate 'Hello' to Hindi"
- **Math**: "What is 25 × 4?"
- **Time**: "What's the current time?"
- **Writing**: "Help me write a professional email"
- **Learning**: "Explain quantum physics in simple words"
- **Multilingual Chat**: Ask in Hindi, get responses in English (or vice versa)

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure virtual environment is activated and `pip install -r requirements.txt` is run |
| API Key errors | Verify `GROQ_API_KEY` is set in `.env` or environment variables |
| Voice not working | Check microphone permissions and system audio settings |
| Transcription fails | Confirm internet connection and API quota |
| TTS audio issues | Ensure language is supported in `VOICE_MAP` |
| Model not responding | Check Groq API status and rate limits |

---

## ⚡ Performance Tips

- Use **llama-3.1-8b-instant** for faster responses with less latency
- Disable **typing effect** for immediate content display
- Disable **TTS** if audio playback isn't needed
- Keep chat history under 8 messages for optimal performance
- Use **auto-detect** sparingly on very long messages

---

## 🧩 Code Architecture

### Message Flow

```
User Input (Text/Voice)
    ↓
[Transcribe if Voice] → Whisper
    ↓
[Detect Language] → langdetect
    ↓
Build System Prompt + Messages
    ↓
Call LLM with Tools → GroqAPI
    ↓
[Check Tool Calls] → Yes: Execute → Send Result Back
    ↓
Stream Final Response → Display in UI
    ↓
[Generate TTS] → Edge TTS → Play Audio
    ↓
Save to Chat History
```

---

## 🔮 Future Enhancements

- [ ] Conversation memory with long-term context
- [ ] Custom tool creation interface
- [ ] User authentication and chat persistence
- [ ] Export conversations (PDF/TXT/JSON)
- [ ] Language learning mode with corrections
- [ ] Multi-turn tool workflows
- [ ] Chat analytics and sentiment tracking
- [ ] Offline mode with lighter models

---

## 📊 Model Comparison

| Aspect | LLaMA 3.3 70B | LLaMA 3.1 8B |
|--------|---------------|-------------|
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Speed | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Latency | Medium | Low |
| Best For | Complex tasks, reasoning | Quick responses |
| Recommended | Research, writing, analysis | Chat, summarization |

---

## 📄 License & Contact

This project is provided as-is for educational and demonstration purposes.

**Author:** Komal Sharma  
**Email:** [1908.komalsharma@gmail.com](mailto:1908.komalsharma@gmail.com)

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

---

Happy building! ✨