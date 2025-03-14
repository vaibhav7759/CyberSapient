import openai
import json
import os
import speech_recognition as sr
import pyttsx3

# Load configuration
CONFIG_FILE = "config.json"

def load_config():
    """Load API keys and other settings from config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}

config = load_config()
OPENAI_API_KEY = config.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is missing. Set it in config.json.")

def load_progress():
    """Load user progress from a JSON file."""
    if os.path.exists("progress.json"):
        with open("progress.json", "r") as file:
            return json.load(file)
    return {}

def save_progress(data):
    """Save user progress to a JSON file."""
    with open("progress.json", "w") as file:
        json.dump(data, file, indent=4)

def chat_mode():
    """Engage in a text-based chat with AI."""
    print("\nChat Mode: Type your messages below. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_input}]
        )
        reply = response['choices'][0]['message']['content']
        print(f"AI: {reply}")

def voice_mode():
    """Engage in voice-based interaction with AI."""
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    print("\nVoice Mode: Speak now. Say 'exit' to quit.")
    
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            try:
                audio = recognizer.listen(source)
                user_input = recognizer.recognize_google(audio)
                print(f"You: {user_input}")
                
                if user_input.lower() == "exit":
                    break
                
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": user_input}]
                )
                reply = response['choices'][0]['message']['content']
                print(f"AI: {reply}")
                engine.say(reply)
                engine.runAndWait()
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError:
                print("Speech recognition service error.")

def main():
    """Main CLI function to select modes."""
    progress = load_progress()
    
    print("Welcome to the Verbal Communication Skills Trainer CLI!")
    print("Choose an option:")
    print("1. Chat Mode")
    print("2. Voice Mode")
    print("3. Exit")
    
    choice = input("Enter your choice: ")
    if choice == "1":
        chat_mode()
    elif choice == "2":
        voice_mode()
    elif choice == "3":
        print("Goodbye!")
        save_progress(progress)
        exit()
    else:
        print("Invalid choice. Try again.")
        main()

if __name__ == "__main__":
    main()
