# AI-Assistant 🤖🎙️

A modern, multi-functional AI Desktop Personal Assistant built with Python. Featuring a sleek Catppuccin-themed GUI, dual Voice and Text controls, universal app and website launching, YouTube playback, Wikipedia knowledge retrieval, and Windows automation.

---

## ✨ Features

- **🎨 Modern Desktop GUI**: Built with Tkinter in an eye-friendly dark theme with real-time status indicators, quick action buttons, and conversation history.
- **🎙️ Voice & Text Controls**: Switch between hands-free continuous speech recognition and keyboard commands.
- **🔊 Text-to-Speech Engine**: SAPI-based speech synthesis with thread-safe audio queues and graceful fallbacks.
- **🚀 Universal Opener**:
  - **System Apps & Settings**: Camera, Notepad, Calculator, Paint, Task Manager, Command Prompt, Settings, File Explorer, Snipping Tool.
  - **Desktop Applications**: Visual Studio Code, Chrome, Edge, and all Start Menu shortcuts.
  - **Websites & Web Apps**: YouTube, Google, ChatGPT, DeepSeek, Gemini, Claude, GitHub, WhatsApp Web, Spotify, Netflix, and more.
- **🎵 Music & Media Playback**: Direct YouTube song searching and playback.
- **🧠 Knowledge & Calculations**:
  - Live Wikipedia summaries using REST API with sentence extraction.
  - Instant math expression evaluation.
  - Time, date, jokes, and interesting facts.
- **💻 Hardware & Media Controls**: Screenshot capture (saved directly to Desktop), volume control, and mute toggling.
- **⚡ ARM64 & x64 Compatible**: In-memory FLAC audio encoding using `soundfile` ensuring smooth speech recognition without external binary dependencies.

---

## 📁 Project Structure

```text
AI-Assistant/
├── AI_Assistant/
│   ├── Assistant_GUI.py       # Main GUI application & core logic
│   ├── Assistant.py           # Console voice assistant engine
│   ├── opener.py              # Universal app & website launcher
│   ├── ai.py                  # Standalone voice helper
│   ├── main.py                # Entry point
│   ├── START_ASSISTANT.bat    # Windows one-click launcher
│   └── Run_Voice_Only.bat     # Voice console launcher
├── main.py                    # Root entry point
├── START_ASSISTANT.bat        # Root launcher
├── requirements.txt           # Project dependencies
├── .gitignore
└── README.md
```

---

## 🛠️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Kiran-0728/AI-Assistant.git
cd AI-Assistant
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Assistant

### Option 1: Desktop GUI (Recommended)
```bash
python main.py
```
*Or double-click `START_ASSISTANT.bat` on Windows.*

### Option 2: Voice-Only Console Mode
```bash
python main.py --voice
```
*Or double-click `Run_Voice_Only.bat`.*

---

## 🗣️ Example Commands

| Command | Action |
| :--- | :--- |
| `"Play Believer"` | Plays the song on YouTube |
| `"Who is Albert Einstein?"` | Reads and displays Wikipedia summary |
| `"What is 45 multiplied by 8?"` | Calculates math expression |
| `"Open Camera"` / `"Open Notepad"` | Launches Windows system app |
| `"Open YouTube"` / `"Open ChatGPT"` | Opens web application |
| `"Take a screenshot"` | Captures screen to your Desktop |
| `"What time is it?"` / `"What is today's date?"` | Tells current time / date |
| `"Tell me a joke"` | Tells a random joke |

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
