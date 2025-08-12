from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class EventService(ABC):
    """
    Abstract base class defining the interface for event service providers in the Adventure Weather Agent.
    
    This abstract class establishes a standardized interface for different event data sources 
    (such as TicketMaster, Google Places, and future event APIs) to ensure consistent method 
    signatures, parameter handling, and return formats across all implementations. It enables
    the EventServiceAggregator to work seamlessly with multiple event sources while maintaining
    a unified interface.
    
    Design Principles:
    - Consistent method signatures across all event service implementations
    - Standardized parameter validation and error handling patterns
    - Uniform return data formats for seamless aggregation
    - Location-based search capabilities with international support
    - Flexible filtering options for keywords, dates, and result limits
    - Abstract interface allows easy addition of new event data sources
    
    Implementation Requirements:
    All concrete implementations must provide the get_events method with the exact signature
    defined below. The method should handle location-based event searching with optional
    filtering capabilities and return normalized event data structures.
    
    Supported Event Sources:
    - TicketMasterService: Live entertainment events, concerts, sports, theater
    - GooglePlacesService: Event venues and entertainment locations
    - Future implementations: Eventbrite, Facebook Events, local event APIs
    """
    
    @abstractmethod
    def get_events(self, city: str, country_code: str, keywords: Optional[str] = None,
                start_date: Optional[str] = None, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Abstract method to retrieve events based on location and search criteria.
        
        This method defines the core interface that all event service implementations must provide
        to ensure consistent behavior across different event data sources. It establishes
        standardized parameters for location-based event searching with flexible filtering options.
        
        All implementations must handle parameter validation, API authentication, request formatting,
        error handling, and response normalization to provide consistent results regardless
        of the underlying event data source.
        
        Parameter Requirements:
        - city: Must support international city names and various formats
        - country_code: Must be ISO 3166-1 alpha-2 format (e.g., 'US', 'CA', 'GB')
        - keywords: Should support flexible keyword matching for event types and genres
        - start_date: Should accept ISO 8601 format for date filtering
        - max_results: Should be configurable with reasonable limits based on API constraints
        
        Args:
            city (str): The city to search for events in. Must support international cities
                       and various naming conventions (e.g., 'New York', 'Los Angeles', 'London')
            country_code (str): Two-letter ISO 3166-1 alpha-2 country code for geographic
                              filtering (e.g., 'US', 'CA', 'GB', 'FR', 'DE', 'AU')
            keywords (str, optional): Keywords to filter events by type, genre, or category
                                    (e.g., 'music', 'comedy', 'sports', 'theater', 'art').
                                    Should support flexible matching. Defaults to None
            start_date (str, optional): Event start date filter in ISO 8601 format
                                      (e.g., '2025-08-10T00:00:00Z'). Used to find events
                                      occurring on or after this date. Defaults to None
            max_results (int, optional): Maximum number of results to return. Should be
                                       configurable based on API limitations and performance
                                       considerations. Defaults to 20
        
        Returns:
            List[Dict[str, Any]]: Standardized list of event dictionaries. Each event should
                                 contain consistent fields regardless of the data source:
                - id: Unique event identifier from the source system
                - name: Event name or title
                - source: Data source identifier (e.g., 'ticketmaster', 'google_places')
                - type: Event type ('event' for confirmed events, 'venue' for venue listings)
                - dates: Date and time information (start, end, timezone)
                - venue: Venue information (name, address, location coordinates)
                - Additional source-specific fields as appropriate
            
        Raises:
            NotImplementedError: If the concrete class doesn't implement this method
            ValueError: If required parameters are invalid or missing
            Exception: If API requests fail or data cannot be retrieved
        """
        pass