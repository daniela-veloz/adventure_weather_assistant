import requests
from typing import Dict, Any, Optional
import os


class WeatherService:
    """
    WeatherAPI client with multi-day forecast support and static method descriptors for LLM function calling.
    
    This service provides comprehensive weather forecast data for specified cities using the WeatherAPI service.
    It supports multi-day forecasts up to 7 days ahead, handles API authentication, request formatting,
    error handling, and response parsing. The class includes static service descriptions for OpenAI
    function calling integration.
    
    Key Features:
    - Multi-day weather forecasts (1-7 days)
    - Current weather conditions with detailed metrics
    - Static method descriptors for LLM function calling
    - Comprehensive error handling and validation
    - Environment variable-based API key management
    - WeatherAPI.com integration with free tier support
    
    Attributes:
        api_key (str): WeatherAPI key for authentication retrieved from environment
        base_url (str): Base URL for WeatherAPI endpoints
        SERVICE_DESCRIPTION (Dict): Static OpenAI function calling descriptor
    """

    SERVICE_DESCRIPTION = {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather and forecast data for a specified city. Supports multi-day forecasts up to 7 days ahead with detailed conditions, temperature, and weather metrics.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city to get weather for (e.g., 'London', 'New York', 'Tokyo'). Supports international cities worldwide."
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of forecast days to retrieve (1-7). Includes current day plus future days.",
                            "minimum": 1,
                            "maximum": 7,
                            "default": 1
                        }
                    },
                    "required": ["city"],
                    "additionalProperties": False
                }
            }
        }

    def __init__(self):
        """
        Initialize the weather service with API configuration and environment setup.
        
        Retrieves the API key from the WEATHER_API_KEY environment variable and configures
        the base URL for WeatherAPI requests. Performs fail-fast validation to ensure
        the API key is available before attempting to use the service.
        
        Environment Variables Required:
        - WEATHER_API_KEY: Your WeatherAPI.com API key (free tier available)
        
        Raises:
            ValueError: If WEATHER_API_KEY environment variable is not set or empty
        """
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = "http://api.weatherapi.com/v1"
        
        if not self.api_key:
            raise ValueError("API key is required. Provide it directly or set WEATHER_API_KEY environment variable.")
    
    def fetch_weather(self, city: str, days: int = 1) -> Dict[str, Any]:
        """
        Fetch comprehensive weather forecast data for a specified city and duration.
        
        This method retrieves current weather conditions and multi-day forecast data from WeatherAPI,
        including temperature, weather conditions, humidity, wind speed, and daily forecasts.
        The response includes both current conditions and future forecast data formatted
        for easy consumption by AI systems and applications.
        
        Features:
        - Current weather conditions with detailed metrics
        - Multi-day forecasts with daily summaries
        - Location information and timezone data
        - Comprehensive weather metrics (temperature, humidity, wind, etc.)
        - Error handling for invalid locations and API issues
        
        Args:
            city (str): The name of the city to get weather for. Supports international cities
                       and various formats (e.g., 'New York', 'London, UK', 'Tokyo, Japan')
            days (int, optional): Number of forecast days (1-7) including current day. Defaults to 1
        
        Returns:
            Dict[str, Any]: Comprehensive weather data containing:
                - location: City location information (name, country, timezone, etc.)
                - current: Current weather conditions (temperature, conditions, wind, etc.)
                - forecast: Multi-day forecast data with daily summaries
                    - forecastday: List of daily forecasts
                    - day: Daily summary (max/min temp, conditions, precipitation)
                    - astro: Sunrise/sunset times and moon phases
                    - hour: Hourly forecast data (if needed)
        
        Raises:
            ValueError: If days is not between 1-7, city is empty, or API parameters are invalid
            Exception: If the API request fails, returns errors, or encounters connectivity issues
            requests.RequestException: If there are network connectivity issues with WeatherAPI
        """
        if days < 1 or days > 7:
            raise ValueError("Days must be between 1 and 7")
        
        if not city or not city.strip():
            raise ValueError("City parameter cannot be empty")
        
        url = f"{self.base_url}/forecast.json"
        params = {
            'key': self.api_key,
            'q': city.strip(),
            'days': days
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching weather data: {str(e)}")
        except ValueError as e:
            raise Exception(f"Error parsing weather data: {str(e)}")

    @staticmethod
    def get_description() -> Dict[str, Any]:
        """
        Get the static service description for OpenAI function calling integration.
        
        This static method returns the SERVICE_DESCRIPTION constant that defines
        the function calling interface for LLM integration. It provides the schema
        and metadata needed for AI systems to understand how to use this weather service.
        
        Returns:
            Dict[str, Any]: OpenAI function calling descriptor containing:
                - type: "function" (required by OpenAI)
                - function: Function metadata and parameter schema
                    - name: Function name for LLM calling
                    - description: Human-readable description of capabilities
                    - parameters: JSON schema for function parameters
        """
        return WeatherService.SERVICE_DESCRIPTION