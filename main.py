import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import wikipedia
import os
import subprocess
import pyautogui
import random
import time
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pyjokes
import wolframalpha  
import requests  
import json  
import calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import openai  
import pywhatkit  
from twilio.rest import Client  
import screen_brightness_control as sbc  
from datetime import datetime 
from requests.exceptions import RequestException
import pywhatkit as wtk
import time


recognizer = sr.Recognizer()
recognizer.energy_threshold = 3000
recognizer.dynamic_energy_threshold = False
recognizer.pause_threshold = 0.8

engine = pyttsx3.init()


voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  
engine.setProperty('rate', 185)
engine.setProperty('volume', 0.9)

# Configuration
WAKE_WORD = "sunny"
USER_NAME = "Sir"
COMMAND_TIMEOUT = 3
LISTEN_TIMEOUT = 4

# Google Calender setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

# API Keys 
WOLFRAMALPHA_APP_ID = 'WP5TAY-GEYJQRJW82'
OPENWEATHER_API_KEY = '0f706fad25418c757c77ce9fce54ed7c'

# Spotify Configuration
SPOTIFY_CLIENT_ID = 'cda0f86462644b37ad14b705f9b6aa12'
SPOTIFY_CLIENT_SECRET = '455eedef520d4d4a9381ee838f1ba210'
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SPOTIFY_SCOPE = 'user-read-playback-state,user-modify-playback-state,user-read-private'

# Initialize Spotify
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    ))
except Exception as e:
    print(f"Spotify initialization error: {e}")
    sp = None

# Application Paths
APPLICATIONS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
    "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
    "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vscode": "C:\\Users\\{YOUR_USERNAME}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "spotify": "C:\\Users\\{YOUR_USERNAME}\\AppData\\Roaming\\Spotify\\Spotify.exe"
}

WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "linkedin": "https://www.linkedin.com",
    "github": "https://github.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "wikipedia": "https://en.wikipedia.org"
}

def speak(text, rate=185):
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

def wish_me():
    hour = datetime.now().hour
    if hour < 12:
        speak(f"Good morning {USER_NAME}")
    elif hour < 18:
        speak(f"Good afternoon {USER_NAME}")
    else:
        speak(f"Good evening {USER_NAME}")
    speak("How may I assist you?", rate=200)

def take_command():
    try:
        with sr.Microphone() as source:
            print("\n[Listening...]")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source, 
                timeout=LISTEN_TIMEOUT,
                phrase_time_limit=COMMAND_TIMEOUT
            )
            
            print("[Processing...]")
            command = recognizer.recognize_google(audio).lower()
            print(f"Recognized: {command}")
            return command
            
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        print("Speech not understood")
        return ""
    except sr.RequestError as e:
        print(f"API Error: {e}")
        return ""
    except Exception as e:
        print(f"Error: {e}")
        return ""

def open_website(site):
    if site in WEBSITES:
        speak(f"Opening {site}")
        webbrowser.open(WEBSITES[site])
        return True
    return False

def authenticate_google_calendar():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

def parse_natural_time(time_str):
    try:
        time_str = (time_str.lower()
                   .replace("th", "")
                   .replace("st", "")
                   .replace("nd", "")
                   .replace("rd", "")
                   .replace(".", "")
                   .replace("p m", "pm")
                   .replace("a m", "am")
                   .strip())
        
        dt = datetime.strptime(time_str, "%B %d %I:%M %p")
        return dt.isoformat() + "Z"
    except ValueError as e:
        print(f"Time parsing error for '{time_str}': {e}")
        return None
def schedule_event(summary, start_time, end_time, description=""):
    try:
        start = parse_natural_time(start_time)
        end = parse_natural_time(end_time)
        
        if not start or not end:
            speak("I couldn't understand the time format. Please say something like 'July 27 2:30 PM'")
            return False

        creds = authenticate_google_calendar()
        service = build('calendar', 'v3', credentials=creds)
        
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start, 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end, 'timeZone': 'Asia/Kolkata'},
        }
        
        service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all'
        ).execute()
        
        speak(f"Success! Scheduled '{summary}' from {start_time.replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')} to {end_time.replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')}")
        return True
        
    except Exception as e:
        print(f"Scheduling Error: {e}")
        speak("Failed to schedule the event. Please try again.")
        return False
    
