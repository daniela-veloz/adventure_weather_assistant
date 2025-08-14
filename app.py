"""
Adventure Weather Assistant - Streamlit Application

This module serves as the main entry point for the Adventure Weather Assistant application.
It handles environment variable loading, API key validation, agent initialization, and
launches the Streamlit web interface for user interactions.

The application combines real-time weather data with local event information to provide
intelligent, weather-aware activity recommendations through a conversational AI interface.

Required Environment Variables:
- OPENAI_API_KEY: OpenAI API key for LLM functionality
- WEATHER_API_KEY: WeatherAPI.com API key for weather data
- TICKETMASTER_API_KEY: TicketMaster API consumer key for event data
- GOOGLE_PLACES_API_KEY: Google Places API key for venue information

Usage:
    streamlit run app.py

This will launch a Streamlit web interface accessible via browser for chatting with the
Adventure Weather Agent.
"""

import streamlit as st
from dotenv import load_dotenv
import os
from backend.activity_adventure_agent import ActivityAdventureAgent
from backend.rate_limiter import RateLimiter, RateLimitType
from backend.ip_extractor import IPExtractor


def load_and_validate_environment():
    """
    Load environment variables and validate that all required API keys are present.
    
    This function loads environment variables from a .env file and performs comprehensive
    validation to ensure all required API keys are available before attempting to
    initialize the application. It provides clear error messages for missing keys
    and confirms successful loading.
    
    Returns:
        bool: True if all required API keys are present and valid
        
    Raises:
        ValueError: If any required API key is missing or empty
        SystemExit: If critical configuration is missing, preventing application startup
    """
    # Load environment variables from .env file
    load_dotenv(override=True)
    
    # Required API keys for the application
    required_keys = {
        'OPENAI_API_KEY': 'OpenAI API',
        'WEATHER_API_KEY': 'Weather API', 
        'TICKETMASTER_API_KEY': 'TicketMaster API',
        'GOOGLE_PLACES_API_KEY': 'Google Places API'
    }
    
    # Check each required API key
    missing_keys = []
    for key, service in required_keys.items():
        value = os.getenv(key)
        if not value or not value.strip():
            missing_keys.append(f"{key} ({service})")
    
    # If any keys are missing, provide helpful error message
    if missing_keys:
        error_msg = f"Missing required API keys: {', '.join(missing_keys)}"
        raise ValueError(error_msg)
    
    return True


def create_agent():
    """
    Create and initialize the ActivityAdventureAgent with error handling.
    
    This function attempts to create an instance of the ActivityAdventureAgent,
    which will initialize all required services (LLM client, weather service,
    event aggregation service) and set up the function registry for AI interactions.
    
    Returns:
        ActivityAdventureAgent: Initialized agent ready for conversations
        
    Raises:
        Exception: If agent initialization fails due to API key issues or service problems
    """
    return ActivityAdventureAgent()


def main():
    """
    Main Streamlit application function.
    
    This function creates the Streamlit interface with chat functionality,
    handles agent initialization, and manages the conversation flow with rate limiting.
    """
    # Configure Streamlit page
    st.set_page_config(
        page_title="Adventure Weather Assistant",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # App header
    st.title("🌤️ Adventure Weather Assistant")
    st.markdown("Get personalized activity recommendations based on real-time weather and local events!")
    
    # Add a divider
    st.divider()
    
    # Initialize rate limiter
    if "rate_limiter" not in st.session_state:
        st.session_state.rate_limiter = RateLimiter()
    
    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize agent in session state
    if "agent" not in st.session_state:
        try:
            with st.spinner("🚀 Initializing Adventure Weather Agent..."):
                load_and_validate_environment()
                st.session_state.agent = create_agent()
        except ValueError as e:
            st.error(f"❌ Configuration Error: {str(e)}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Failed to initialize agent: {str(e)}")
            st.stop()
    
    # Check rate limits and display status
    rate_limit_result = st.session_state.rate_limiter.check_rate_limit()
    
    # Display rate limit status in sidebar
    with st.sidebar:
        st.header("📊 Usage Stats")
        if rate_limit_result.stats:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Hourly Usage", 
                    f"{rate_limit_result.stats['hourly_used']}/{rate_limit_result.stats['hourly_limit']}"
                )
            with col2:
                st.metric(
                    "Daily Usage", 
                    f"{rate_limit_result.stats['daily_used']}/{rate_limit_result.stats['daily_limit']}"
                )
    
    # Chat interface
    st.markdown("### Chat with the Agent")
    
    # Display rate limit warning if applicable
    if not rate_limit_result.valid:
        if rate_limit_result.limit_type == RateLimitType.HOURLY_LIMIT:
            st.error(f"🚫 Hourly limit reached. Try again in {rate_limit_result.next_reset} minutes.")
        elif rate_limit_result.limit_type == RateLimitType.DAILY_LIMIT:
            st.error(f"🚫 Daily limit reached. Try again in {rate_limit_result.next_reset} hours.")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input - disable if rate limited
    chat_disabled = not rate_limit_result.valid
    placeholder_text = "Ask me about activities in your city... (e.g., 'What should I do in Seattle today?')"
    if chat_disabled:
        placeholder_text = "Rate limit reached - please wait before sending another message"
    
    if prompt := st.chat_input(placeholder_text, disabled=chat_disabled):
        # Double-check rate limit before processing
        rate_check = st.session_state.rate_limiter.check_rate_limit()
        if not rate_check.valid:
            st.error("⚠️ Rate limit exceeded. Please wait before sending another message.")
            st.rerun()
            return
        
        # Record the request
        ip_address = IPExtractor.get_client_ip()
        st.session_state.rate_limiter.record_request(ip_address)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking and checking weather & events, this might take some seconds, please wait..."):
                try:
                    # Convert Streamlit message format to OpenAI format for conversation history
                    conversation_history = []
                    for msg in st.session_state.messages[:-1]:  # Exclude the current user message
                        conversation_history.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    
                    # Use the agent's chat method with conversation history
                    response = st.session_state.agent.chat(prompt, conversation_history)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Add more sidebar information
    with st.sidebar:
        st.header("🔧 About")
        st.markdown("""
        This Adventure Weather Assistant combines:
        - 🌤️ Real-time weather data
        - 🎭 Local events from TicketMaster
        - 📍 Venue information from Google Places
        - 🤖 AI-powered recommendations
        
        Just ask about activities in any city and get personalized suggestions!
        """)
        
        st.header("⚡ Rate Limits")
        st.markdown("""
        To ensure fair usage for everyone:
        - **Hourly**: 10 requests per hour
        - **Daily**: 25 requests per day
        """)
        
        st.header("💡 Example Questions")
        st.markdown("""
        - "What should I do in New York today?"
        - "Find outdoor activities in San Francisco"
        - "What events are happening in Austin this weekend?"
        - "Give me indoor activities for a rainy day in Seattle"
        """)
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()