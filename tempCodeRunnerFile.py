try:
    import speech_recognition as sr
    import pyttsx3
    import webbrowser
    import datetime
    import wikipedia
    import os
    import subprocess
    import pyautogui
    import random
    from time import sleep
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install missing packages using:")
    print("pip install SpeechRecognition pyttsx3 wikipedia pyautogui")
    exit()


# Initialize components
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set voice properties (adjust as needed)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # 0 for male, 1 for female
engine.setProperty('rate', 150)  # Speed of speech

# Wolfram Alpha API (for computational questions)
WOLFRAM_ALPHA_APP_ID = 'YOUR_APP_ID'  # Replace with your actual API key

# Configuration
WAKE_WORD = "jarvis"
USER_NAME = "Sir"  # Change to whatever you prefer

def speak(text, rate=150):
    """Converts text to speech with adjustable rate."""
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

def wish_me():
    """Greets the user based on time of day."""
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak(f"Good morning {USER_NAME}, how may I assist you today?")
    elif 12 <= hour < 18:
        speak(f"Good afternoon {USER_NAME}, how may I assist you today?")
    else:
        speak(f"Good evening {USER_NAME}, how may I assist you today?")

def take_command():
    """Takes microphone input and returns text."""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("Recognizing...")
            command = recognizer.recognize_google(audio).lower()
            print(f"User said: {command}\n")
            return command
    except sr.WaitTimeoutError:
        print("Listening timed out.")
        return ""
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""
    except Exception as e:
        print(f"Error in take_command: {e}")
        return ""

def process_command(command):
    """Processes the command and performs actions."""
    if not command:
        return
    
    # Web browsing
    if "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
        
    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
        
    elif "open linkedin" in command:
        speak("Opening LinkedIn")
        webbrowser.open("https://www.linkedin.com")
        
    elif "open github" in command:
        speak("Opening GitHub")
        webbrowser.open("https://github.com")
        
    elif "open instagram" in command:
        speak("Opening Instagram")
        webbrowser.open("https://www.instagram.com")
        
    elif "search" in command:
        query = command.replace("search", "").strip()
        if query:
            speak(f"Searching for {query}")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        else:
            speak("What would you like me to search for?")
            
    # System controls
    elif "shutdown" in command or "power off" in command:
        speak("Shutting down the system in 5 seconds")
        sleep(5)
        os.system("shutdown /s /t 1")
        
    elif "restart" in command:
        speak("Restarting the system in 5 seconds")
        sleep(5)
        os.system("shutdown /r /t 1")
        
    elif "sleep" in command:
        speak("Putting system to sleep")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        
    # Applications
    elif "open notepad" in command:
        speak("Opening Notepad")
        subprocess.Popen(["notepad.exe"])
        
    elif "open calculator" in command:
        speak("Opening Calculator")
        subprocess.Popen("calc.exe")
        
    elif "open command prompt" in command:
        speak("Opening Command Prompt")
        os.system("start cmd")
        
    # Media control
    elif "play music" in command:
        music_dir = "C:\\Music"  # Change to your music directory
        songs = os.listdir(music_dir)
        if songs:
            os.startfile(os.path.join(music_dir, random.choice(songs)))
        else:
            speak("No music files found in the directory")
            
    elif "pause" in command or "resume" in command:
        pyautogui.press('playpause')
        speak("Media playback toggled")
        
    elif "volume up" in command:
        pyautogui.press('volumeup')
        speak("Volume increased")
        
    elif "volume down" in command:
        pyautogui.press('volumedown')
        speak("Volume decreased")
        
    elif "mute" in command or "unmute" in command:
        pyautogui.press('volumemute')
        speak("Volume muted/unmuted")
        
    # Information
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
        
    elif "date" in command:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
        
    elif "who is" in command or "what is" in command:
        query = command.replace("who is", "").replace("what is", "").strip()
        try:
            result = wikipedia.summary(query, sentences=2)
            speak(f"According to Wikipedia: {result}")
        except wikipedia.exceptions.DisambiguationError as e:
            speak(f"Multiple results found. Can you be more specific about {query}?")
        except wikipedia.exceptions.PageError:
            speak(f"I couldn't find information about {query}")
            
    elif "calculate" in command:
        try:
            client = wolframalpha.Client(WOLFRAM_ALPHA_APP_ID)
            res = client.query(command)
            answer = next(res.results).text
            speak(f"The answer is {answer}")
        except Exception:
            speak("I couldn't calculate that. Please try a different query.")
            
    # Personal assistant functions
    elif "how are you" in command:
        responses = [
            "I'm functioning optimally, thank you for asking.",
            "I'm doing well, ready to assist you.",
            "All systems are operational. How may I help you?"
        ]
        speak(random.choice(responses))
        
    elif "thank you" in command:
        speak("You're welcome! Is there anything else I can do for you?")
        
    elif "your name" in command:
        speak("I am JARVIS, your personal AI assistant.")
        
    elif "who made you" in command or "created you" in command:
        speak("I was created by a talented developer to assist you with various tasks.")
        
    elif "exit" in command or "goodbye" in command or "shut down" in command:
        speak(f"Goodbye {USER_NAME}. Have a great day!")
        exit()
        
    else:
        speak("I didn't understand that command. Could you please repeat?")

if __name__ == "__main__":
    speak("Initializing JARVIS... Systems online.")
    wish_me()
    
    while True:
        print(f"\nWaiting for wake word '{WAKE_WORD}'...")
        command = take_command()
        
        if WAKE_WORD in command:
            speak("Yes? How may I assist you?")
            command = take_command()
            process_command(command)
        elif command:  # If command exists but no wake word
            print(f"Command detected but wake word '{WAKE_WORD}' not found.")