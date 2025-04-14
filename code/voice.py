import speech_recognition as sr
import pyttsx3
import pyautogui
import webbrowser
import subprocess
import audioop
from gesture import GestureMediaControl


# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 175)

gesture = GestureMediaControl()

def speak(text):

    engine.say(text)
    engine.runAndWait()



def is_voice_close_enough(audio_data, threshold=300):
    raw_data = audio_data.get_raw_data()
    sample_width = audio_data.sample_width
    rms = audioop.rms(raw_data, sample_width)  #Computing RMS volume
    return rms > threshold


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=2)
            audio = recognizer.listen(source, timeout=10)

            # for checking if voice is close enough
            if not is_voice_close_enough(audio, threshold=300):  
                print("Voice too soft or far, ignoring.")
                return None

            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text

        except sr.UnknownValueError:
            print("Could not understand.")
        except sr.RequestError:
            print("Check your internet connection.")
            speak("Check your internet connection.")
        except sr.WaitTimeoutError:
            print("Listening timed out.")
    return None

def open_application(app_name):
    app_name = app_name.lower()

    # System Apps
    system_apps = {
        "file explorer": "explorer",
        "task manager": "taskmgr",
        "control panel": "control",
        "settings": "start ms-settings:"
    }

    if app_name in system_apps:
        print(f"Opening {app_name}")
        subprocess.run(system_apps[app_name], shell=True)
        return

    # Microsoft store apps
    store_apps = {

        "photos": "Microsoft.Windows.Photos_8wekyb3d8bbwe!App",
        "camera": "Microsoft.WindowsCamera_8wekyb3d8bbwe!App",
        "calculator": "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App",
        "mail": "microsoft.windowscommunicationsapps_8wekyb3d8bbwe!microsoft.windowslive.mail",
        "calendar": "microsoft.windowscommunicationsapps_8wekyb3d8bbwe!microsoft.windowslive.calendar"
    }

    if app_name in store_apps:
        
        subprocess.run(f"explorer shell:AppsFolder\\{store_apps[app_name]}", shell=True)
        print(f"Opening {app_name}")
        return

    try:
        subprocess.run(f"start {app_name}", shell=True)
        print(f"Opening {app_name}")
        return
    except FileNotFoundError:
        print(f"Unable to find {app_name}. Please check the name.")
        return

def notepad_mode():
    speak("Start dictating. Say 'exit' to stop.")

    while True:
        command = listen()
        if command:
            if "exit notepad" in command:
                speak("Exiting dictation.")
                print("Exiting notepad mode")
                break
            print(f"Writing \"{command}\"")
            pyautogui.typewrite(command + " ", interval=0.05)


def execute_command(command):

    if "youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif "spotify web" in command:
        speak("Opening Spotify")
        webbrowser.open("https://open.spotify.com")
    
    elif "netflix" in command:
        speak("Opening Netflix")
        webbrowser.open("https://www.netflix.com")
    
    elif "amazon prime" in command or "prime video" in command:
        speak("Opening Amazon Prime Video")
        webbrowser.open("https://www.primevideo.com")

    elif "open" in command:
        app_name = command.replace("open", "").strip()
        if app_name=="notepad":
            speak("Starting notepad mode")
            print("Starting notepad mode.")
            open_application(app_name)
            notepad_mode()
        else:
            open_application(app_name)

    elif "enable gesture" in command:
        speak("Gesture recognition enabled")
        gesture.start()   

    elif "play" in command or "resume" in command:
        pyautogui.press("space")

    elif "pause" in command or "stop" in command:
        pyautogui.press("space")

    elif "increase volume" in command:
        pyautogui.press("volumeup", presses=5)

    elif "decrease volume" in command:
        pyautogui.press("volumedown", presses=5)

    elif "mute" in command:
        pyautogui.press("volumemute")

    elif "next" in command:
        pyautogui.hotkey("ctrl", "right")

    elif "previous" in command:
        pyautogui.hotkey("ctrl", "left")

    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "search" in command:
        search_query = command.replace("search", "").strip()
        if search_query:
            speak(f"Searching for {search_query}")
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
        else:
            speak("What do you want to search for?")

    elif "exit" in command or "quit" in command or "stop" in command:
        speak("Goodbye!")
        exit()

def voice_assistant():

    wake_word = "hello media"
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("Listening for wake word...")
        recognizer.adjust_for_ambient_noise(source)

        try:

            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio).lower()

            if wake_word in text:
                print("Wake word detected! Activating assistant...")
                speak("Hello, I am your assistant. How can I help you?")

            else:
                print("Wake word not detected. Exiting...")
                return
            
        except sr.UnknownValueError:
            print("Wake word not detected.")
            return
        
        except sr.RequestError:
            print("Error processing wake word.")
            return

    while True:

        command = listen()
        if command:
            execute_command(command)

if __name__ == "__main__":
    voice_assistant()
