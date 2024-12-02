import streamlit as st
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv
import os
import speech_recognition as sr

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(page_title="Jarvis AI Assistant", page_icon="🤖")

# Initialize speech recognition
recognizer = sr.Recognizer()

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

# Web-based Voice Interaction Component
def voice_interaction_component():
    st.write("### 🎤 Voice Interaction")
    st.markdown("""
    <script>
    const startRecording = () => {
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'en-US';
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            window.parent.postMessage({type: 'voiceInput', text: transcript}, '*');
        };
        recognition.start();
    }
    </script>
    <button onclick="startRecording()">Start Voice Input</button>
    """, unsafe_allow_html=True)

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

    # Voice Interaction Component
    voice_interaction_component()

    # Add JavaScript to handle voice input
    st.components.v1.html("""
    <script>
    window.addEventListener('message', (event) => {
        if (event.data.type === 'voiceInput') {
            // Send voice input to Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue', 
                key: 'voiceInput', 
                value: event.data.text
            }, '*');
        }
    });
    </script>
    """, height=0)

    # Capture voice input
    voice_input = st.session_state.get('voiceInput', None)
    if voice_input:
        st.write(f"🎤 Voice Input: {voice_input}")
        # Process voice input
        if openai_model:
            try:
                response = openai_model.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant named Jarvis."},
                        {"role": "user", "content": voice_input}
                    ]
                ).choices[0].message.content
                st.write("🤖 OpenAI Response:", response)
            except Exception as e:
                st.error(f"OpenAI error: {e}")
                
                # Fallback to Gemini if OpenAI fails
                if gemini_model:
                    try:
                        response = gemini_model.generate_content(voice_input).text
                        st.write("🤖 Gemini Response:", response)
                    except Exception as e:
                        st.error(f"Gemini error: {e}")
                        st.warning("No alternative AI model available.")

    # Text input processing
    user_input = st.chat_input("What can I help you with?")
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