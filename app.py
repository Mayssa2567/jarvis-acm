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

    # Add this function to your existing code
def voice_input_component():
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
    """, unsafe_allow_html=True)

    # SVG Microphone Icon with inline JavaScript
    mic_svg = """
    <svg id="micIcon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" 
         fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
         style="cursor:pointer; transition: color 0.3s;"
         onclick="startRecording()">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
        <line x1="12" y1="19" x2="12" y2="23"></line>
        <line x1="8" y1="23" x2="16" y2="23"></line>
    </svg>
    """
    
    return mic_svg

# Main application logic
def main():

    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        user_input = st.text_input("What can I help you with?", key="user_prompt")
    
    with col2:
        # Add voice input component
        mic_svg = voice_input_component()
        st.markdown(mic_svg, unsafe_allow_html=True)
        
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

    # Initialize conversation history if not already done
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    # Voice Interaction Component
    voice_interaction_component()

    # Add JavaScript to handle voice input
    st.components.v1.html("""<script>
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
        response = process_input(voice_input, openai_model, gemini_model)
        if response:
            # Append user input and response to conversation history
            st.session_state.conversation.append({"user": voice_input, "jarvis": response})

    # Text input processing
    user_input = st.chat_input("What can I help you with?")
    if user_input:
        # Process text input using AI
        response = process_input(user_input, openai_model, gemini_model)
        if response:
            # Append user input and response to conversation history
            st.session_state.conversation.append({"user": user_input, "jarvis": response})

    # CSS for bubble background
    st.markdown("""
        <style>
            .chat-container {
                background-color: rgba(255, 255, 255, 0.15); /* Semi-transparent white */
                border-radius: 10px;
                padding: 20px;
                max-height: 500px; /* Limit height for scrolling */
                overflow-y: auto; /* Enable vertical scroll */
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }
            .user-bubble {
                background-color: rgba(240, 240, 240, 0.15); /* Light gray for user */
                border-radius: 20px 0 20px 20px;
                padding: 10px;
                margin: 5px 0;
                display: inline-block;
                max-width: 80%; /* Limit width */
                float: right; /* Align to the right */
                text-align: right; /* Align text to the right */
            }
            .jarvis-bubble {
                background-color: rgba(220, 220, 220, 0.15); /* Slightly darker gray for Jarvis */
                border-radius: 0 20px 20px 20px;
                padding: 10px;
                margin: 5px 0;
                display: inline-block;
                max-width: 80%; /* Limit width */
                float: left; /* Align to the left */
                text-align: left; /* Align text to the left */
            }
        </style>
        """, unsafe_allow_html=True)

    # Display conversation history
    st.write("### Conversation History")
    with st.container():
        chat_container = st.container()
        with chat_container:
            for chat in st.session_state.conversation:
                st.markdown(f'<div class="user-bubble"><h6><b>You:</b></h6> {chat["user"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="jarvis-bubble"><h6><b>Jarvis:</b></h6> {chat["jarvis"]}</div>', unsafe_allow_html=True)

def process_input(user_input, openai_model, gemini_model):
    if openai_model:
        try:
            response = openai_model.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant named Jarvis."},
                    {"role": "user", "content": user_input}
                ]
            ).choices[0].message.content
            return response
        except Exception as e:
            st.error(f"OpenAI error: {e}")

            # Fallback to Gemini if OpenAI fails
            if gemini_model:
                try:
                    response = gemini_model.generate_content(user_input).text
                    return response
                except Exception as e:
                    st.error(f"Gemini error: {e}")

    elif gemini_model:
        try:
            response = gemini_model.generate_content(user_input).text
            return response
        except Exception as e:
            st.error(f"Gemini error: {e}")

    return None

if __name__ == "__main__":
    main()