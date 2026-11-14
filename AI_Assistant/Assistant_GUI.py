import os
import sys
import re
import threading
import queue
import datetime
import random
import webbrowser
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext
import speech_recognition as sr

# Ensure robust in-memory FLAC conversion (fixes Windows ARM64 / missing flac.exe)
try:
    import io
    import soundfile as sf
    _orig_get_flac_data = sr.AudioData.get_flac_data
    def _in_memory_flac_data(self, convert_rate=None, convert_width=None):
        try:
            wav_data = self.get_wav_data(convert_rate, convert_width)
            data, samplerate = sf.read(io.BytesIO(wav_data))
            out_buf = io.BytesIO()
            sf.write(out_buf, data, samplerate, format="FLAC")
            return out_buf.getvalue()
        except Exception:
            return _orig_get_flac_data(self, convert_rate, convert_width)
    sr.AudioData.get_flac_data = _in_memory_flac_data
except Exception:
    pass
import pyttsx3
import requests
import pyjokes
import pyautogui
import opener

try:
    import pywhatkit
except Exception:
    pywhatkit = None

# ----------------- Wikipedia & Web Search Helper -----------------
def search_wikipedia_summary(query):
    """Fetch accurate Wikipedia summary using Wikipedia REST API with proper User-Agent"""
    clean_query = re.sub(
        r'^(who is|who was|what is|what are|where is|tell me about|explain|search wikipedia for|search wikipedia|wikipedia)\s+',
        '', query, flags=re.IGNORECASE
    ).strip()
    
    if not clean_query:
        return None
        
    try:
        headers = {'User-Agent': 'AIAssistantBot/2.0 (Windows NT 10.0; Win64; x64)'}
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(clean_query)}&format=json&utf8=1"
        res = requests.get(search_url, headers=headers, timeout=5).json()
        items = res.get('query', {}).get('search', [])
        if not items:
            return None
            
        top_title = items[0]['title']
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(top_title)}"
        sum_res = requests.get(summary_url, headers=headers, timeout=5).json()
        extract = sum_res.get('extract')
        if extract:
            # Return first two sentences
            sentences = [s.strip() for s in extract.split('. ') if s.strip()]
            return '. '.join(sentences[:2]) + '.'
    except Exception as e:
        print(f"Wikipedia search error: {e}")
    return None

def evaluate_math(text):
    """Safely parse and evaluate simple math expressions"""
    clean = text.lower()
    replacements = [
        ('multiplied by', '*'), ('divided by', '/'), ('plus', '+'), 
        ('minus', '-'), ('times', '*'), ('into', '*'), ('x', '*')
    ]
    for word, sym in replacements:
        clean = clean.replace(word, sym)
        
    m = re.search(r'(\d+(?:\.\d+)?\s*[\+\-\*\/]\s*\d+(?:\.\d+)?(?:\s*[\+\-\*\/]\s*\d+(?:\.\d+)?)*)', clean)
    if m:
        expr = m.group(1).strip()
        try:
            res = eval(expr, {"__builtins__": None}, {})
            if isinstance(res, float) and res.is_integer():
                res = int(res)
            return f"The answer to {expr} is {res}"
        except Exception:
            return None
    return None


