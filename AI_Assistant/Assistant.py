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
import datetime
import requests
import webbrowser
import pyjokes
import random
import re
import os
import subprocess
import pyautogui
import opener

try:
    import pywhatkit
except Exception:
    pywhatkit = None

_tts_engine = None

def get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        try:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except Exception:
                pass
            _tts_engine = pyttsx3.init()
            _tts_engine.setProperty('rate', 160)
            try:
                voices = _tts_engine.getProperty('voices')
                if voices:
                    _tts_engine.setProperty('voice', voices[0].id)
            except Exception:
                pass
        except Exception as e:
            print(f"TTS init warning: {e}")
            _tts_engine = None
    return _tts_engine

def speak(text):
    print(f"Assistant: {text}")
    engine = get_tts_engine()
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")

def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good morning!")
    elif hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak("How can I help you today?")

def search_wikipedia_summary(query):
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
            sentences = [s.strip() for s in extract.split('. ') if s.strip()]
            return '. '.join(sentences[:2]) + '.'
    except Exception as e:
        print(f"Wiki error: {e}")
    return None

def evaluate_math(text):
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

def open_website(command):
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
            speak(f"Opening {key.capitalize()}")
            webbrowser.open(url)
            return True
    m = re.search(r'open\s+([a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,})', command)
    if m:
        domain = m.group(1)
        url = f"https://{domain}" if not domain.startswith("http") else domain
        speak(f"Opening {domain}")
        webbrowser.open(url)
        return True
    return False

def handle_system_apps(command):
    if "camera" in command or "webcam" in command:
        speak("Opening Camera")
        subprocess.Popen(["cmd", "/c", "start", "microsoft.windows.camera:"], shell=True)
        return True
    elif "notepad" in command:
        speak("Opening Notepad")
        subprocess.Popen(["notepad.exe"])
        return True
    elif "calculator" in command or "calc" in command:
        speak("Opening Calculator")
        subprocess.Popen(["calc.exe"])
        return True
    elif "paint" in command:
        speak("Opening Paint")
        subprocess.Popen(["mspaint.exe"])
        return True
    elif "command prompt" in command or "cmd" in command or "terminal" in command:
        speak("Opening Command Prompt")
        subprocess.Popen(["cmd.exe"])
        return True
    elif "settings" in command:
        speak("Opening Windows Settings")
        os.system("start ms-settings:")
        return True
    elif "file explorer" in command or "files" in command or "my computer" in command or "this pc" in command:
        speak("Opening File Explorer")
        subprocess.Popen(["explorer.exe"])
        return True
    elif "task manager" in command:
        speak("Opening Task Manager")
        subprocess.Popen(["taskmgr.exe"])
        return True
    elif "snipping tool" in command or "snip" in command:
        speak("Opening Snipping Tool")
        subprocess.Popen(["cmd", "/c", "start", "ms-screenclip:"], shell=True)
        return True
    elif "screenshot" in command:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop):
            desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(desktop, f"screenshot_{ts}.png")
        pyautogui.screenshot(filepath)
        speak("Screenshot captured and saved to your Desktop!")
        return True
    elif "volume up" in command or "increase volume" in command:
        pyautogui.press('volumeup', presses=5)
        speak("Turned the volume up")
        return True
    elif "volume down" in command or "decrease volume" in command:
        pyautogui.press('volumedown', presses=5)
        speak("Turned the volume down")
        return True
    elif "mute" in command or "unmute" in command:
        pyautogui.press('volumemute')
        speak("Toggled mute")
        return True
    return False

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        recognizer.pause_threshold = 0.8
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""
        except Exception:
            return ""

        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            speak("Sorry, I'm having trouble connecting to speech recognition.")
            return ""

