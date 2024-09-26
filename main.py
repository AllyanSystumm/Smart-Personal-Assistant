import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import random
import schedule
import time
import spacy
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Initialize NLP Model
nlp = spacy.load('en_core_web_sm')

# Initialize the speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Set female voice

# Function to make the assistant speak
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# Function to take voice commands
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        print("Could not understand, please say that again.")
        return "None"
    return query

# Process query using NLP (spaCy)
def process_query(query):
    doc = nlp(query)
    return doc

# Suggest a random activity
def suggest_activity():
    activities = ["Read a book", "Go for a walk", "Take a 5-minute meditation", 
                  "Plan your day", "Do some stretching exercises", "Review your to-do list"]
    return random.choice(activities)

# Reminder management
def reminder(task):
    speak(f"Reminder: {task}")

def add_reminder(task, time_str):
    schedule.every().day.at(time_str).do(reminder, task)

# File Management
def create_file(file_name, content):
    with open(file_name, 'w') as file:
        file.write(content)
    return f"File '{file_name}' created."

def open_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            return file.read()
    else:
        return f"File '{file_name}' does not exist."

# Google Calendar Integration
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_upcoming_events():
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        return "No upcoming events found."
    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_list.append(f"{start}: {event['summary']}")
    return '\n'.join(event_list)

# Main function that processes user commands
def main():
    speak("Hello, I am your Smart Personal Assistant. How can I help you today?")
    
    while True:
        query = take_command().lower()
        doc = process_query(query)
        
        if 'wikipedia' in query:
            speak("Searching Wikipedia...")
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            speak(results)
        
        elif 'open youtube' in query:
            webbrowser.open("youtube.com")
        
        elif 'open google' in query:
            webbrowser.open("google.com")
        
        elif 'open stackoverflow' in query:
            webbrowser.open("stackoverflow.com")
        
        elif 'play music' in query:
            music_dir = 'path_to_music_folder'  # Update this path
            songs = os.listdir(music_dir)
            os.startfile(os.path.join(music_dir, songs[0]))

        elif 'suggest an activity' in query:
            activity = suggest_activity()
            speak(f"How about you {activity}?")

        elif 'remind me' in query:
            speak("What is the task?")
            task = take_command()
            speak("At what time should I remind you? (24-hour format HH:MM)")
            time_str = take_command()
            add_reminder(task, time_str)
            speak(f"Reminder for '{task}' set at {time_str}")

        elif 'create file' in query:
            speak("What is the file name?")
            file_name = take_command().lower() + ".txt"
            speak("What content should I write?")
            content = take_command()
            status = create_file(file_name, content)
            speak(status)

        elif 'open file' in query:
            speak("Which file do you want to open?")
            file_name = take_command().lower() + ".txt"
            file_content = open_file(file_name)
            speak(file_content)
        
        elif 'show my events' in query:
            events = get_upcoming_events()
            speak(f"Here are your upcoming events:\n{events}")

        elif 'stop' in query:
            speak("Goodbye!")
            break

        # Run pending scheduled tasks
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
