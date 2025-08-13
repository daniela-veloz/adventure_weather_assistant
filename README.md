---
title: Adventure Weather Assistant
emoji: 🌤️
colorFrom: blue
colorTo: purple
sdk: docker
app_file: app.py
pinned: false
license: mit
short_description: AI activity planner with weather and events
---

# 🌤️ Adventure Weather Assistant

An intelligent activity planning assistant that combines real-time weather data with local event information to suggest
personalized activities. Built with Streamlit and powered by OpenAI GPT-4o-mini.

## 🚀 Features

- **🌦️ Real-time Weather Integration**: 7-day weather forecasts from WeatherAPI
- **🎭 Event Discovery**: Live events from TicketMaster and Google Places
- **🤖 AI-Powered Recommendations**: Intelligent activity suggestions based on weather conditions
- **💬 Conversational Interface**: Natural chat interface with conversation memory
- **🛡️ Rate Limiting**: Fair usage controls (10/hour, 25/day per IP)
- **🌐 Web Interface**: Modern Streamlit-based chat interface

## 🎓 LLM Techniques & Learning Opportunities

This project serves as a comprehensive learning platform for modern LLM application development, covering essential techniques and patterns used in production AI systems:

### 🔧 **Function Calling & Tool Use**
- **OpenAI Function Calling**: Learn how to extend LLM capabilities with external tools
- **Function Registry Pattern**: Implement dynamic function mapping for extensible AI agents
- **Tool Orchestration**: Coordinate multiple API calls based on LLM decisions
- **Parameter Validation**: Handle function arguments and ensure proper API integration

### 💬 **Conversation Management**
- **Memory Systems**: Maintain context across multi-turn conversations
- **Session State**: Persist conversation data in web applications

### 🎯 **Prompt Engineering**
- **System Prompts**: Design effective instructions for AI behavior and personality
- **Function Call Guidance**: Write prompts that encourage proper tool usage
- **Error Recovery**: Handle edge cases and guide LLMs through failure scenarios
- **Iterative Processing**: Handle multi-step workflows with function calls


### 🏗️ **Production AI Architecture**
- **Modular Design**: Separate concerns between UI, business logic, and external services
- **Service Layer Pattern**: Abstract API integrations for maintainability
- **Rate Limiting**: Implement fair usage policies for API cost control

### 📊 **Real-World Integration**
- **Multi-API Orchestration**: Combine weather, events, and location data intelligently
- **Parallel Processing**: Execute multiple API calls concurrently for better performance
- **Data Aggregation**: Merge and rank results from multiple sources


This project provides a practical foundation for understanding how to build, deploy, and maintain AI-powered applications in real-world scenarios.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          Adventure Weather Assistant                            │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────────────────────────────────────────────┐
│   Streamlit     │    │                  Backend Services                        │
│   Frontend      │    │                                                          │
│                 │    │  ┌─────────────────┐    ┌──────────────────────────────┐ │
│  ┌──────────┐   │    │  │ Activity        │    │        LLM Client            │ │
│  │ Chat UI  │◄──┼────┼──► Adventure      │◄───┤     (OpenAI GPT-4o-mini)     │ │
│  │          │   │    │  │ Agent           │    │   - Function Calling         │ │
│  │ Rate     │   │    │  │                 │    │   - Conversation Memory      │ │
│  │ Limiter  │   │    │  │ ┌─────────────┐ │    │   - Error Handling           │ │
│  │          │   │    │  │ │ Function    │ │    └──────────────────────────────┘ │
│  │ Usage    │   │    │  │ │ Registry    │ │                                     │
│  │ Stats    │   │    │  │ └─────────────┘ │                                     │
│  └──────────┘   │    │  └─────────────────┘                                     │
└─────────────────┘    └──────────────────────────────────────────────────────────┘
                                            │
                        ┌───────────────────┼───────────────────┐
                        │                   │                   │
                        ▼                   ▼                   ▼
            ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
            │ Weather Service │ │ Event Service   │ │   Rate Limiter  │
            │                 │ │ Aggregator      │ │                 │
            │ ┌─────────────┐ │ │                 │ │ ┌─────────────┐ │
            │ │ WeatherAPI  │ │ │ ┌─────────────┐ │ │ │ IP Extractor│ │
            │ │ Integration │ │ │ │ TicketMaster│ │ │ │             │ │
            │ │             │ │ │ │   Service   │ │ │ │ File-based  │ │
            │ │ - Current   │ │ │ │             │ │ │ │ Tracking    │ │
            │ │   Weather   │ │ │ │ Google      │ │ │ │             │ │
            │ │ - 7-day     │ │ │ │ Places      │ │ │ │ Hourly &    │ │
            │ │   Forecast  │ │ │ │ Service     │ │ │ │ Daily       │ │
            │ │             │ │ │ │             │ │ │ │ Limits      │ │
            │ └─────────────┘ │ │ │ Parallel    │ │ │ └─────────────┘ │
            └─────────────────┘ │ │ Processing  │ │ └─────────────────┘
                                │ │ & Ranking   │ │
                                │ └─────────────┘ │
                                └─────────────────┘

                            External APIs
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   OpenAI    │ │ WeatherAPI  │ │TicketMaster │ │Google Places│
    │     API     │ │     API     │ │     API     │ │     API     │
    └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