# ----------------- Core Assistant Logic -----------------
class AssistantCore:
    def __init__(self, on_status_change=None, on_message=None):
        self.on_status_change = on_status_change
        self.on_message = on_message
        self.recognizer = sr.Recognizer()
        self.tts_lock = threading.Lock()

    def set_status(self, text, color="#89b4fa"):
        if self.on_status_change:
            self.on_status_change(text, color)

    def log_message(self, sender, text):
        if self.on_message:
            self.on_message(sender, text)

    def speak(self, text):
        self.log_message("Assistant", text)
        self.set_status("Speaking...", "#a6e3a1")
        
        def _tts():
            with self.tts_lock:
                try:
                    try:
                        import pythoncom
                        pythoncom.CoInitialize()
                    except Exception:
                        pass
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 160)
                    try:
                        voices = engine.getProperty('voices')
                        if voices:
                            engine.setProperty('voice', voices[0].id)
                    except Exception:
                        pass
                    engine.say(text)
                    engine.runAndWait()
                    engine.stop()
                except Exception as e:
                    print(f"TTS Error: {e}")
            self.set_status("Ready", "#89b4fa")

        threading.Thread(target=_tts, daemon=True).start()

    def greet_user(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = "Good morning!"
        elif hour < 18:
            greeting = "Good afternoon!"
        else:
            greeting = "Good evening!"
        self.speak(f"{greeting} I'm your AI assistant, ready to help!")

    def open_website(self, command):
        sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://www.github.com",
            "wikipedia": "https://www.wikipedia.org",
            "whatsapp": "https://web.whatsapp.com",
            "gmail": "https://mail.google.com",
            "instagram": "https://www.instagram.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "reddit": "https://www.reddit.com",
            "linkedin": "https://www.linkedin.com",
            "netflix": "https://www.netflix.com",
            "spotify": "https://open.spotify.com",
            "amazon": "https://www.amazon.com"
        }
        for key, url in sites.items():
            if f"open {key}" in command or command == key:
                self.speak(f"Opening {key.capitalize()}")
                webbrowser.open(url)
                return True
                
        # Generic URL matcher (e.g., "open cricbuzz.com")
        m = re.search(r'open\s+([a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,})', command)
        if m:
            domain = m.group(1)
            url = f"https://{domain}" if not domain.startswith("http") else domain
            self.speak(f"Opening {domain}")
            webbrowser.open(url)
            return True
            
        return False

    def handle_system_apps(self, command):
        if "camera" in command or "webcam" in command:
            self.speak("Opening Camera")
            subprocess.Popen(["cmd", "/c", "start", "microsoft.windows.camera:"], shell=True)
            return True
        elif "notepad" in command:
            self.speak("Opening Notepad")
            subprocess.Popen(["notepad.exe"])
            return True
        elif "calculator" in command or "calc" in command:
            self.speak("Opening Calculator")
            subprocess.Popen(["calc.exe"])
            return True
        elif "paint" in command:
            self.speak("Opening Paint")
            subprocess.Popen(["mspaint.exe"])
            return True
        elif "command prompt" in command or "cmd" in command or "terminal" in command:
            self.speak("Opening Command Prompt")
            subprocess.Popen(["cmd.exe"])
            return True
        elif "settings" in command:
            self.speak("Opening Windows Settings")
            os.system("start ms-settings:")
            return True
        elif "file explorer" in command or "files" in command or "my computer" in command or "this pc" in command:
            self.speak("Opening File Explorer")
            subprocess.Popen(["explorer.exe"])
            return True
        elif "task manager" in command:
            self.speak("Opening Task Manager")
            subprocess.Popen(["taskmgr.exe"])
            return True
        elif "snipping tool" in command or "snip" in command:
            self.speak("Opening Snipping Tool")
            subprocess.Popen(["cmd", "/c", "start", "ms-screenclip:"], shell=True)
            return True
        elif "screenshot" in command:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop):
                desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(desktop, f"screenshot_{ts}.png")
            pyautogui.screenshot(filepath)
            self.speak("Screenshot captured and saved to your Desktop!")
            return True
        elif "volume up" in command or "increase volume" in command:
            pyautogui.press('volumeup', presses=5)
            self.speak("Turned the volume up")
            return True
        elif "volume down" in command or "decrease volume" in command or "lower volume" in command:
            pyautogui.press('volumedown', presses=5)
            self.speak("Turned the volume down")
            return True
        elif "mute" in command or "unmute" in command:
            pyautogui.press('volumemute')
            self.speak("Toggled mute")
            return True
        return False

    def process_command(self, raw_command):
        command = raw_command.strip().lower()
        if not command:
            return

        self.log_message("You", raw_command)

        # 1. Exit / Stop
        if any(w in command for w in ["exit", "quit", "goodbye", "bye", "close assistant", "stop assistant"]):
            self.speak("Goodbye! Have a great day!")
            if hasattr(self, 'on_quit') and self.on_quit:
                self.on_quit()
            return

        # 2. Greetings
        if re.search(r'\b(hello|hi|hey|good morning|good evening|good afternoon|namaste|sup|what\'s up)\b', command):
            responses = [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Hey! I'm here and listening. What would you like to do?"
            ]
            self.speak(random.choice(responses))
            return

        # 3. Help & Capabilities
        if any(w in command for w in ["what can you do", "help", "commands", "features", "options"]):
            help_msg = (
                "Here is what I can do for you:\n"
                "• Play any song: 'Play Believer' or 'Play music'\n"
                "• Answer any question: 'Who is Elon Musk?' or 'What is AI?'\n"
                "• Web search: 'Search for quantum computing' or 'Google python tutorial'\n"
                "• Open apps & sites: 'Open YouTube', 'Open Notepad', 'Open Calculator'\n"
                "• Time & Date: 'What time is it?' or 'What is today\\'s date?'\n"
                "• Calculations: 'Calculate 45 times 8'\n"
                "• Fun: 'Tell me a joke' or 'Tell me a cool fact'\n"
                "• System controls: 'Take a screenshot', 'Volume up', 'Mute'"
            )
            self.speak("I can play music, search Google or Wikipedia, open apps and websites, tell time, do math, and more!")
            self.log_message("System", help_msg)
            return

        # 4. Identity & Small Talk
        if any(p in command for p in ["who are you", "what is your name", "who created you", "who made you"]):
            self.speak("I am your personal AI Desktop Assistant, built with Python to help make your computer experience effortless!")
            return

        if any(p in command for p in ["how are you", "how are you doing", "how are you today"]):
            responses = [
                "I'm feeling great and ready to assist you!",
                "Doing awesome! Thank you for asking. How are you?",
                "Running smoothly with all systems operational!"
            ]
            self.speak(random.choice(responses))
            return

        if any(p in command for p in ["thank you", "thanks", "thanks a lot", "thank u"]):
            self.speak("You're very welcome! Always happy to help.")
            return

        if any(p in command for p in ["can you hear me", "are you there", "are you listening"]):
            self.speak("Yes, I can hear you loud and clear!")
            return

        # 5. Math / Calculation
        math_ans = evaluate_math(command)
        if math_ans:
            self.speak(math_ans)
            return

        # 6. Time & Date
        if "time" in command and not ("play" in command or "search" in command):
            now = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {now}")
            return

        if "date" in command or "today's day" in command or "what day is" in command:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {today}")
            return

        # 7. Jokes & Facts
        if "joke" in command or "make me laugh" in command or "funny" in command:
            joke = pyjokes.get_joke()
            self.speak(joke)
            return

        if any(p in command for p in ["fact", "tell me something cool", "interesting fact"]):
            facts = [
                "Did you know? Honey never spoils. Archaeologists have found 3,000-year-old honey in Egyptian tombs that is still edible!",
                "Did you know? Octopuses have three hearts and blue blood!",
                "Did you know? A day on Venus is longer than a year on Venus!",
                "Did you know? The first computer bug was an actual real moth found inside a Harvard Mark II computer in 1947!"
            ]
            self.speak(random.choice(facts))
            return

        # 8. Music & Video (YouTube)
        if re.search(r'\b(play|song|music|listen to)\b', command):
            song = re.sub(r'^(play music|play song|play|can you play|listen to)\s*', '', command, flags=re.IGNORECASE).strip()
            song = song.replace("on youtube", "").strip()
            if not song:
                song = "top trending music"
            self.speak(f"Playing {song} on YouTube")
            played = False
            if pywhatkit is not None:
                try:
                    pywhatkit.playonyt(song)
                    played = True
                except Exception:
                    pass
            if not played:
                webbrowser.open(f"https://www.youtube.com/results?search_query={requests.utils.quote(song)}")
            return

        # Hardware & Media controls (Volume, Screenshot, Mute)
        if any(w in command for w in ["screenshot", "volume up", "increase volume", "volume down", "decrease volume", "lower volume", "mute", "unmute"]):
            if self.handle_system_apps(command):
                return

        # 9. Universal Opener: Opens ANY app, tool, folder, website, or web service
        if re.search(r'\b(open|launch|start|go to)\b', command) or len(command.split()) <= 3:
            opened, msg = opener.universal_open(command)
            if opened:
                self.speak(msg)
                return

        # 10. Explicit Google / Web Search
        if re.search(r'\b(search for|search|google)\b', command):
            query = re.sub(r'^(search for|search google for|search|google for|google)\s*', '', command, flags=re.IGNORECASE).strip()
            if query:
                self.speak(f"Searching Google for {query}")
                webbrowser.open(f"https://www.google.com/search?q={requests.utils.quote(query)}")
                return

        # 12. Knowledge & Wikipedia Queries ("who is", "what is", "where is", "tell me about")
        if re.search(r'^(who is|who was|what is|what are|where is|tell me about|explain|wikipedia)\b', command):
            self.set_status("Searching Wikipedia...", "#cba6f7")
            wiki_result = search_wikipedia_summary(command)
            if wiki_result:
                self.speak(wiki_result)
                return
            else:
                # If Wikipedia did not find it, search Google
                query = re.sub(r'^(who is|who was|what is|what are|where is|tell me about|explain|wikipedia)\s*', '', command, flags=re.IGNORECASE).strip()
                self.speak(f"I couldn't find a direct summary, so I'm opening Google search results for {query}")
                webbrowser.open(f"https://www.google.com/search?q={requests.utils.quote(query)}")
                return

        # 13. Smart Fallback: NEVER dead-end with "I'm not sure yet"!
        # First try Wikipedia query on the full sentence
        wiki_res = search_wikipedia_summary(command)
        if wiki_res:
            self.speak(wiki_res)
            return

        # Otherwise, open Google search for the user's query
        self.speak(f"Here is what I found on Google for {command}")
        webbrowser.open(f"https://www.google.com/search?q={requests.utils.quote(command)}")

    def listen_single_turn(self):
        try:
            with sr.Microphone() as source:
                self.set_status("Listening...", "#f9e2af")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                self.recognizer.pause_threshold = 0.8
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                except sr.WaitTimeoutError:
                    self.set_status("Ready", "#89b4fa")
                    return ""

                self.set_status("Processing speech...", "#cba6f7")
                command = self.recognizer.recognize_google(audio)
                return command
        except sr.UnknownValueError:
            self.set_status("Ready", "#89b4fa")
            return ""
        except sr.RequestError:
            self.set_status("Network Error", "#f38ba8")
            return ""
        except Exception as e:
            print(f"Mic error: {e}")
            self.set_status("Ready", "#89b4fa")
            return ""


