import streamlit as st
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv
import os
import speech_recognition as sr
import pyttsx3
import threading
import queue

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(page_title="Jarvis AI Assistant", page_icon="🤖")

# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Voice interaction queue
voice_queue = queue.Queue()

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen to voice commands
def listen_for_voice():
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio)
            return text.lower()
        except sr.UnknownValueError:
            st.write("🤖 Sorry, I didn't catch that. Could you repeat?")
            return None
        except sr.RequestError:
            st.write("🤖 Sorry, there was an issue with the speech recognition service.")
            return None

# Function to initialize OpenAI
def init_openai(api_key=None):
    # Try to get API key from environment if not provided
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        try:
            return OpenAI(api_key=api_key)
        except Exception as e:
            st.error(f"OpenAI initialization error: {e}")
    return None

# Function to initialize Google Gemini
def init_gemini(api_key=None):
    # Try to get API key from environment if not provided
    if not api_key:
        api_key = os.getenv('GOOGLE_API_KEY')
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.error(f"Gemini initialization error: {e}")
    return None

# Predefined command handlers
def handle_time():
    from datetime import datetime
    return f"Current time is: {datetime.now().strftime('%I:%M %p')}"

def handle_date():
    from datetime import datetime
    return f"Today's date is: {datetime.now().strftime('%B %d, %Y')}"

def handle_system_info():
    import platform
    return f"""
    System Information:
    - OS: {platform.system()}
    - Release: {platform.release()}
    - Machine: {platform.machine()}
    """

def handle_weather():
    return "Sorry, weather API integration is not implemented in this version."

# Voice command handlers
def process_voice_command(command, openai_model, gemini_model):
    # Predefined commands dictionary
    commands = {
        "time": handle_time,
        "date": handle_date,
        "system": handle_system_info,
        "weather": handle_weather
    }

    # Check for predefined commands
    if command in commands:
        response = commands[command]()
        speak(response)
        return response

    # AI-powered response
    if openai_model:
        try:
            response = openai_model.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant named Jarvis. Respond conversationally."},
                    {"role": "user", "content": command}
                ]
            ).choices[0].message.content
            speak(response)
            return response
        except Exception as e:
            st.error(f"OpenAI error: {e}")
    
    # Fallback to Gemini
    if gemini_model:
        try:
            response = gemini_model.generate_content(command).text
            speak(response)
            return response
        except Exception as e:
            st.error(f"Gemini error: {e}")

    return "Sorry, I couldn't process your request."

# Voice interaction thread
def voice_interaction_thread(openai_model, gemini_model):
    while True:
        command = voice_queue.get()
        if command is None:
            break
        process_voice_command(command, openai_model, gemini_model)
        voice_queue.task_done()

# Main application logic
def main():
    # Sidebar for configuration
    st.sidebar.header("AI Assistant Configuration")

    # Check and initialize models
    openai_model = init_openai()
    gemini_model = init_gemini()

    # If no API keys found in environment, prompt user
    if not openai_model:
        st.sidebar.warning("OpenAI API Key not found in environment.")
        openai_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
        if openai_api_key:
            openai_model = init_openai(openai_api_key)

    if not gemini_model:
        st.sidebar.warning("Google Gemini API Key not found in environment.")
        gemini_api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")
        if gemini_api_key:
            gemini_model = init_gemini(gemini_api_key)

    # Voice interaction setup
    st.sidebar.subheader("Voice Interaction")
    voice_button = st.sidebar.button("🎤 Start Voice Command")

    # Text input
    user_input = st.chat_input("What can I help you with?")

    # Voice or text input processing
    if voice_button:
        try:
            # Start voice interaction thread
            voice_thread = threading.Thread(target=voice_interaction_thread, args=(openai_model, gemini_model))
            voice_thread.start()

            # Listen for voice command
            voice_command = listen_for_voice()
            if voice_command:
                voice_queue.put(voice_command)
                st.write(f"🎤 You said: {voice_command}")
        except Exception as e:
            st.error(f"Voice interaction error: {e}")

    # Text input processing
    if user_input:
        # Process text input using AI
        if openai_model:
            try:
                response = openai_model.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant named Jarvis."},
                        {"role": "user", "content": user_input}
                    ]
                ).choices[0].message.content
                st.write("🤖 OpenAI Response:", response)
            except Exception as e:
                st.error(f"OpenAI error: {e}")
                
                # Fallback to Gemini if OpenAI fails
                if gemini_model:
                    try:
                        response = gemini_model.generate_content(user_input).text
                        st.write("🤖 Gemini Response:", response)
                    except Exception as e:
                        st.error(f"Gemini error: {e}")
                        st.warning("No alternative AI model available.")
        
        # If OpenAI is not available, use Gemini
        elif gemini_model:
            try:
                response = gemini_model.generate_content(user_input).text
                st.write("🤖 Gemini Response:", response)
            except Exception as e:
                st.error(f"Gemini error: {e}")
        
        else:
            st.warning("Please provide an API key for OpenAI or Google Gemini")

if __name__ == "__main__":
    main()