def run_assistant():
    greet_user()
    while True:
        command = take_command()
        if not command:
            continue

        # 1. Exit / Stop
        if any(w in command for w in ["stop", "exit", "quit", "goodbye", "bye", "close assistant"]):
            speak("Goodbye! Have a nice day!")
            break

        # 2. Greetings
        if re.search(r'\b(hello|hi|hey|good morning|good evening|good afternoon|namaste|sup|what\'s up)\b', command):
            responses = [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Hey! I'm here and listening."
            ]
            speak(random.choice(responses))
            continue

        # 3. Help
        if any(w in command for w in ["what can you do", "help", "commands", "features"]):
            speak("I can play music on YouTube, answer questions with Wikipedia, open apps like Notepad and Calculator, tell time and date, do calculations, tell jokes, and search Google!")
            continue

        # 4. Identity & Small Talk
        if any(p in command for p in ["who are you", "what is your name", "who created you"]):
            speak("I'm your personal AI desktop assistant!")
            continue

        if any(p in command for p in ["how are you", "how are you doing"]):
            speak("I'm doing great, thank you! Ready to help you.")
            continue

        if any(p in command for p in ["thank you", "thanks"]):
            speak("You're very welcome!")
            continue

        # 5. Math
        math_ans = evaluate_math(command)
        if math_ans:
            speak(math_ans)
            continue

        # 6. Time & Date
        if "time" in command and not ("play" in command or "search" in command):
            now = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {now}")
            continue

        if "date" in command or "today's day" in command:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            speak(f"Today is {today}")
            continue

        # 7. Joke & Fact
        if "joke" in command or "make me laugh" in command or "funny" in command:
            joke = pyjokes.get_joke()
            speak(joke)
            continue

        if "fact" in command or "something cool" in command:
            facts = [
                "Did you know? Octopuses have three hearts and blue blood!",
                "Did you know? Honey never spoils across thousands of years!",
                "Did you know? A day on Venus is longer than a whole year on Venus!"
            ]
            speak(random.choice(facts))
            continue

        # 8. Music & Video
        if re.search(r'\b(play|song|music|listen to)\b', command):
            song = re.sub(r'^(play music|play song|play|can you play|listen to)\s*', '', command, flags=re.IGNORECASE).strip()
            song = song.replace("on youtube", "").strip()
            if not song:
                song = "top trending music"
            speak(f"Playing {song} on YouTube")
            played = False
            if pywhatkit is not None:
                try:
                    pywhatkit.playonyt(song)
                    played = True
                except Exception:
                    pass
            if not played:
                webbrowser.open(f"https://www.youtube.com/results?search_query={requests.utils.quote(song)}")
            continue

        # Hardware & Media controls (Volume, Screenshot, Mute)
        if any(w in command for w in ["screenshot", "volume up", "increase volume", "volume down", "decrease volume", "lower volume", "mute", "unmute"]):
            if handle_system_apps(command):
                continue

        # 9. Universal Opener: Opens ANY app, tool, folder, website, or web service
        if re.search(r'\b(open|launch|start|go to)\b', command) or len(command.split()) <= 3:
            opened, msg = opener.universal_open(command)
            if opened:
                speak(msg)
                continue

        # 11. Explicit Google Search
        if re.search(r'\b(search for|search|google)\b', command):
            query = re.sub(r'^(search for|search google for|search|google for|google)\s*', '', command, flags=re.IGNORECASE).strip()
            if query:
                speak(f"Searching Google for {query}")
                webbrowser.open(f"https://www.google.com/search?q={requests.utils.quote(query)}")
                continue

        # 12. Knowledge & Wikipedia Queries
        if re.search(r'^(who is|who was|what is|what are|where is|tell me about|explain|wikipedia)\b', command):
            wiki_result = search_wikipedia_summary(command)
            if wiki_result:
                speak(wiki_result)
                continue
            else:
                query = re.sub(r'^(who is|who was|what is|what are|where is|tell me about|explain|wikipedia)\s*', '', command, flags=re.IGNORECASE).strip()
                speak(f"Opening Google search results for {query}")
                webbrowser.open(f"https://www.google.com/search?q={requests.utils.quote(query)}")
                continue

        # 13. Smart Fallback: NEVER dead-end
        wiki_res = search_wikipedia_summary(command)
        if wiki_res:
            speak(wiki_res)
            continue

        speak(f"Here is what I found on Google for {command}")
        webbrowser.open(f"https://www.google.com/search?q={requests.utils.quote(command)}")

if __name__ == "__main__":
    run_assistant()