def set_reminder(reminder_text, reminder_time):
    try:
        if os.name == 'nt':
            subprocess.Popen(f'powershell.exe -command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{reminder_text}\')"',
                            creationflags=subprocess.CREATE_NEW_CONSOLE)
            speak(f"Reminder set for {reminder_time}")
        else:
            speak("Reminder functionality currently works best on Windows")
        return True
    except Exception as e:
        print(f"Reminder Error: {e}")
        return False

def get_huggingface_response(prompt):
    """Get AI response from HuggingFace's free Inference API"""
    try:
        API_KEY = ""  # Replace with your actual key
        
        API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": f"Explain this in simple terms: {prompt}",
            "parameters": {
                "max_new_tokens": 150,  # Limit response length
                "temperature": 0.7,     # Creativity control
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        
        # Check for API errors
        if response.status_code == 401:
            raise ValueError("Invalid HuggingFace API key")
        response.raise_for_status()
        
        return response.json()[0]['generated_text']
        
    except RequestException as e:
        print(f"API Error: {e}")
        return "I can't connect to the AI service right now."
    except Exception as e:
        print(f"Processing Error: {e}")
        return "I couldn't generate a response."

def ai_chat(prompt):
    """Wrapper with fallback knowledge base"""
    try:
        
        response = get_huggingface_response(prompt)
        
        
        if not response.strip():
            return get_local_answer(prompt)
        return response
        
    except Exception as e:
        print(f"AI Error: {e}")
        return get_local_answer(prompt)

def get_local_answer(prompt):
    """Local knowledge base fallback"""
    knowledge_base = {
        "explain blockchain": 
            "Blockchain is like a digital notebook that many computers share. "
            "Once something is written, no one can change it without everyone knowing.",
        "explain ai":
            "AI (Artificial Intelligence) means computers that can learn and "
            "make decisions somewhat like humans do.",
        
    }
    
    prompt_lower = prompt.lower()
    for question in knowledge_base:
        if question in prompt_lower:
            return knowledge_base[question]
    
    return "I don't have information about that yet."

def send_whatsapp_message(contact_name, message):
    try:
        contact_db = {
            "mom": "+91 7671885245",  
            "dad": "+91 9248087878",
            "brother": "+91 9951880874",
            "sunny": "+91 8008365637",
            "grandfather":"+91 9398532871",
        }
        
        # Get phone number from database
        phone_no = contact_db.get(contact_name.lower())
        
        if not phone_no:
            speak(f"Contact {contact_name} not found in database")
            return False
            
        # Send message
        import pywhatkit
        pywhatkit.sendwhatmsg_instantly(
            phone_no=phone_no,
            message=message,
            wait_time=15,
            tab_close=True
        )
        speak(f"Message sent to {contact_name}")
        return True
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        speak("Failed to send WhatsApp message")
        return False

def control_brightness(level):
    try:
        sbc.set_brightness(level)
        speak(f"Screen brightness set to {level}%")
        return True
    except Exception as e:
        print(f"Brightness Error: {e}")
        speak("Failed to adjust brightness")
        return False
    
def open_application(app_name):
    if app_name in APPLICATIONS:
        try:
            speak(f"Opening {app_name}")
            subprocess.Popen(APPLICATIONS[app_name])
            return True
        except Exception as e:
            print(f"Error opening {app_name}: {e}")
            speak(f"Failed to open {app_name}")
            return False
    else:
        speak(f"Application {app_name} not configured")
        return False

def search_youtube(query):
    speak(f"Searching YouTube for {query}")
    webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
    return True

def control_spotify(command):
    if sp is None:
        speak("Spotify integration is not available")
        return False
        
    try:
        # Get active devices
        devices = sp.devices().get('devices', [])
        if not devices:
            speak("No active Spotify device found. Please open Spotify on your computer or phone.")
            return False

        device_id = devices[0]['id']
        current_playback = sp.current_playback()

        # Play specific song
        if "play" in command and "spotify" in command:
            song = command.replace("play", "").replace("on spotify", "").strip()
            if song:
                results = sp.search(q=song, limit=1, type='track')
                if results['tracks']['items']:
                    track_uri = results['tracks']['items'][0]['uri']
                    sp.start_playback(device_id=device_id, uris=[track_uri])
                    speak(f"Playing {song} on Spotify")
                else:
                    speak(f"Couldn't find {song} on Spotify")
            return True
        
        # Search on Spotify
        elif "search" in command and "spotify" in command:
            query = command.replace("search", "").replace("on spotify", "").strip()
            if query:
                speak(f"Searching Spotify for {query}")
                webbrowser.open(f"https://open.spotify.com/search/{query.replace(' ', '%20')}")
            return True
        
        # Pause playback
        elif "pause" in command and "spotify" in command:
            if current_playback and current_playback['is_playing']:
                sp.pause_playback(device_id=device_id)
                speak("Paused Spotify")
            else:
                speak("Spotify is already paused")
            return True
            
        # Resume playback
        elif "resume" in command and "spotify" in command:
            if current_playback and not current_playback['is_playing']:
                sp.start_playback(device_id=device_id)
                speak("Resumed Spotify")
            else:
                speak("Spotify is already playing")
            return True
            
        # Next track
        elif "next" in command and "spotify" in command:
            sp.next_track(device_id=device_id)
            speak("Skipping to next track")
            return True
            
        # Previous track
        elif "previous" in command and "spotify" in command:
            sp.previous_track(device_id=device_id)
            speak("Playing previous track")
            return True
            
        # Volume controls
        elif "volume" in command and "spotify" in command:
            if current_playback:
                current_volume = current_playback['device']['volume_percent']
                if "up" in command:
                    new_volume = min(100, current_volume + 20)
                    sp.volume(new_volume, device_id=device_id)
                    speak(f"Volume increased to {new_volume}%")
                elif "down" in command:
                    new_volume = max(0, current_volume - 20)
                    sp.volume(new_volume, device_id=device_id)
                    speak(f"Volume decreased to {new_volume}%")
            else:
                speak("No active playback")
            return True
            
        # Toggle shuffle
        elif "shuffle" in command and "spotify" in command:
            if current_playback:
                current_state = current_playback['shuffle_state']
                sp.shuffle(not current_state, device_id=device_id)
                speak("Shuffle " + ("on" if not current_state else "off"))
            else:
                speak("No active playback")
            return True
            
        # Cycle repeat modes
        elif "repeat" in command and "spotify" in command:
            if current_playback:
                current_state = current_playback['repeat_state']
                states = ['off', 'context', 'track']
                new_state = states[(states.index(current_state) + 1 % len(states))]
                sp.repeat(new_state, device_id=device_id)
                speak(f"Repeat set to {new_state}")
            else:
                speak("No active playback")
            return True
            
        # Current song info
        elif "what's playing" in command and "spotify" in command:
            if current_playback and current_playback['is_playing']:
                track = current_playback['item']['name']
                artist = current_playback['item']['artists'][0]['name']
                speak(f"Currently playing {track} by {artist}")
            else:
                speak("Nothing is currently playing")
            return True
            
    except spotipy.SpotifyException as e:
        if e.http_status == 403:
            speak("Premium subscription required for this feature")
        else:
            print(f"Spotify API Error: {e}")
            speak("Couldn't complete the Spotify command")
        return False
    except Exception as e:
        print(f"General Error: {e}")
        speak("Spotify command failed. Please try again.")
        return False

def get_weather(city):
    try:
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}appid={OPENWEATHER_API_KEY}&q={city}"
        response = requests.get(complete_url)
        data = response.json()
        
        if data["cod"] != "404":
            main = data["main"]
            temperature = main["temp"] - 273.15  # Convert from Kelvin to Celsius
            weather_desc = data["weather"][0]["description"]
            speak(f"The temperature in {city} is {temperature:.1f}°C with {weather_desc}")
        else:
            speak("City not found")
    except Exception as e:
        print(f"Weather API Error: {e}")
        speak("Couldn't fetch weather information")

