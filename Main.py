import json
import os
import requests
import speech_recognition as sr
import pyttsx3
import random

# Load configuration
CONFIG_FILE = "config.json"

def load_config():
    """Load API keys and other settings from config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}

config = load_config()
XAI_API_KEY = config.get("XAI_API_KEY")
if not XAI_API_KEY:
    raise ValueError("xAI API key is missing. Set it in config.json.")

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

def get_ai_response(user_input):
    """Send input to AI API and return response."""
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {XAI_API_KEY}"
            },
            json={
                "model": "grok-2-latest",
                "messages": [{"role": "user", "content": user_input}],
                "stream": False,
                "temperature": 0
            }
        )
        data = response.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        else:
            print("Unexpected API response:", data)
            return "Error: Unexpected API response format."
    except requests.exceptions.RequestException as e:
        print("API request failed:", e)
        return "Error: Failed to connect to AI service."

def main():
    """Main function to run the application and allow seamless mode switching."""
    while True:
        print("\n===== Verbal Communication Skills Trainer CLI =====")
        print("Choose an option:")
        print("1. Chat Mode")
        print("2. Voice Mode")
        print("3. Training Mode")
        print("4. Assess Presentation")
        print("5. Exit")
        
        choice = input("Enter your choice: ")
        if choice == "1":
            chat_mode()
        elif choice == "2":
            voice_mode()
        elif choice == "3":
            training_mode()
        elif choice == "4":
            assess_presentation()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

def chat_mode():
    """Engage in a text-based chat with AI."""
    print("\nChat Mode: Type your messages below. Type 'exit' to return to main menu.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        reply = get_ai_response(user_input)
        print(f"AI: {reply}")

def voice_mode():
    """Engage in voice-based interaction with AI."""
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    print("\nVoice Mode: Speak now. Say 'exit' to return to main menu.")
    
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
                
                reply = get_ai_response(user_input)
                print(f"AI: {reply}")
                engine.say(reply)
                engine.runAndWait()
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError:
                print("Speech recognition service error.")

def generate_random_prompt(topic):
    """Use LLM to generate a random prompt for a given topic."""
    prompt_request = f"Generate a random prompt for a {topic} exercise. Keep it concise and engaging."
    return get_ai_response(prompt_request)

def training_mode():
    """Skill training activities: Impromptu Speaking, Storytelling, Conflict Resolution."""
    topics = {
        "1": {
            "name": "Impromptu Speaking",
            "feedback_prompt": "Evaluate the following response for structure, clarity, and engagement. Provide scores out of 10 and offer specific improvement suggestions:"
        },
        "2": {
            "name": "Storytelling",
            "feedback_prompt": "Critique the following story for narrative flow, vocabulary richness, and emotional impact. Provide scores out of 10 and suggest improvements:"
        },
        "3": {
            "name": "Conflict Resolution",
            "feedback_prompt": "Analyze the following response for empathy, assertiveness, and diplomatic communication. Provide scores out of 10 and suggest ways to improve handling conflicts:"
        }
    }
    
    print("\nChoose a training module:")
    for key, value in topics.items():
        print(f"{key}. {value['name']}")
    
    choice = input("Enter your choice: ")
    
    if choice not in topics:
        print("Invalid choice.")
        return
    
    topic_name = topics[choice]["name"]
    random_prompt = generate_random_prompt(topic_name)
    
    print(f"\nYour task: {random_prompt}")
    user_input = input("Your response: ")
    
    # Retrieve past progress
    progress = load_progress()
    
    if topic_name in progress:
        print("\nPrevious Feedback:")
        for attempt, details in progress[topic_name].items():
            print(f"Attempt {attempt}: {details['feedback']}")
    
    # Get AI feedback
    feedback_prompt = f"{topics[choice]['feedback_prompt']}\n\n{user_input}"
    reply = get_ai_response(feedback_prompt)
    
    print("\nAI Scoring and Feedback:")
    print(reply)
    
    # Store new progress
    if topic_name not in progress:
        progress[topic_name] = {}
    attempt_number = len(progress[topic_name]) + 1
    progress[topic_name][attempt_number] = {"response": user_input, "feedback": reply}
    save_progress(progress)


def assess_presentation():
    """Assess user-submitted presentations with structured scoring."""
    print("\nAssessment Options:")
    print("1. Text Input")
    print("2. Voice Recording")
    choice = input("Enter your choice: ")
    
    if choice == "1":
        presentation_text = input("Enter your presentation text: ")
    elif choice == "2":
        recognizer = sr.Recognizer()
        print("\nRecording your presentation... Speak now.")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source)
                presentation_text = recognizer.recognize_google(audio)
                print(f"You said: {presentation_text}")
            except sr.UnknownValueError:
                print("Could not understand audio.")
                return
            except sr.RequestError:
                print("Speech recognition service error.")
                return
    else:
        print("Invalid choice.")
        return
    
    reply = get_ai_response(f"Evaluate this presentation for structure, clarity, persuasiveness, vocabulary, relevance and engagement. Provide scores out of 10 for Structure, Delivery, and Content, along with specific improvement suggestions: {presentation_text}")
    
    print("\nAI Scoring and Feedback:")
    print(reply)
    
    progress = load_progress()
    progress["presentation"] = {"response": presentation_text, "feedback": reply}
    save_progress(progress)

if __name__ == "__main__":
    main()
