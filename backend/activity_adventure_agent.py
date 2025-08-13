import json
from .llm_client import LLMClient
from .weather_service import WeatherService
from .event_service_aggregator import EventServiceAggregator


class ActivityAdventureAgent:
    """
    Main conversational agent with function registry and Gradio chat interface for intelligent activity planning.
    
    This is the central orchestrator of the Adventure Weather Agent system, providing a conversational
    AI interface that combines real-time weather data with local event information to suggest
    personalized outdoor and indoor activities. The agent uses advanced function calling capabilities
    to access multiple data sources and provides intelligent, weather-aware recommendations with
    a friendly and humorous personality.

    """
    
    MODEL = "gpt-4o-mini"
    DEFAULT_NUMBER_OF_ACTIVITIES = 7
    TOOLS = [
        WeatherService.get_description(),
        EventServiceAggregator.get_description()
    ]

    SYSTEM_MESSAGE = f"""
    You are a funny and helpful activity planner, who help to find the best things to do based on the weather. Your job is to recommend up to {DEFAULT_NUMBER_OF_ACTIVITIES} activities based on real-time weather obtained from a weather tool, ensuring a mix of indoor and outdoor activities whenever possible.

    ### IMPORTANT: Always Use Your Tools First
    ALWAYS start by calling the get_weather tool to get current weather conditions when a user mentions a city, even for general questions like "what can I do in [city]" or "activities in [city]". Then use get_events tool to find local events. Only after gathering this data should you provide recommendations.

    ### Activity and Event Suggestion Process
    To provide the best activity recommendations, follow these steps in order:
    Step 1: Retrieve Weather Data – ALWAYS use the get_weather tool first when a city is mentioned. For multi-day requests, use days=7 to get a full week forecast.
    Step 2: Fetch Activities – Use the get_events tool to find relevant events in the user's area.
    Step 3: Suggest Activities – Recommend suitable indoor or outdoor activities based on the weather data you retrieved.

    ### Process Rules
    You must analyze and think carefully to determine the best combinations of activities and events for the user. Follow these rules:
    - ALWAYS call get_weather first when a city is mentioned, even for vague requests
    - For "next week" or "this weekend" requests, get weather forecast with days=7
    - Evaluate weather conditions to decide if outdoor activities are suitable
    - Check event availability and select the most relevant ones
    - Balance indoor and outdoor activities(weather allowed) to provide the best experience. If one these categories is unavailable, that's fine
    just provide the best possible suggestions.

    ### Event Formatting in Output
    Provide the events in the following format:
    **Event Name**:
    - 📅 Date: Give the date like 19th March 2025
    - 📍 Venue: Name of the venue here
    - 🔗 Ticket Link: Put the URL here
    (Separate events with a snazzy divider)

    ### User Interaction Rules
    - If the user doesn't mention a city, ask them to provide one.
    - ALWAYS use tools to get real data before making recommendations
    - Use a friendly and funny tone, be concise but don't forget to add a dash of humor!
    """

    def __init__(self):
        """
        Initialize the Activity Adventure Agent with all required services and function registry.
        
        Sets up the complete agent infrastructure including the enhanced LLM client,
        weather service, event aggregation service, and function registry that maps
        LLM function calls to actual service methods. This initialization ensures
        all components are properly configured and ready for conversational interactions.

        Raises:
            ValueError: If any required API keys are missing or services cannot be initialized
        """
        self.llm_client = LLMClient(self.MODEL)
        self.weather_api = WeatherService()
        self.activity_api = EventServiceAggregator()
        
        # Create function registry mapping function names to callable methods
        self.function_registry = {
            "get_weather": self._get_weather,
            "get_events": self._get_events
        }

    def _get_weather(self, city: str, days: int = 1) -> dict:
        """
        Wrapper method for weather API that matches the function call signature for LLM integration.
        
        This method provides a clean interface between the LLM function calling system
        and the actual WeatherService, ensuring proper parameter handling and response
        formatting for optimal AI consumption. It acts as an adapter layer that
        maintains the function calling contract while delegating to the actual service.
        
        Args:
            city (str): The city to get weather for (validated by WeatherService)
            days (int, optional): Number of forecast days (1-7). Defaults to 1
        
        Returns:
            dict: Weather forecast data from WeatherAPI formatted for LLM consumption
                 containing current conditions, forecasts, and location information
        
        Raises:
            Exception: Propagates WeatherService exceptions with context preservation
        """
        return self.weather_api.fetch_weather(city, days)

    def _get_events(self, city: str, country_code: str, keywords: str = None, 
                   start_date: str = None, max_results: int = 20) -> dict:
        """
        Wrapper method for events API that matches the function call signature for LLM integration.
        
        This method provides a clean interface between the LLM function calling system
        and the actual EventServiceAggregator, handling parameter normalization and
        response formatting for optimal AI processing. It serves as an adapter layer
        that maintains function calling contracts while leveraging the full aggregation capabilities.
        
        Args:
            city (str): The city to search for events in (validated by aggregator)
            country_code (str): Two-letter country code for geographic filtering
            keywords (str, optional): Keywords for event filtering and relevance scoring. Defaults to None
            start_date (str, optional): ISO 8601 start date filter. Defaults to None  
            max_results (int, optional): Maximum results to return. Defaults to 20
        
        Returns:
            dict: Comprehensive aggregation response containing ranked events, venues,
                 and metadata from multiple sources (TicketMaster, Google Places)
        
        Raises:
            Exception: Propagates EventServiceAggregator exceptions with context preservation
        """
        return self.activity_api.get_events(
            city=city,
            country_code=country_code,
            keywords=keywords,
            start_date=start_date,
            max_results=max_results
        )

    def chat(self, message, history):
        """
        Main chat interface method for Gradio integration with comprehensive conversation handling.
        
        This method provides the primary interface for conversational interactions with the
        Adventure Weather Agent. It leverages the enhanced LLMClient's function calling
        capabilities to automatically handle weather data retrieval, event discovery,
        and intelligent response generation while maintaining conversation context and
        providing robust error handling.
        
        Conversation Flow:
        1. Receives user message and conversation history from Gradio
        2. Uses enhanced LLMClient with automatic function calling workflow
        3. Executes weather and event API calls as needed based on user intent
        4. Generates contextual activity recommendations with weather awareness
        5. Returns formatted response with activities, events, and personality
        
        Function Calling Integration:
        The method uses the LLMClient's chat_with_function_calling method which:
        - Automatically determines when to call weather and event functions
        - Executes function calls using the function registry
        - Handles iterative function calling for complex workflows
        - Manages conversation state throughout the process
        - Provides comprehensive error recovery and fallback responses
        
        Args:
            message (str): User's input message or query for activity recommendations
            history (List): Conversation history in Gradio/OpenAI message format
                          containing previous exchanges for context maintenance
        
        Returns:
            str: Comprehensive response containing activity recommendations, event details,
                weather information, and personality-driven commentary formatted for
                easy reading and action by the user. Always returns a string response
                even in error conditions.
        """
        try:
            # Use the enhanced LLMClient method that handles function calling automatically
            response = self.llm_client.chat_with_function_calling(
                user_prompt=message,
                system_prompt=self.SYSTEM_MESSAGE,
                history=history,
                tools=self.TOOLS,
                function_registry=self.function_registry
            )
            
            # Ensure we always return a string
            return response if response is not None else "I apologize, but I couldn't generate a response. Please try again!"
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}. Please try again!"