## 🔧 Core Components

### Frontend Layer
- **Streamlit App** (`app.py`): Web interface with chat UI, rate limiting display, and usage stats
- **Rate Limiting**: IP-based request tracking with visual feedback

### Business Logic Layer
- **ActivityAdventureAgent**: Main orchestrator with function calling and conversation management
- **LLMClient**: Enhanced OpenAI client with function calling, error recovery, and conversation history
- **Function Registry**: Maps LLM function calls to actual service methods

### Service Layer
- **WeatherService**: WeatherAPI integration for current conditions and 7-day forecasts
- **EventServiceAggregator**: Multi-source event discovery with parallel processing
- **TicketMasterService**: Live entertainment events from TicketMaster Discovery API
- **GooglePlacesService**: Event venues and local attractions from Google Places API
- **RateLimiter**: IP-based rate limiting with hourly/daily limits

### Data Flow
1. **User Input** → Streamlit chat interface
2. **Rate Check** → Validate user can make request
3. **Agent Processing** → LLM determines need for function calls
4. **Parallel API Calls** → Weather + Events data fetched simultaneously
5. **AI Response** → LLM generates personalized recommendations
6. **Display** → Formatted response with events, weather, and activities

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- API Keys for:
  - OpenAI (GPT-4o-mini)
  - WeatherAPI
  - TicketMaster Discovery API
  - Google Places API

### Setup

1. **Clone the repository**
   ```bash
   git clone git@github.com:daniela-veloz/adventure_weather_assistant.git
   cd adventure_weather_assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   WEATHER_API_KEY=your_weatherapi_key
   TICKETMASTER_API_KEY=your_ticketmaster_api_key
   GOOGLE_PLACES_API_KEY=your_google_places_api_key
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the app**
   Open your browser to `http://localhost:8501`

## 🎯 Usage

### Basic Queries
- "What should I do in Seattle today?"
- "Find outdoor activities in San Francisco"
- "What events are happening in Austin this weekend?"
- "Give me indoor activities for a rainy day in London"

### Advanced Features
- **Conversation Memory**: Follow-up questions remember previous context
- **Weather-Aware**: Suggestions adapt to current and forecasted conditions
- **Multi-day Planning**: Ask about "next week" for 7-day recommendations
- **Event Integration**: Real-time events with dates, venues, and ticket links

## 🚦 Rate Limits

To ensure fair usage:
- **Hourly**: 10 requests per hour per IP
- **Daily**: 25 requests per day per IP
- **No Cooldown**: Immediate follow-up questions allowed

Rate limit status is displayed in the sidebar with real-time usage statistics.

## 📁 Project Structure

```
adventure_weather_assistant/
├── app.py                          # Main Streamlit application
├── backend/                        # Backend services package
│   ├── __init__.py                 # Package initialization
│   ├── activity_adventure_agent.py # Main conversational agent
│   ├── llm_client.py              # Enhanced OpenAI client
│   ├── weather_service.py         # Weather API integration
│   ├── event_service.py           # Abstract event service base
│   ├── ticketmaster_service.py    # TicketMaster API client
│   ├── google_places_service.py   # Google Places API client
│   ├── event_service_aggregator.py # Multi-source event aggregation
│   ├── rate_limiter.py            # IP-based rate limiting
│   └── ip_extractor.py            # Client IP extraction
├── simple_app.py                  # Alternative Flask interface
├── streamlit_app.py               # Standalone Streamlit version
├── adventure_weather_assistant.ipynb # Original notebook (reference)
├── CLAUDE.md                      # Development documentation
└── README.md                      # This file
```

## 🔌 API Integrations

### OpenAI GPT-4o-mini
- **Function Calling**: Automatic weather and event data retrieval
- **Conversation Memory**: Multi-turn conversation support
- **Error Recovery**: Graceful handling of API failures

### WeatherAPI
- **Current Conditions**: Real-time weather data
- **7-Day Forecasts**: Extended weather planning
- **Global Coverage**: Weather for cities worldwide

### TicketMaster Discovery API
- **Live Events**: Concerts, sports, theater, and more
- **Event Details**: Dates, venues, ticket links
- **Location-based**: Events near specified cities

### Google Places API
- **Venue Discovery**: Entertainment venues and attractions
- **Location Details**: Addresses, ratings, and information
- **Activity Suggestions**: Local points of interest

## 🛡️ Security & Privacy

- **IP-based Rate Limiting**: Prevents abuse without user registration
- **Environment Variables**: Secure API key management
- **No Personal Data Storage**: Conversations are not persisted
- **Error Handling**: Graceful failures without exposing sensitive information
