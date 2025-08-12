import json
import concurrent.futures
from datetime import datetime
from typing import Dict, Any, List, Optional
from event_service import EventService
from ticketmaster_service import TicketMasterService
from google_places_service import GooglePlacesService


class EventServiceAggregator(EventService):
    """
    Multi-source event aggregator with parallel processing and intelligent ranking for comprehensive event discovery.
    
    This advanced aggregator orchestrates multiple event data sources (TicketMaster and Google Places)
    to provide comprehensive event and venue information through intelligent data fusion. It executes
    API calls in parallel for optimal performance, implements sophisticated scoring algorithms for
    result ranking, and provides unified response formats with detailed metadata about the
    aggregation process.
    
    Data Sources Integration:
    - TicketMaster Discovery API: Live entertainment events with comprehensive metadata
    - Google Places API: Event venues and entertainment locations with quality ratings
    - Future extensibility: Ready for additional event APIs and data sources

    """

    SERVICE_DESCRIPTION = {
            "type": "function",
            "function": {
                "name": "get_events",
                "description": "Search for events and entertainment venues in a specified city using multiple data sources. Aggregates and ranks results from TicketMaster and Google Places to provide comprehensive event listings with intelligent scoring.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city to search for events in (e.g., 'Austin', 'Los Angeles', 'Seattle', 'New York'). Supports major international cities."
                        },
                        "country_code": {
                            "type": "string",
                            "description": "Two-letter ISO 3166-1 alpha-2 country code (e.g., 'US', 'CA', 'GB', 'AU')",
                            "pattern": "^[A-Z]{2}$",
                            "minLength": 2,
                            "maxLength": 2
                        },
                        "keywords": {
                            "type": "string",
                            "description": "Optional keywords to filter events by category, genre, or type (e.g., 'music', 'comedy', 'sports', 'theater', 'concerts', 'festivals')"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Optional start date filter in ISO 8601 format (e.g., '2025-08-10T00:00:00Z') to find events occurring on or after this date",
                            "format": "date-time"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return from aggregation",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20
                        }
                    },
                    "required": ["city", "country_code"],
                    "additionalProperties": False
                }
            }
        }
    
    def __init__(self):
        """
        Initialize the event service aggregator with all required data sources and fail-fast validation.
        
        Creates instances of both TicketMaster and Google Places services, performing immediate
        initialization to ensure all required API keys are available and properly configured
        before attempting to use the aggregator. This fail-fast approach helps identify
        configuration issues early in the application lifecycle.
        
        Raises:
            ValueError: If any required API keys are missing or services cannot be initialized.
                       This includes cases where environment variables are not set or empty,
                       ensuring all dependencies are properly configured before use.
        """
        # Initialize both services - fail fast if any API keys are missing
        self.ticketmaster_service = TicketMasterService()
        self.google_places_service = GooglePlacesService()
    
    def _score_event(self, event: Dict[str, Any], keywords: Optional[str] = None) -> float:
        """
        Score events for intelligent ranking based on relevance and quality indicators.
        
        This method implements a scoring algorithm that evaluates events using
        multiple criteria including data source reliability, keyword relevance, quality metrics,
        and temporal factors. The scoring system enables intelligent result ranking to
        prioritize the most relevant and high-quality events for users.
        
        Scoring Algorithm Components:
        - Source Priority: Confirmed events (TicketMaster) score higher than venues (Google Places)
        - Keyword Relevance: Text matching across event names and venue information
        - Quality Metrics: Integration of ratings, reviews, and venue quality indicators
        - Temporal Relevance: Preference for upcoming events with confirmed dates
        - Venue Quality: Assessment of venue reputation and facilities
        
        Scoring Scale:
        - Base scores: 10.0 for confirmed events, 5.0 for venues
        - Keyword bonuses: +2.0 per matched keyword
        - Rating bonuses: Up to +2.5 for 5-star ratings
        - Date bonuses: +1.0 for events with confirmed dates
        - Venue quality bonuses: +0.5 for well-named venues
        
        Args:
            event (Dict[str, Any]): Event or venue data to score containing metadata,
                                   venue information, ratings, and other quality indicators
            keywords (str, optional): Search keywords for relevance scoring. Used to boost
                                    events that match user search intent. Defaults to None
        
        Returns:
            float: Composite relevance and quality score where higher values indicate better
                  matches. Scores typically range from 5.0 to 20.0+ depending on event quality
                  and relevance to search criteria.
        """
        score = 0.0
        
        # Base score for confirmed events vs venues
        if event.get('source') == 'ticketmaster':
            score += 10.0  # Actual events get higher base score
        elif event.get('source') == 'google_places':
            score += 5.0   # Venues get lower base score
        
        # Keyword relevance scoring
        if keywords:
            keywords_lower = keywords.lower().split()
            event_text = f"{event.get('name', '')} {event.get('venue', {}).get('name', '')}".lower()
            
            for keyword in keywords_lower:
                if keyword in event_text:
                    score += 2.0
        
        # Rating bonus (if available)
        if 'rating' in event and event['rating']:
            score += min(event['rating'] * 0.5, 2.5)  # Max 2.5 bonus for 5-star rating
        
        # Date relevance (prefer upcoming events)
        if 'dates' in event or 'start' in event:
            score += 1.0
        
        # Venue quality indicators
        venue = event.get('venue', {})
        if venue.get('name') and len(venue['name']) > 5:
            score += 0.5
        
        return score
    
    def _normalize_event_format(self, event: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Normalize events from different sources to a consistent, unified format for seamless processing.
        
        This method transforms event data from different APIs (TicketMaster, Google Places) into
        a standardized format that enables consistent processing, display, and analysis across
        different data sources. The normalization process handles schema differences, field
        mapping, and data type conversion to create a unified event representation.

        
        Args:
            event (Dict[str, Any]): Raw event data from the source API containing
                                   source-specific fields, structures, and formats
            source (str): Source identifier ('ticketmaster' or 'google_places') used
                         to determine appropriate normalization strategy and field mapping
        
        Returns:
            Dict[str, Any]: Normalized event data with consistent structure containing:
                Common Fields:
                - id: Unique event identifier from source system
                - name: Event or venue name
                - source: Data source identifier for tracking
                - type: Event type ('event' for confirmed events, 'venue' for locations)
                
                TicketMaster Events:
                - url: Direct link to TicketMaster event page
                - dates: Comprehensive date/time information with timezone
                - venue: Standardized venue information structure
                - images: Event images and promotional materials
                - priceRanges: Ticket pricing information
                - classifications: Event categories and genres
                
                Google Places Venues:
                - venue: Venue details with address and location
                - rating: Google Places rating (1-5 scale)
                - types: Google Places venue type classifications
                - note: Explanatory text about venue vs. event distinction
        """
        if source == 'ticketmaster':
            normalized = {
                'id': event.get('id'),
                'name': event.get('name', 'Unknown Event'),
                'source': 'ticketmaster',
                'type': 'event',
                'url': event.get('url'),
                'dates': {
                    'start': event.get('dates', {}).get('start', {}),
                    'timezone': event.get('dates', {}).get('timezone')
                },
                'venue': {},
                'images': event.get('images', []),
                'priceRanges': event.get('priceRanges', []),
                'classifications': event.get('classifications', [])
            }
            
            # Extract venue info
            if '_embedded' in event and 'venues' in event['_embedded']:
                venue = event['_embedded']['venues'][0]
                normalized['venue'] = {
                    'name': venue.get('name'),
                    'address': venue.get('address', {}),
                    'city': venue.get('city', {}),
                    'location': venue.get('location', {})
                }
                
        elif source == 'google_places':
            normalized = {
                'id': event.get('place_id'),
                'name': event.get('name', 'Unknown Venue'),
                'source': 'google_places', 
                'type': 'venue',
                'venue': event.get('venue', {}),
                'rating': event.get('rating'),
                'types': event.get('types', []),
                'note': event.get('note'),
                'search_date': event.get('search_date')
            }
        
        return normalized
    
    def get_events(self, city: str, country_code: str, keywords: Optional[str] = None,
                   start_date: Optional[str] = None, max_results: int = 20) -> Dict[str, Any]:
        """
        Aggregate events from multiple sources with parallel processing, intelligent ranking, and comprehensive metadata.
        
        This method orchestrates the complete event aggregation workflow, providing a comprehensive
        solution for multi-source event discovery. It manages parallel API execution, data
        normalization, intelligent scoring, and result compilation while maintaining detailed
        metadata about the aggregation process for analytics and debugging.

        
        Args:
            city (str): The city to search for events in. Must support international cities
                       with various naming conventions (e.g., 'New York', 'Los Angeles', 'London').
                       Cannot be empty or whitespace-only
            country_code (str): Two-letter ISO 3166-1 alpha-2 country code for geographic
                              filtering (e.g., 'US', 'CA', 'GB', 'AU'). Must be exactly 2 characters
            keywords (str, optional): Keywords to filter events by type, genre, category, or artist
                                    (e.g., 'music concerts', 'comedy shows', 'sports events').
                                    Used for both source filtering and result ranking. Defaults to None
            start_date (str, optional): ISO 8601 format start date filter (e.g., '2025-08-10T00:00:00Z')
                                      to find events occurring on or after this date. Defaults to None
            max_results (int, optional): Maximum number of results to return from aggregation (1-100).
                                       Results are intelligently ranked and limited. Defaults to 20
        
        Returns:
            Dict[str, Any]: Comprehensive aggregation response containing:
                Query Information:
                - query: Original search parameters for reference and caching
                
                Metadata:
                - metadata: Detailed aggregation statistics including:
                  - total_results: Number of results returned
                  - sources_used: List of data sources that contributed results
                  - timestamp: ISO 8601 timestamp of aggregation completion
                  - errors: List of any errors encountered during processing
                
                Results:
                - events: Ranked list of normalized events and venues containing:
                  - Intelligent ranking based on relevance and quality scores
                  - Normalized data format for consistent processing
                  - Source attribution for transparency and debugging
                  - Complete event/venue information from original sources
        
        Raises:
            ValueError: If parameters are invalid including:
                - Empty or whitespace-only city parameter
                - Invalid country code format (not exactly 2 characters)  
                - max_results outside valid range (1-100)
            Exception: If critical errors occur during aggregation that prevent
                      partial results from being returned
        """
        
        if max_results < 1 or max_results > 100:
            raise ValueError("max_results must be between 1 and 100")
            
        if not city or not city.strip():
            raise ValueError("City parameter cannot be empty")
            
        if not country_code or len(country_code) != 2:
            raise ValueError("Country code must be a 2-letter code (e.g., 'US', 'CA')")
        
        all_results = []
        errors = []
        
        # Prepare service calls
        def call_ticketmaster():
            try:
                results = self.ticketmaster_service.get_events(
                    city=city,
                    country_code=country_code, 
                    keywords=keywords,
                    start_date=start_date,
                    max_results=min(max_results, 20)
                )
                return [self._normalize_event_format(event, 'ticketmaster') for event in results]
            except Exception as e:
                errors.append(f"TicketMaster error: {str(e)}")
                return []
        
        def call_google_places():
            try:
                results = self.google_places_service.get_events(
                    city=city,
                    country_code=country_code,
                    keywords=keywords,
                    start_date=start_date, 
                    max_results=min(max_results, 15)
                )
                return [self._normalize_event_format(event, 'google_places') for event in results]
            except Exception as e:
                errors.append(f"Google Places error: {str(e)}")
                return []
        
        # Execute services in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_ticketmaster = executor.submit(call_ticketmaster)
            future_google_places = executor.submit(call_google_places)
            
            # Collect results
            ticketmaster_results = future_ticketmaster.result()
            google_places_results = future_google_places.result()
        
        # Combine all results
        all_results.extend(ticketmaster_results)
        all_results.extend(google_places_results)
        
        # Score and sort results
        scored_results = []
        for event in all_results:
            score = self._score_event(event, keywords)
            scored_results.append((score, event))
        
        # Sort by score (highest first) and return top results
        scored_results.sort(key=lambda x: x[0], reverse=True)
        best_results = [event for score, event in scored_results[:max_results]]
        
        # Track which sources were used in results
        sources = {event.get('source') for event in best_results}
        
        # Add metadata to response
        response_data = {
            'query': {
                'city': city,
                'country_code': country_code,
                'keywords': keywords,
                'start_date': start_date,
                'max_results': max_results
            },
            'metadata': {
                'total_results': len(best_results),
                'sources_used': list(sources),
                'timestamp': datetime.now().isoformat(),
                'errors': errors
            },
            'events': best_results
        }
        
        return response_data
    
    def get_events_json(self, city: str, country_code: str, keywords: Optional[str] = None,
                       start_date: Optional[str] = None, max_results: int = 20) -> str:
        """
        Return aggregated events as a properly formatted JSON string for API responses and export.
        
        Args:
            city (str): The city to search for events in
            country_code (str): Two-letter ISO 3166-1 alpha-2 country code (e.g., 'US', 'CA')
            keywords (str, optional): Keywords to filter events by category or type. Defaults to None
            start_date (str, optional): ISO 8601 format start date filter. Defaults to None
            max_results (int, optional): Maximum number of results to return. Defaults to 20
        
        Returns:
            str: JSON-formatted string containing the complete event aggregation response
                with proper indentation and encoding. Includes all event data, metadata,
                and query information in a structured, readable format.
            
        Raises:
            ValueError: If parameters are invalid (propagated from get_events)
            json.JSONEncodeError: If response data contains non-serializable objects
        """
        results = self.get_events(city, country_code, keywords, start_date, max_results)
        return json.dumps(results, indent=2, default=str)

    @staticmethod
    def get_description() -> Dict[str, Any]:
        """
        Get the static service description for OpenAI function calling integration.
        
        Returns:
            Dict[str, Any]: OpenAI function calling descriptor with comprehensive parameter schema
        """
        return EventServiceAggregator.SERVICE_DESCRIPTION