def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)


def calculate(expression):
    try:
        
        expression = expression.replace("calculate", "").replace("what is", "").strip()
        
        if not expression:
            speak("Please specify what to calculate")
            return
            
        
        if all(c in "0123456789+-*/.() " for c in expression):
            try:
                result = eval(expression)  
                speak(f"The answer is {result}")
                return
            except:
                pass  
        
        
        if 'WOLFRAMALPHA_APP_ID' in globals():
            client = wolframalpha.Client(WOLFRAMALPHA_APP_ID)
            res = client.query(expression)
            answer = next(res.results).text
            speak(f"The answer is {answer}")
        else:
            speak("Advanced calculations require WolframAlpha API setup")
            
    except Exception as e:
        print(f"Calculation Error: {e}")
        speak("I couldn't perform that calculation")

def process_command(command):
    if not command:
        speak("I didn't catch that", rate=200)
        return False
    
    command = command.lower()
    processed = True
    
    # Spotify controls
    if "spotify" in command:
        if control_spotify(command):
            return True
    
    # YouTube search
    elif "youtube" in command and ("search" in command or "play" in command):
        query = command.replace("search", "").replace("play", "").replace("on youtube", "").strip()
        if query:
            return search_youtube(query)
        else:
            speak("What should I search on YouTube?")
            return False
    
    # Website opening
    elif "open" in command:
       
        for app in APPLICATIONS:
            if app in command:
                if open_application(app):
                    return True
                
        
        for site in WEBSITES:
            if site in command:
                if open_website(site):
                    return True
        speak("Application or website not recognized")
        return False
    
    # Search command
    elif "search" in command:
        query = command.replace("search", "").strip()
        if query:
            speak(f"Searching for {query}")
            webbrowser.open(f"https://google.com/search?q={query}")
        else:
            speak("What should I search for?")
            processed = False
    
    # System controls
    elif any(cmd in command for cmd in ["shutdown", "power off"]):
        speak("Shutting down in 5 seconds")
        time.sleep(5)
        os.system("shutdown /s /t 1")
        
    elif "restart" in command:
        speak("Restarting in 5 seconds")
        time.sleep(5)
        os.system("shutdown /r /t 1")
        
    elif "sleep" in command:
        speak("Entering sleep mode")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    
    elif "brightness" in command:
        if "increase" in command:
            current = sbc.get_brightness()[0]
            control_brightness(min(100, current + 20))
        elif "decrease" in command:
            current = sbc.get_brightness()[0]
            control_brightness(max(0, current - 20))
        elif any(word in command for word in ["set", "change"]):
            level = int(''.join(filter(str.isdigit, command)))
            control_brightness(level)

    # Media controls
    elif "play music" in command and "spotify" not in command:
        music_dir = "C:\\Music"
        if os.path.exists(music_dir):
            songs = [f for f in os.listdir(music_dir) if f.endswith('.mp3')]
            if songs:
                os.startfile(os.path.join(music_dir, random.choice(songs)))
            else:
                speak("No music files found")
        else:
            speak("Music directory not found")

    # Calendar and Scheduling
    elif "schedule" in command or "set meeting" in command:
        try:
            speak("Let's schedule an event. What's it about?")
            summary = take_command()
            
            speak("When should it start? Example: 'July 26 2:30 PM' or just '2:30 PM' for today")
            start_time = take_command()
            
            speak("When should it end?")
            end_time = take_command()
            
            if summary and start_time and end_time:
                    if "p.m." not in start_time.lower() and "a.m." not in start_time.lower():
                        speak("Please specify AM or PM")
                        start_time = take_command()
                    schedule_event(summary, start_time, end_time)
            else:
                speak("Missing information. Let's try again.")
                
        except Exception as e:
            print(f"Scheduling Error: {e}")
            speak("Couldn't schedule the event. Please try again.")

    # AI Features
    elif "ask ai" in command or "explain" in command:
        query = command.replace("ask ai", "").replace("explain", "").strip()
        if query:
            response = ai_chat(query)
            speak(response)
        else:
            speak("What would you like me to explain?")

    elif "set reminder" in command:
        speak("What should I remind you about?")
        reminder_text = take_command()
        speak("When should I remind you? (Example: in 30 minutes)")
        reminder_time = take_command()
        set_reminder(reminder_text, reminder_time)

    # Messaging
    elif "send message to" in command or "whatsapp" in command:
        try:
            # Extract contact name
            if "send message to" in command:
                contact = command.split("send message to")[1].split()[0]
            else:  # whatsapp command
                contact = command.split("whatsapp")[1].split()[0]
            
            # Extract message
            message = command.split("saying")[1].strip() if "saying" in command else "Hello from Sunny"
            
            send_whatsapp_message(contact, message)
            
        except Exception as e:
            print(f"Message processing error: {e}")
            speak("I didn't understand. Format: 'Send message to [contact] saying [message]'")
    
    # Information
    elif "time" in command:
        speak(time.strftime("%I:%M %p"))
        
    elif "date" in command:
        speak(datetime.date.today().strftime("%B %d, %Y"))
        
    elif "weather" in command:
        city = command.replace("weather", "").replace("in", "").strip()
        if city:
            get_weather(city)
        else:
            speak("Which city's weather would you like to know?")
            processed = False
            
    elif any(phrase in command for phrase in ["who is", "what is"]):
        query = command.split("is", 1)[1].strip()
        try:
            result = wikipedia.summary(query, sentences=2, auto_suggest=False)
            speak(result)
        except:
            speak(f"Couldn't find information about {query}")
    
    # Utilities
    elif "joke" in command:
        tell_joke()
        
    elif "calculate" in command or "what is" in command and any(op in command for op in ["+", "-", "*", "/"]):
        expression = command.replace("calculate", "").replace("what is", "").strip()
        if expression:
            calculate(expression)
        else:
            speak("What should I calculate?")
            processed = False
    
    # Conversation
    elif "how are you" in command:
        speak("I'm functioning perfectly, thank you!")
        
    elif "your name" in command:
        speak("I am Sunny, your AI assistant")
        
    elif any(word in command for word in ["exit", "goodbye", "shut down"]):
        speak(f"Goodbye {USER_NAME}")
        sys.exit()
        
    else:
        speak("Command not recognized")
        processed = False
    
    return processed

