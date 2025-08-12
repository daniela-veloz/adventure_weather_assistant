"""
Adventure Weather Assistant - Main Application Entry Point

This module serves as the main entry point for the Adventure Weather Assistant application.
It handles environment variable loading, API key validation, agent initialization, and
launches the Gradio web interface for user interactions.

The application combines real-time weather data with local event information to provide
intelligent, weather-aware activity recommendations through a conversational AI interface.

Required Environment Variables:
- OPENAI_API_KEY: OpenAI API key for LLM functionality
- WEATHER_API_KEY: WeatherAPI.com API key for weather data
- TICKETMASTER_API_KEY: TicketMaster API consumer key for event data
- GOOGLE_PLACES_API_KEY: Google Places API key for venue information

Usage:
    python app.py

This will launch a Gradio web interface accessible via browser for chatting with the
Adventure Weather Agent.
"""

from dotenv import load_dotenv
import os
import gradio as gr
from activity_adventure_agent import ActivityAdventureAgent


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
        else:
            print(f"✅ {service} key loaded successfully!")
    
    # If any keys are missing, provide helpful error message
    if missing_keys:
        print("\n❌ Missing required API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease ensure all required API keys are set in your .env file.")
        print("See the project documentation for API key setup instructions.")
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    print("\n✅ All API keys loaded successfully!")
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
    try:
        print("🚀 Initializing Adventure Weather Agent...")
        agent = ActivityAdventureAgent()
        print("✅ Agent initialized successfully!")
        return agent
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        print("Please check your API keys and try again.")
        raise


def launch_gradio_interface(agent):
    """
    Launch the Gradio chat interface for the Adventure Weather Agent.
    
    This function creates and launches a Gradio ChatInterface that provides
    a web-based conversational interface for users to interact with the
    Adventure Weather Agent. The interface supports message history and
    real-time responses.
    
    Args:
        agent (ActivityAdventureAgent): Initialized agent instance to handle chat interactions
        
    Returns:
        None: Function launches the web interface and runs indefinitely
    """
    print("🌐 Launching Gradio chat interface...")
    print("💬 Open your browser to start chatting with the Adventure Weather Agent!")
    
    # Create and launch the chat interface
    interface = gr.ChatInterface(
        fn=agent.chat, 
        type="messages",
        title="🌤️ Adventure Weather Assistant",
        description="Get personalized activity recommendations based on real-time weather and local events!"
    )
    
    interface.launch()


def main():
    """
    Main application entry point with comprehensive error handling and initialization.
    
    This function orchestrates the complete application startup process including:
    1. Environment variable loading and validation
    2. Agent initialization with all required services
    3. Gradio web interface launch
    4. Comprehensive error handling with user-friendly messages
    
    The function ensures graceful error handling at each step and provides
    clear feedback to users about the application status and any issues encountered.
    """
    try:
        print("🌤️ Starting Adventure Weather Assistant...")
        print("=" * 50)
        
        # Step 1: Load and validate environment variables
        load_and_validate_environment()
        
        # Step 2: Initialize the agent
        agent = create_agent()
        
        # Step 3: Launch the web interface
        print("\n" + "=" * 50)
        launch_gradio_interface(agent)
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("\nApplication cannot start without proper API key configuration.")
        print("Please fix the configuration and try again.")
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        print("\nThe application encountered an unexpected error during startup.")
        print("Please check your configuration and try again.")
        
    except KeyboardInterrupt:
        print("\n\n👋 Adventure Weather Assistant shutting down...")
        print("Thanks for using the Adventure Weather Assistant!")


if __name__ == "__main__":
    main()