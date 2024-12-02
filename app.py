import streamlit as st
import google.generativeai as genai
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(page_title="Jarvis AI Assistant", page_icon="🤖")

# Title and description
st.title("🤖 Jarvis AI Assistant")
st.write("Your intelligent AI companion powered by Google Gemini and OpenAI")

# Sidebar for configuration
st.sidebar.header("AI Assistant Configuration")

# Function to initialize Google Gemini
def init_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-pro')
    except Exception as e:
        st.sidebar.error(f"Gemini initialization error: {e}")
        return None

# Function to initialize OpenAI
def init_openai(api_key):
    try:
        openai.api_key = api_key
        return openai
    except Exception as e:
        st.sidebar.error(f"OpenAI initialization error: {e}")
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

# Main application logic
def main():
    # API Key inputs
    st.sidebar.subheader("API Keys")
    gemini_api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
    openai_api_key = st.sidebar.text_input("OpenAI API Key (Optional)", type="password")

    # Initialize models based on provided keys
    gemini_model = init_gemini(gemini_api_key) if gemini_api_key else None
    openai_model = init_openai(openai_api_key) if openai_api_key else None

    # Predefined commands dictionary
    commands = {
        "time": handle_time,
        "date": handle_date,
        "system": handle_system_info,
        "weather": handle_weather
    }

    # Chat input
    user_input = st.chat_input("What can I help you with?")

    if user_input:
        # Check for predefined commands
        if user_input.lower() in commands:
            response = commands[user_input.lower()]()
            st.write(response)
        else:
            # Try Gemini first
            if gemini_model:
                try:
                    response = gemini_model.generate_content(user_input).text
                    st.write("🤖 Gemini Response:", response)
                except Exception as e:
                    st.error(f"Gemini error: {e}")
                    
                    # Fallback to OpenAI if Gemini fails
                    if openai_model:
                        try:
                            response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "You are a helpful AI assistant named Jarvis."},
                                    {"role": "user", "content": user_input}
                                ]
                            ).choices[0].message.content
                            st.write("🤖 OpenAI Response:", response)
                        except Exception as e:
                            st.error(f"OpenAI error: {e}")
                    else:
                        st.warning("No alternative AI model available.")
            
            # If Gemini is not available, use OpenAI
            elif openai_model:
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful AI assistant named Jarvis."},
                            {"role": "user", "content": user_input}
                        ]
                    ).choices[0].message.content
                    st.write("🤖 OpenAI Response:", response)
                except Exception as e:
                    st.error(f"OpenAI error: {e}")
            
            else:
                st.warning("Please provide an API key for Google Gemini or OpenAI")

if __name__ == "__main__":
    main()