def print_help():
    print("\nAvailable Commands:")
    print("-------------------")
    print("1. Media Controls:")
    print(" - 'Sunny play [song] on spotify' - Play specific song")
    print(" - 'Sunny search [query] on spotify' - Search on Spotify")
    print(" - 'Sunny pause/resume spotify' - Control playback")
    print(" - 'Sunny play [video] on youtube' - Search YouTube")
    print(" - 'Sunny play music' - Play local music")
    
    print("\n2. Application Controls:")
    print(" - 'Sunny open [app]' - Open applications (notepad, word, excel, etc.)")
    print(" - 'Sunny open [website]' - Open websites (google, youtube, etc.)")
    
    print("\n3. System Controls:")
    print(" - 'Sunny shutdown' - Shutdown computer")
    print(" - 'Sunny restart' - Restart computer")
    print(" - 'Sunny sleep' - Put computer to sleep")
    
    print("\n4. Information:")
    print(" - 'Sunny what time is it' - Current time")
    print(" - 'Sunny what is today's date' - Current date")
    print(" - 'Sunny weather in [city]' - Weather information")
    print(" - 'Sunny who/what is [query]' - Wikipedia search")
    
    print("\n5. Utilities:")
    print(" - 'Sunny search [query]' - Web search")
    print(" - 'Sunny calculate [expression]' - Math calculation")
    print(" - 'Sunny tell me a joke' - Hear a joke")

    print("\n" + "📅 Calender And Scheduling".ljust(50, ' '))
    print("-"*50)
    print("- 'Schedule a meeting about [topic] on [date/time]'")
    print("- 'Add event [description] at [time]'")
    print("- 'Show my calendar for [day/week]'")
    print("- 'Set reminder to [action] in [time]'")
    print("- 'Cancel my next meeting'")


    print("\n" + "🤖 AI & SMART FEATURES".ljust(50, ' '))
    print("-"*50)
    print("| 'Ask AI: [your question]'")
    print("| 'Explain [concept] simply'")
    print("| 'Generate [poem/story] about [topic]'")
    print("| 'Summarize [topic]'")

    print("\n" + "📱 MESSAGING & COMMUNICATION".ljust(50, ' '))
    print("-"*50)
    print("| 'Send WhatsApp to [contact] saying [message]'")
    print("| 'Text [contact] [message]'")
    print("| 'Read my last notification'")
    print("| 'Check for new emails'")
    
    print("\n6. Conversation:")
    print(" - 'Sunny how are you'")
    print(" - 'Sunny what's your name'")
    print(" - 'Sunny goodbye' - Exit Sunny")

if __name__ == "__main__":
    print_help()
    speak("Sunny initializing", rate=240)
    wish_me()
    
    while True:
        print(f"\n[Ready] Say '{WAKE_WORD}' to activate")
        command = take_command()
        
        if WAKE_WORD in command:
            speak("Yes?", rate=200)
            start_time = time.time()
            
            while time.time() - start_time < 10:  # 10 second command window
                command = take_command()
                if command:
                    if process_command(command):
                        break