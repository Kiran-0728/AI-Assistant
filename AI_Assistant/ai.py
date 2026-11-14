import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import pyjokes
import random
import os

try:
    import pywhatkit
except Exception:
    pywhatkit = None

# Initialize text-to-speech engine
_engine = None
def get_engine():
    global _engine
    if _engine is None:
        try:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except Exception:
                pass
            _engine = pyttsx3.init()
            _engine.setProperty('rate', 150)
        except Exception as e:
            print(f"TTS init error: {e}")
            _engine = None
    return _engine

def speak(text):
    """Convert text to speech"""
    print(f"Assistant: {text}")
    eng = get_engine()
    if eng:
        try:
            eng.say(text)
            eng.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")

def greet_user():
    """Greet based on time of day"""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greet = "Good morning"
    elif 12 <= hour < 17:
        greet = "Good afternoon"
    elif 17 <= hour < 21:
        greet = "Good evening"
    else:
        greet = "Hello"
    try:
        user_name = os.getlogin().capitalize()
    except Exception:
        user_name = "there"
    speak(f"{greet}, {user_name}! How can I assist you?")

def listen():
    """Listen for voice commands"""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            speak("Could not connect to Google Speech Recognition.")
            return ""
    except Exception as e:
        print(f"Microphone error: {e}")
        return ""

def play_local_music(folder_path):
    """Play a random music file from a folder"""
    try:
        songs = os.listdir(folder_path)
        music_files = [song for song in songs if song.endswith(('.mp3', '.wav'))]
        if music_files:
            song = random.choice(music_files)
            os.startfile(os.path.join(folder_path, song))
            speak(f"Playing {song}")
        else:
            speak("No music files found in the folder.")
    except Exception as e:
        speak("I couldn't play music from your folder.")
        print(e)

def execute_command(command):
    """Execute command based on voice input"""
    if "time" in command:
        time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {time}")

    elif "search for" in command:
        query = command.replace("search for", "").strip()
        speak(f"Searching for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    elif "play" in command:
        song = command.replace("play", "").strip()
        speak(f"Playing {song} on YouTube")
        played = False
        if pywhatkit:
            try:
                pywhatkit.playonyt(song)
                played = True
            except Exception:
                pass
        if not played:
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")

    elif "wikipedia" in command:
        topic = command.replace("wikipedia", "").strip()
        try:
            summary = wikipedia.summary(topic, sentences=1)
            speak(summary)
        except wikipedia.exceptions.DisambiguationError:
            speak("There are multiple results. Please be more specific.")
        except Exception:
            speak("Sorry, I couldn't find that on Wikipedia.")

    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif "open gmail" in command:
        speak("Opening Gmail")
        webbrowser.open("https://mail.google.com")

    elif "joke" in command:
        joke = pyjokes.get_joke()
        speak(joke)

    elif "play music" in command:
        music_folder = os.path.join(os.path.expanduser("~"), "Music")
        play_local_music(music_folder)

    elif "how are you" in command:
        speak("I'm doing great, thanks for asking! How can I help you today?")

    elif "tell me something cool" in command:
        speak("Did you know? Octopuses have three hearts and blue blood!")

    elif "exit" in command or "goodbye" in command:
        speak("Goodbye! Have a nice day.")
        exit()

    else:
        speak("I didn't understand that command.")

if __name__ == "__main__":
    # Run the assistant
    greet_user()
    while True:
        command = listen()
        if command:
            execute_command(command)
