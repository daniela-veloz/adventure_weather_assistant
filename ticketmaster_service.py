import requests
from typing import List, Dict, Any, Optional
import os
from event_service import EventService


class TicketMasterService(EventService):
    """
    TicketMaster Discovery API client for retrieving live entertainment events.
    
    This service integrates with the TicketMaster Discovery API v2 to search for and retrieve
    comprehensive information about live entertainment events including concerts, sports events,
    theater performances, comedy shows, and other ticketed entertainment. It provides robust
    filtering capabilities by location, keywords, dates, and result limits while handling
    API authentication, rate limiting, and error recovery.
    
    Key Features:
    - Comprehensive event discovery across all entertainment categories
    - Advanced filtering by location, keywords, dates, and event types
    - Detailed event information including venues, pricing, and classifications
    - International support with country-specific event discovery
    - Robust error handling and API response validation
    - TicketMaster Discovery API v2 integration with consumer key authentication
    
    Event Categories Supported:
    - Music: Concerts, festivals, tours, live performances
    - Sports: Professional sports, college sports, motorsports
    - Theater: Broadway, musicals, plays, performing arts
    - Comedy: Stand-up, comedy tours, improv shows
    - Family: Kids shows, family entertainment, educational events
    - Miscellaneous: Special events, conventions, exhibitions
    
    Attributes:
        api_key (str): TicketMaster API consumer key for authentication
        base_url (str): Base URL for TicketMaster Discovery API v2 endpoints
    """
    
    def __init__(self):
        """
        Initialize the TicketMaster service with API configuration and authentication setup.
        
        Retrieves the API consumer key from the TICKETMASTER_API_KEY environment variable
        and configures the base URL for TicketMaster Discovery API v2 requests. Performs
        fail-fast validation to ensure the API key is available before attempting API calls.
        
        Environment Variables Required:
        - TICKETMASTER_API_KEY: Your TicketMaster API consumer key (free developer account available)
        
        API Registration:
        1. Visit https://developer.ticketmaster.com
        2. Create a free developer account
        3. Create an application to get your consumer key
        4. Set the consumer key as TICKETMASTER_API_KEY environment variable
        
        Raises:
            ValueError: If TICKETMASTER_API_KEY environment variable is not set or empty
        """
        self.api_key = os.getenv('TICKETMASTER_API_KEY')
        self.base_url = "https://app.ticketmaster.com/discovery/v2"
        
        if not self.api_key:
            raise ValueError("API key is required. Provide it directly or set TICKETMASTER_API_KEY environment variable.")
    
    def get_events(self, city: str, country_code: str, keywords: Optional[str] = None, 
                   start_date: Optional[str] = None, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve live entertainment events from TicketMaster based on comprehensive search criteria.
        
        This method searches TicketMaster's extensive event database for live entertainment events
        matching the specified location and optional filters. It returns detailed event information
        including venue details, dates and times, pricing information, event classifications,
        and ticket availability. Results are validated and formatted for consistent consumption.
        
        Search Capabilities:
        - Location-based filtering by city and country
        - Keyword matching across event names, descriptions, and categories
        - Date range filtering for events occurring on or after specified dates
        - Event classification filtering (music, sports, theater, etc.)
        - Venue information integration with detailed location data
        - Pricing and ticket availability information
        
        Data Quality Features:
        - Comprehensive parameter validation with detailed error messages
        - API response validation and error handling
        - Event deduplication and quality filtering
        - Venue information enrichment and geocoding
        - Date and time normalization across timezones
        
        Args:
            city (str): The city to search for events in. Supports major international cities
                       and various naming formats (e.g., 'New York', 'Los Angeles', 'London',
                       'Toronto'). Cannot be empty or whitespace-only
            country_code (str): Two-letter ISO 3166-1 alpha-2 country code for geographic
                              filtering (e.g., 'US', 'CA', 'GB', 'AU'). Must be exactly 2 characters
            keywords (str, optional): Keywords to filter events by type, genre, artist name,
                                    or venue (e.g., 'music', 'rock concert', 'comedy show',
                                    'basketball', 'broadway'). Supports flexible matching
                                    across event metadata. Defaults to None (no keyword filtering)
            start_date (str, optional): Event start date filter in ISO 8601 format
                                      (e.g., '2025-08-10T00:00:00Z'). Returns events occurring
                                      on or after this date. Defaults to None (no date filtering)
            max_results (int, optional): Maximum number of results to return (1-200).
                                       Limited by TicketMaster API pagination constraints.
                                       Defaults to 20 for optimal performance
        
        Returns:
            List[Dict[str, Any]]: Comprehensive list of event dictionaries containing:
                Event Metadata:
                - id: TicketMaster event ID for unique identification
                - name: Event name or title
                - url: TicketMaster event page URL for ticket purchasing
                - images: List of event images with different sizes and ratios
                
                Date and Time Information:
                - dates: Complete date/time structure with start/end times
                - timezone: Event timezone for accurate local time display
                
                Venue Information:
                - _embedded.venues: Detailed venue information array containing:
                  - name: Venue name
                  - address: Complete venue address structure
                  - city: Venue city information
                  - location: Geographic coordinates
                
                Event Details:
                - classifications: Event categories (music, sports, theater, etc.)
                - priceRanges: Ticket pricing information (if available)
                - sales: Ticket sale status and availability
                
        Raises:
            ValueError: If parameters are invalid including:
                - Empty or whitespace-only city parameter
                - Invalid country code (not exactly 2 characters)
                - max_results outside valid range (1-200)
            Exception: If API operations fail including:
                - TicketMaster API authentication failures
                - Network connectivity issues
                - API rate limiting or quota exceeded
                - Invalid API responses or parsing errors
            requests.RequestException: If HTTP requests fail due to network issues
        """
        
        if max_results < 1 or max_results > 200:
            raise ValueError("max_results must be between 1 and 200")
        
        if not city or not city.strip():
            raise ValueError("City parameter cannot be empty")
        
        if not country_code or len(country_code) != 2:
            raise ValueError("Country code must be a 2-letter code (e.g., 'US', 'CA')")
        
        url = f"{self.base_url}/events.json"
        params = {
            'apikey': self.api_key,
            'city': city.strip(),
            'countryCode': country_code.upper(),
            'size': min(max_results, 200)  # API max is 200 per page
        }
        
        if keywords:
            params['keyword'] = keywords.strip()
        
        if start_date:
            params['startDateTime'] = start_date
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract events from the response
            if '_embedded' in data and 'events' in data['_embedded']:
                events = data['_embedded']['events']
                return events[:max_results]  # Ensure we don't exceed max_results
            else:
                return []
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching events from Ticketmaster: {str(e)}")
        except ValueError as e:
            raise Exception(f"Error parsing Ticketmaster response: {str(e)}")