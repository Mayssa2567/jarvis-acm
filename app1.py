import streamlit as st
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipedia
import random

# Global initializations
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# from gtts import gTTS
# import os

# def speak(text):
#     """Convert text to speech using gTTS"""
#     try:
#         tts = gTTS(text=text, lang='en')
#         tts.save("output.mp3")
#         st.audio("output.mp3", format="audio/mp3", start_time=0)
#         os.remove("output.mp3")  # Clean up
#     except Exception as e:
#         st.write(f"❌ TTS error: {e}")

def speak(text):
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to user's voice input"""
    with sr.Microphone() as source:
        st.write("🎙️ Listening... Speak now")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
        try:
            command = recognizer.recognize_google(audio)
            return command.lower()
        except:
            st.write("❌ Sorry, I couldn't understand you.")
            return ""

def get_time():
    """Get current time"""
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    return f"The current time is {current_time}"

def get_date():
    """Get current date"""
    current_date = datetime.datetime.now().strftime("%d %B %Y")
    return f"Today's date is {current_date}"

def search_wikipedia(query):
    """Search Wikipedia for information"""
    try:
        result = wikipedia.summary(query, sentences=2)
        return result
    except:
        return "Sorry, I couldn't find information about that."

def open_website(query):
    """Open websites"""
    websites = {
        'google': 'https://www.google.com',
        'youtube': 'https://www.youtube.com',
        'github': 'https://www.github.com'
    }
    
    for site in websites:
        if site in query:
            webbrowser.open(websites[site])
            return f"Opening {site}"
    
    return "Sorry, I don't know how to open that website"

def tell_joke():
    """Tell a fun joke"""
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why did the computer go to the doctor? Because it had a virus!",
        "What do you call a fake noodle? An impasta!",
        "Why don't scientists trust atoms? Because they make up everything!"
    ]
    return random.choice(jokes)

def get_response(command):
    """Generate intelligent responses"""
    # Convert command to lowercase for easier matching
    command = command.lower()

    # Dictionary of responses and actions
    responses = {
        'hello': "Hi there! I'm Jarvis, your AI assistant.",
        'how are you': "I'm great! Ready to help you with anything.",
        'your name': "I'm Jarvis, created to make your life easier!",
        'time': get_time(),
        'date': get_date(),
        'joke': tell_joke()
    }

    # Check for exact matches first
    for key in responses:
        if key in command:
            return responses[key]
    
    # Check for specific actions
    if 'open' in command and 'website' in command:
        return open_website(command)
    
    # Wikipedia search
    if 'search' in command or 'tell me about' in command:
        query = command.replace('search', '').replace('tell me about', '').strip()
        return search_wikipedia(query)
    
    # Default responses
    default_responses = [
        "Interesting! Can you tell me more?",
        "I'm listening. What else would you like to know?",
        "That sounds cool! What would you like to explore?"
    ]
    
    return random.choice(default_responses)

def main():
    # Streamlit page configuration
    st.set_page_config(page_title="Jarvis Assistant", page_icon="🤖")
    
    # Title and description
    st.title("🤖 Jarvis: Your Intelligent Assistant")
    st.write("Ask me anything! I can help with time, date, jokes, Wikipedia searches, and more.")
    
    # Create tabs for different interaction modes
    tab1, tab2 = st.tabs(["Text Interaction", "Voice Interaction"])
    
    with tab1:
        st.header("Text Chat")
        # Text input
        user_input_text = st.text_input("Type your message:", key="text_input")
        
        if user_input_text:
            response = get_response(user_input_text)
            st.write("Jarvis:", response)
    
    with tab2:
        st.header("Voice Interaction")
        # Voice input button
        if st.button("🎙️ Start Listening"):
            user_input_voice = listen()
            
            if user_input_voice:
                st.write("You said:", user_input_voice)
                response = get_response(user_input_voice)
                st.write("Jarvis:", response)
    
    # Additional fun features
    st.sidebar.header("Quick Actions")
    if st.sidebar.button("Tell me a Joke"):
        joke = tell_joke()
        st.sidebar.write(joke)
    
    if st.sidebar.button("What's the Time?"):
        st.sidebar.write(get_time())
    
    # Audio toggle
    speak_response = st.checkbox("Read responses aloud")
    if speak_response:
        try:
            speak(response)
        except:
            st.write("Could not read response aloud")

# Run the Jarvis assistant
if __name__ == "__main__":
    main()