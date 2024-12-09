# Itinerary Planner - Trip Bharat
Itinerary Planner is a Streamlit-based application that uses AI agents to generate personalized travel itineraries. It leverages powerful tools like LangChain, CrewAI, and custom APIs to provide detailed insights and recommendations for your trip.

## Features
- **User-Friendly Interface:** Input trip details directly from a sleek Streamlit app.
- **AI-Driven Insights:** Uses advanced language models and search tools to plan itineraries.
- **Multi-Agent System:** Employs specialized agents to handle research and itinerary planning.
- **Custom Styling:** Engaging visual design with background images.
- **Detailed Output:** Generates a comprehensive travel plan, including accommodations, transport, culture, and activities.

## How it works
### 1. Custom AI Agents:
   - Tour and Travel Agent:
       - Researches the destination for accommodations, culture, and activities.
       - Uses tools like Tavily Search and SerperDev Tool.
    
### 2. Itinerary Planner:
- Creates a personalized travel plan based on user inputs.

### 3. Multi-Agent Crew:
- Tasks are executed sequentially
      - The research agent gathers data.
      - The planner agent organizes it into a detailed itinerary

## Technologies Used
- Streamlit: User interface for receiving inputs and displaying results.
- Groq API: Utilizes the Llama3 model for language understanding and generation.
- CrewAI Framework: Defines collaborative agents and their respective tasks.
- LangChain Tools:
    - SerperDevTool: For Google-based search queries.
    - TavilySearchAPIWrapper: For retrieving detailed search results.

- Python Libraries:
  - base64: For encoding background images.
  - os: For handling environment variables.
  - time and sys: For processing tasks and timers.
  - re: For text processing in logs.
    
## Interface

  ![s7](https://github.com/user-attachments/assets/d822043a-776d-4ffd-b945-661d2574fb93)
