# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **modular Python Adventure Weather Assistant** that combines real-time weather data with local event information to suggest personalized activities. The project has been refactored from a single Jupyter notebook into a well-structured modular codebase with separate files for each component.

## Development Environment

- **Language**: Python 3.x with modular file structure
- **Entry Point**: `main.py` - Application launcher with environment validation
- **Interface**: Gradio ChatInterface for web-based chat interaction
- **AI Model**: OpenAI GPT-4o-mini for conversational AI
- **Legacy**: `adventure_weather_assistant.ipynb` - Original implementation (reference only)

## Required API Keys

The project requires these API keys in environment variables:
```
OPENAI_API_KEY=your_openai_api_key
WEATHER_API_KEY=your_weatherapi_key  
TICKETMASTER_API_KEY=your_ticketmaster_api_key
GOOGLE_PLACES_API_KEY=your_google_places_api_key
```

## File Structure

```
adventure_weather_assitant/
├── main.py                         # Application entry point
├── llm_client.py                   # Enhanced OpenAI client
├── weather_service.py              # Weather API integration
├── event_service.py                # Abstract base class for events
├── ticketmaster_service.py         # TicketMaster API client
├── google_places_service.py        # Google Places API client
├── event_service_aggregator.py     # Multi-source event aggregation
├── activity_adventure_agent.py     # Main conversational agent
├── adventure_weather_assistant.ipynb  # Original notebook (reference)
├── README.md                       # HuggingFace metadata
├── index.html & style.css          # Static web files
└── CLAUDE.md                       # This file
```

## Architecture

### Core Components
- **LLMClient** (`llm_client.py`): Enhanced OpenAI client with advanced function calling and iterative processing
- **WeatherService** (`weather_service.py`): WeatherAPI integration for current conditions and forecasts (1-7 days)
- **EventService** (`event_service.py`): Abstract base class defining interface for event providers
- **TicketMasterService** (`ticketmaster_service.py`): Live entertainment events from TicketMaster Discovery API
- **GooglePlacesService** (`google_places_service.py`): Event venues from Google Places API
- **EventServiceAggregator** (`event_service_aggregator.py`): Multi-source event aggregation with parallel processing and intelligent ranking
- **ActivityAdventureAgent** (`activity_adventure_agent.py`): Main conversational agent with function registry

### Function Calling System
The project uses sophisticated LLM function calling where the AI agent can:
- Automatically call weather APIs based on user queries
- Search for events using multiple data sources in parallel
- Aggregate and rank results intelligently
- Provide weather-aware activity recommendations

## Development Commands

### Running the Application
```bash
# Run the main application
python app.py

# This will:
# 1. Load and validate environment variables
# 2. Initialize all services with API key validation
# 3. Launch Gradio web interface
```

### Testing Individual Components

```python
# Test weather service
from backend.weather_service import WeatherService

weather_service = WeatherService()
forecast = weather_service.fetch_weather("London", 3)

# Test event aggregation
from backend.event_service_aggregator import EventServiceAggregator

aggregator = EventServiceAggregator()
results = aggregator.get_events("Seattle", "US", "music", max_results=5)

# Test chat agent
from backend.activity_adventure_agent import ActivityAdventureAgent

agent = ActivityAdventureAgent()
response = agent.chat("What should I do in Austin?", [])
```

### Development Workflow
```bash
# Install dependencies
pip install openai requests python-dotenv gradio

# Set up environment variables in .env file
# Run the application
python app.py
```

## Key Dependencies

```python
# Core dependencies by module:
# llm_client.py
from openai import OpenAI
from typing import Dict, Any, List, Optional, Callable
import json

# weather_service.py
import requests
import os

# event services
from abc import ABC, abstractmethod
import concurrent.futures
from datetime import datetime

# app.py
import gradio as gr
from dotenv import load_dotenv
```

## Working with the Codebase

- **Modular structure** - each class in its own file for better maintainability
- **Import dependencies** - modules import only what they need
- **Clear separation of concerns** - each file has a single responsibility
- **Gradio interface** - accessible via browser after running main.py
- **Function calling is automatic** - the LLM determines when to call weather/event APIs
- **Parallel processing** - event services run concurrently for better performance
- **Comprehensive error handling** - graceful failures with user-friendly messages

## Data Flow

1. `main.py` loads environment and initializes `ActivityAdventureAgent`
2. User sends message via Gradio chat interface
3. `ActivityAdventureAgent` processes with `LLMClient` function calling
4. LLM automatically determines need for weather/event data
5. `WeatherService` and `EventServiceAggregator` called in parallel
6. `EventServiceAggregator` coordinates `TicketMasterService` and `GooglePlacesService`
7. Results aggregated, scored, and ranked
8. LLM generates final response with activity recommendations
9. Response displayed in chat interface

## Adding New Features

- **New event sources**: Extend `EventService` abstract class
- **New APIs**: Follow the service pattern with environment variable configuration
- **Enhanced LLM features**: Extend `LLMClient` capabilities
- **New function calls**: Add to `ActivityAdventureAgent.function_registry`

## HuggingFace Space Configuration

This project includes HuggingFace Space configuration files:
- `README.md`: HuggingFace metadata and configuration
- `index.html` & `style.css`: Static web interface (separate from Gradio)