# ----------------- Modern Desktop GUI -----------------
class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Desktop Assistant")
        self.root.geometry("640x720")
        self.root.minsize(520, 600)
        self.root.configure(bg="#1e1e2e")

        self.BG_MAIN = "#1e1e2e"
        self.BG_CARD = "#252538"
        self.BG_INPUT = "#313244"
        self.ACCENT = "#cba6f7"
        self.ACCENT_HOVER = "#b4befe"
        self.TEXT_COLOR = "#cdd6f4"
        self.TEXT_MUTED = "#a6adc8"
        self.SUCCESS = "#a6e3a1"
        self.WARNING = "#f9e2af"

        self.assistant = AssistantCore(
            on_status_change=self.update_status_threadsafe,
            on_message=self.display_message_threadsafe
        )
        self.assistant.on_quit = self.on_closing

        self.voice_listening_active = False
        self.voice_thread = None

        self.setup_ui()

        # Bring window to front so it is visible over VS Code
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.focus_force()

        print("AI Assistant GUI launched successfully! Window is open on your screen.")

        # Start greeting in thread
        self.root.after(400, self.assistant.greet_user)
        # Automatically start continuous voice listening
        self.root.after(1200, self.toggle_continuous_listening)

    def setup_ui(self):
        # Header Frame
        header = tk.Frame(self.root, bg=self.BG_CARD, height=85)
        header.pack(fill=tk.X, padx=16, pady=(16, 8))
        header.pack_propagate(False)

        # Title & Subtitle
        title_box = tk.Frame(header, bg=self.BG_CARD)
        title_box.pack(side=tk.LEFT, padx=16, pady=10)

        title_lbl = tk.Label(
            title_box, text="AI Personal Assistant",
            font=("Segoe UI", 16, "bold"), fg=self.TEXT_COLOR, bg=self.BG_CARD
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            title_box, text="Always Ready • Voice & Text Controls",
            font=("Segoe UI", 9), fg=self.TEXT_MUTED, bg=self.BG_CARD
        )
        subtitle_lbl.pack(anchor="w")

        # Status Badge
        self.status_frame = tk.Frame(header, bg=self.BG_CARD)
        self.status_frame.pack(side=tk.RIGHT, padx=16, pady=15)

        self.status_dot = tk.Label(
            self.status_frame, text="●", font=("Segoe UI", 14),
            fg=self.SUCCESS, bg=self.BG_CARD
        )
        self.status_dot.pack(side=tk.LEFT, padx=(0, 6))

        self.status_lbl = tk.Label(
            self.status_frame, text="Ready", font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_COLOR, bg=self.BG_CARD
        )
        self.status_lbl.pack(side=tk.LEFT)

        # Quick Actions Bar
        actions_frame = tk.Frame(self.root, bg=self.BG_MAIN)
        actions_frame.pack(fill=tk.X, padx=16, pady=4)

        buttons_info = [
            ("🎵 Play Music", lambda: self.assistant.process_command("play music")),
            ("📷 Camera", lambda: self.assistant.process_command("open camera")),
            ("🕒 Time", lambda: self.assistant.process_command("what is the time")),
            ("😂 Tell Joke", lambda: self.assistant.process_command("tell me a joke")),
            ("📺 YouTube", lambda: self.assistant.process_command("open youtube")),
            ("💡 Help", lambda: self.assistant.process_command("what can you do")),
        ]

        for text, cmd in buttons_info:
            btn = tk.Button(
                actions_frame, text=text, font=("Segoe UI", 9),
                bg=self.BG_INPUT, fg=self.TEXT_COLOR, activebackground=self.ACCENT,
                activeforeground="#11111b", bd=0, padx=10, pady=5, cursor="hand2",
                command=cmd
            )
            btn.pack(side=tk.LEFT, padx=3)

        # Chat / Transcript Display
        chat_frame = tk.Frame(self.root, bg=self.BG_CARD)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, font=("Segoe UI", 10),
            bg=self.BG_CARD, fg=self.TEXT_COLOR, bd=0, padx=14, pady=14,
            insertbackground=self.TEXT_COLOR, selectbackground=self.ACCENT
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        # Tags for styling messages
        self.chat_display.tag_config("You", foreground="#89b4fa", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("Assistant", foreground="#a6e3a1", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("System", foreground="#f9e2af", font=("Segoe UI", 9))
        self.chat_display.tag_config("text", foreground=self.TEXT_COLOR, font=("Segoe UI", 10))

        # Bottom Input & Voice Control Bar
        bottom_frame = tk.Frame(self.root, bg=self.BG_CARD, height=65)
        bottom_frame.pack(fill=tk.X, padx=16, pady=(0, 16))
        bottom_frame.pack_propagate(False)

        # Voice Toggle Button
        self.mic_btn = tk.Button(
            bottom_frame, text="🎙️ Listening ON", font=("Segoe UI", 10, "bold"),
            bg="#313244", fg="#a6e3a1", activebackground=self.ACCENT,
            bd=0, padx=14, pady=8, cursor="hand2",
            command=self.toggle_continuous_listening
        )
        self.mic_btn.pack(side=tk.LEFT, padx=(12, 8), pady=12)

        # Text input field
        self.entry = tk.Entry(
            bottom_frame, font=("Segoe UI", 11), bg=self.BG_INPUT,
            fg=self.TEXT_COLOR, bd=0, insertbackground=self.TEXT_COLOR
        )
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=12)
        self.entry.bind("<Return>", lambda event: self.send_typed_command())
        self.entry.focus_set()

        # Send Button
        send_btn = tk.Button(
            bottom_frame, text="Send ➤", font=("Segoe UI", 10, "bold"),
            bg=self.ACCENT, fg="#11111b", activebackground=self.ACCENT_HOVER,
            bd=0, padx=16, pady=8, cursor="hand2",
            command=self.send_typed_command
        )
        send_btn.pack(side=tk.RIGHT, padx=(8, 12), pady=12)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_status_threadsafe(self, text, color="#89b4fa"):
        self.root.after(0, lambda: self._apply_status(text, color))

    def _apply_status(self, text, color):
        self.status_lbl.config(text=text)
        self.status_dot.config(fg=color)

    def display_message_threadsafe(self, sender, text):
        self.root.after(0, lambda: self._apply_message(sender, text))

    def _apply_message(self, sender, text):
        self.chat_display.config(state=tk.NORMAL)
        if sender == "You":
            self.chat_display.insert(tk.END, "👤 You: ", "You")
        elif sender == "Assistant":
            self.chat_display.insert(tk.END, "🤖 Assistant: ", "Assistant")
        else:
            self.chat_display.insert(tk.END, f"ℹ️ {sender}: ", "System")

        self.chat_display.insert(tk.END, f"{text}\n\n", "text")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_typed_command(self):
        cmd = self.entry.get().strip()
        if cmd:
            self.entry.delete(0, tk.END)
            threading.Thread(target=self.assistant.process_command, args=(cmd,), daemon=True).start()

    def toggle_continuous_listening(self):
        if self.voice_listening_active:
            self.voice_listening_active = False
            self.mic_btn.config(text="🎙️ Voice Muted", fg=self.TEXT_MUTED, bg="#313244")
            self.update_status_threadsafe("Voice Muted", "#f38ba8")
        else:
            self.voice_listening_active = True
            self.mic_btn.config(text="🎙️ Listening ON", fg="#a6e3a1", bg="#313244")
            self.update_status_threadsafe("Listening...", self.WARNING)
            if self.voice_thread is None or not self.voice_thread.is_alive():
                self.voice_thread = threading.Thread(target=self._voice_loop, daemon=True)
                self.voice_thread.start()

    def _voice_loop(self):
        import time
        while self.voice_listening_active:
            if self.assistant.tts_lock.locked():
                time.sleep(0.2)
                continue

            command = self.assistant.listen_single_turn()
            if command and self.voice_listening_active:
                self.assistant.process_command(command)

    def on_closing(self):
        self.voice_listening_active = False
        try:
            self.root.destroy()
        except Exception:
            pass
        sys.exit(0)


def launch():
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch()
