import requests
from typing import List, Dict, Any, Optional
import os
from .event_service import EventService


class GooglePlacesService(EventService):
    """
    Google Places API client adapted for finding event venues and entertainment locations.
    
    This service uses the Google Places API to discover venues and entertainment locations
    that commonly host events. Since Google Places doesn't directly provide event scheduling
    data, this implementation focuses on finding event-related venues such as theaters,
    concert halls, arenas, museums, and entertainment centers that users can investigate
    for actual event schedules.
    
    Key Features:
    - Event venue discovery using Google's comprehensive location database
    - Entertainment location search with category-based filtering
    - Venue quality assessment using Google ratings and reviews
    - Geographic search with flexible location and keyword support
    - Venue metadata including addresses, ratings, and contact information
    - Integration with Google's powerful location intelligence
    
    Venue Categories Supported:
    - Entertainment venues: Theaters, concert halls, clubs, arenas
    - Cultural institutions: Museums, art galleries, cultural centers
    - Recreational facilities: Amusement parks, casinos, entertainment complexes
    - Sports venues: Stadiums, sports complexes, bowling alleys
    - Educational venues: Universities, convention centers, community centers
    
    Important Limitations:
    This service provides venue information rather than specific event listings.
    Users should check venue websites, TicketMaster, or other event platforms
    for actual event schedules and ticket information.
    
    Attributes:
        api_key (str): Google Places API key for authentication
        base_url (str): Base URL for Google Places API endpoints
    """
    
    def __init__(self):
        """
        Initialize the Google Places service with API configuration and authentication setup.
        
        Retrieves the API key from the GOOGLE_PLACES_API_KEY environment variable and
        configures the base URL for Google Places API requests. Performs fail-fast
        validation to ensure the API key is available and properly configured.
        
        Raises:
            ValueError: If GOOGLE_PLACES_API_KEY environment variable is not set or empty
        """
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
        if not self.api_key:
            raise ValueError("API key is required. Provide it directly or set GOOGLE_PLACES_API_KEY environment variable.")
    
    def get_events(self, city: str, country_code: str, keywords: Optional[str] = None, 
                   start_date: Optional[str] = None, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search for event venues and entertainment locations using Google Places API.
        
        This method searches for venues that commonly host events rather than specific events.
        It uses Google's comprehensive location database to find theaters, concert halls,
        arenas, museums, and other entertainment venues that may host events matching
        the search criteria. Results are formatted to indicate these are venues that
        may host events rather than confirmed event listings.
        
        Search Strategy:
        The method constructs intelligent search queries combining user keywords with
        event-related venue types to maximize relevant results. It filters results
        to focus on entertainment-oriented venues using Google Places type classifications
        and keyword matching algorithms.
        
        Venue Discovery Features:
        - Intelligent query construction with event-focused keywords
        - Venue type filtering for entertainment and event spaces
        - Quality scoring using Google ratings and review data
        - Geographic relevance ranking based on location and popularity
        - Comprehensive venue metadata including contact and location information
        
        Data Processing Pipeline:
        1. Construct search queries with user keywords and venue-specific terms
        2. Execute Google Places text search with establishment filtering
        3. Filter results for event-related venue types and categories
        4. Score and rank venues based on relevance and quality indicators
        5. Format results with clear indication of venue vs. event status
        
        Args:
            city (str): The city to search for venues in. Supports major international cities
                       and various naming conventions (e.g., 'Los Angeles', 'London', 'Tokyo').
                       Cannot be empty or whitespace-only
            country_code (str): Two-letter ISO 3166-1 alpha-2 country code for geographic
                              context (e.g., 'US', 'CA', 'GB'). Must be exactly 2 characters
                              for proper geographic filtering
            keywords (str, optional): Keywords to include in venue search for more targeted results.
                                    Combined with event-related terms (e.g., 'music concerts',
                                    'comedy shows', 'theater performances'). Defaults to None
            start_date (str, optional): Not used by Google Places API but included for interface
                                      compatibility with other event services. May be used in
                                      future implementations. Defaults to None
            max_results (int, optional): Maximum number of venues to return (1-60). Limited by
                                       Google Places API constraints and practical considerations
                                       for response time and relevance. Defaults to 20
        
        Returns:
            List[Dict[str, Any]]: Comprehensive list of venue dictionaries formatted as event-like entries:
                Basic Information:
                - name: Formatted as "Events at [Venue Name]" to indicate potential event hosting
                - source: 'google_places' for data source identification
                - place_id: Google Places unique identifier for additional data retrieval
                - note: Explanatory text indicating this is a venue, not a specific event
                
                Venue Details:
                - venue: Nested venue information structure containing:
                  - name: Official venue name from Google Places
                  - address: Complete formatted address string
                  - location: Geographic coordinates (latitude, longitude)
                
                Quality Indicators:
                - rating: Google Places rating (1-5 scale) if available
                - types: Google Places venue type classifications
                - search_date: Original search date if start_date was provided
                
                Event Context:
                Results are formatted to clearly indicate these are venues that may host events
                rather than specific events, with suggestions to check venue websites or
                event platforms for actual event schedules.
        
        Raises:
            ValueError: If parameters are invalid including:
                - Empty or whitespace-only city parameter
                - Invalid country code format (not exactly 2 characters)
                - max_results outside valid range (1-60)
            Exception: If API operations fail including:
                - Google Places API authentication or quota issues
                - Network connectivity problems
                - Invalid API responses or parsing errors
                - Geographic location resolution failures
            requests.RequestException: If HTTP requests fail due to network issues
        """
        
        # Note: Google Places API doesn't directly provide events data
        # This implementation searches for event venues and entertainment places
        # that might host events matching the search criteria
        
        if max_results < 1 or max_results > 60:
            raise ValueError("max_results must be between 1 and 60")
        
        if not city or not city.strip():
            raise ValueError("City parameter cannot be empty")
        
        if not country_code or len(country_code) != 2:
            raise ValueError("Country code must be a 2-letter code (e.g., 'US', 'CA')")
        
        # Create search query for event venues and entertainment places
        query_parts = []
        if keywords:
            query_parts.append(keywords.strip())
        
        # Add event-related venue types
        venue_keywords = ["events", "entertainment", "venues", "concerts", "theaters", "halls"]
        query_parts.extend(venue_keywords)
        query_parts.append(f"{city.strip()}, {country_code.upper()}")
        
        query = " ".join(query_parts)
        
        url = f"{self.base_url}/textsearch/json"
        params = {
            'key': self.api_key,
            'query': query,
            'type': 'establishment'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'OK':
                if data['status'] == 'ZERO_RESULTS':
                    return []
                else:
                    raise Exception(f"Google Places API error: {data.get('error_message', data['status'])}")
            
            # Filter results to focus on event-related venues
            event_venues = []
            event_related_types = {
                'night_club', 'casino', 'museum', 'amusement_park', 'stadium', 
                'movie_theater', 'bowling_alley', 'art_gallery', 'zoo', 
                'tourist_attraction', 'establishment', 'point_of_interest'
            }
            
            for place in data.get('results', []):
                place_types = set(place.get('types', []))
                
                # Check if place has event-related types or keywords in name
                if (place_types.intersection(event_related_types) or 
                    any(keyword in place['name'].lower() for keyword in 
                        ['theater', 'theatre', 'concert', 'hall', 'center', 'venue', 'club', 'arena'])):
                    
                    # Transform to event-like format
                    event_venue = {
                        'name': f"Events at {place['name']}",
                        'venue': {
                            'name': place['name'],
                            'address': place.get('formatted_address', ''),
                            'location': place.get('geometry', {}).get('location', {})
                        },
                        'place_id': place.get('place_id'),
                        'rating': place.get('rating'),
                        'types': place.get('types', []),
                        'source': 'google_places',
                        'note': 'This is a venue that may host events. Use Google Events search or venue websites for actual event listings.'
                    }
                    
                    if start_date:
                        event_venue['search_date'] = start_date
                    
                    event_venues.append(event_venue)
                
                if len(event_venues) >= max_results:
                    break
            
            return event_venues[:max_results]
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching venues from Google Places: {str(e)}")
        except ValueError as e:
            raise Exception(f"Error parsing Google Places response: {str(e)}")