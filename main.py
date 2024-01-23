import openai
import tkinter as tk
import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
from config import apikey
import psutil
import pygame
import os
import threading
import sys
from Clap import MainClapExe

MainClapExe()
pygame.init()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
def speak(audio):
    engine.say(audio)
    engine.runAndWait()
def play_song(song_path):
    pygame.mixer.init()
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

def pause_song():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()

def open_application(app_name):
    os.startfile(app_name)

def close_application(app_name):
    for proc in psutil.process_iter():
        try:
            if app_name.lower() in proc.name().lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

chatStr = []


def chat(query):
    global chatStr
    openai.api_key = apikey
    try:
        chatStr.append({'role': 'user', 'content': query})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chatStr,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        assistant_reply = response['choices'][0]['message']['content']

        chatStr.append({'role': 'assistant', 'content': assistant_reply})

        for message in chatStr:
            print(f"{message['role']}: {message['content']}")
        speak(assistant_reply)
        chatStr = []

        return assistant_reply
    except Exception as e:
        print(f"An error occurred during chat: {e}")
        return "Oops! An error occurred during chat. Please try again later."


def ai(prompt):
    text = f"OpenAI response for Prompt: {prompt} \n *************************\n\n"
    openai.api_key = apikey
    conversation = [
        {'role': 'user', 'content': f'User: {prompt}'},
        {'role': 'assistant', 'content': 'Assistant: previous assistant response, if any'}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        text += response["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error occurred during OpenAI API call:", str(e))
        return "Oops! An error occurred during the OpenAI API call. Please try again later."

    try:
        if not os.path.exists("Openai"):
            os.mkdir("Openai")

        filename = f"Openai/{''.join(prompt.split('write an')[1:]).strip()}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        print("File saved successfully.")
    except Exception as e:
        print("Error occurred while writing the file:", str(e))

class DesktopAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Desktop Assistant")

        self.label = tk.Label(self, text="Welcome to Desktop Assistant!", bg='white')
        self.label.pack(pady=10)

        self.start_button = tk.Button(self, text="Start", command=self.start_voice_command, bg="green", fg="white",
                                      activebackground="lightgreen", activeforeground="black")
        self.start_button.pack(pady=5)

        self.pause_button = tk.Button(self, text="Pause", command=self.pause_voice_command, state=tk.DISABLED, bg="red",
                                      fg="white", activebackground="salmon", activeforeground="white")
        self.pause_button.pack(pady=5)

        self.output_text = tk.Text(self, height=50, width=70, bg='white')
        self.output_text.pack(pady=10)
        self.redirect_output()
    def redirect_output(self):
        sys.stdout = self.OutputRedirector(self.output_text)

    class OutputRedirector:
        def __init__(self, text_widget):
            self.text_widget = text_widget

        def write(self, output):
            self.text_widget.insert(tk.END, output)
    def handle_voice_command(self):
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.label.configure(text="Listening...")

        def voice_command_thread():
            while self.voice_command_active:
                command = self.listen()

                if command:
                    self.label.configure(text=f"You said: {command}")
                    self.process_command(command)


                if not self.voice_command_active:
                    break

            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.label.configure(text="Welcome to Desktop Assistant!")


        voice_thread = threading.Thread(target=voice_command_thread)
        voice_thread.start()

    def start_voice_command(self):
        self.voice_command_active = True
        self.handle_voice_command()

    def pause_voice_command(self):
        self.voice_command_active = False
    def listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening1...")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)

        try:
            print("Recognizing...")
            query = r.recognize_google(audio)
            print(f"You said: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
        except sr.RequestError:
            print("Sorry, my speech recognition service is currently unavailable.")

    def speak(self, audio):
        engine.say(audio)
        engine.runAndWait()

    def process_command(self, command):
        global chatStr

        if 'open' in command and 'application' in command:
            app_name = command.split(' ')[-1]
            open_application(app_name)

        elif any(keyword in command for keyword in ["open", "YouTube", "Wikipedia", "Google"]):
            for keyword, url in [["YouTube", "https://www.youtube.com"], ["Wikipedia", "https://www.wikipedia.com"], ["Google", "https://www.google.com"]]:
                if keyword.lower() in command.lower():
                    self.speak(f"Opening {keyword}...")
                    webbrowser.open(url)

        elif 'play a song' in command:
            song_path = "A:\music.mp3"
            play_song(song_path)

        elif 'stop' in command:
            pause_song()

        # elif 'open' in command and 'application' in command:
        #     app_name = command.split(' ')[-1]
        #     open_application(app_name)

        elif 'close' in command and 'application' in command:
            app_name = command.split(' ')[-1]
            close_application(app_name)


        elif "search" in command:
            query = command.split("search for ")[-1]
            speak("Searching for " + query)
            webbrowser.open("https://www.google.com/search?q=" + query)

        elif "the time" in command:
            hour = datetime.datetime.now().strftime("%H")
            min = datetime.datetime.now().strftime("%M")
            print(f"JARVIS: {hour}:{min}")
            self.speak(f"Sir, the time is {hour} o'clock {min} minutes")
            # print(f"JARVIS: {hour}:{min}")

        elif 'write an' in command:
            ai(prompt=command)

        elif 'Jarvis Quit' in command:
            self.destroy()

        elif 'reset chat' in command:
            chatStr = ""

        else:
            chat(command)

if __name__ == '__main__':
    print('Welcome to Jarvis A.I')
    speak("Jarvis A.I")
    assistant = DesktopAssistant()
    # while(1):
    assistant.mainloop()


