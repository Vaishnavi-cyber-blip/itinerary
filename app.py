import base64
import streamlit as st
import sys
import time
from crewai import Agent, Task, Crew, Process
from langchain.agents import Tool
import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from crewai_tools import SerperDevTool
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search.tool import TavilySearchResults

st.set_page_config(page_title="itinerary", page_icon="🧳")
load_dotenv()
groq_api_key = os.environ["GROQ_API_KEY"]
tavily_api_key = os.environ["TAVILY_API_KEY"]
serper_api_key=os.environ["SERPER_API_KEY"]

llm = ChatGroq(api_key=groq_api_key, model="llama3-8b-8192")
search = TavilySearchAPIWrapper(tavily_api_key=tavily_api_key)
tavily_tool = TavilySearchResults(api_wrapper=search)
tool = SerperDevTool(serper_api_key=serper_api_key)
task_values = []

@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("assets/wall6.png")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:image/png;base64,{img}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

[data-testid="stSidebar"] > div:first-child {{
    background-image: url("data:image/png;base64,{img}");
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
    right: 2rem;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

def create_crewai_setup(tripfrom, budget, days, tripto):
    # Define the city insights agent first
    city_insights = Agent(
        role="Tour and travel agent",
        goal=f"""Perform detailed research about {tripfrom} and {tripto} to provide the Itinerary planner 
                deep analysis of accommodation, transport, culture, and other insights of the place.

            Important:
                    - Once you know the selected city, provide keenly researched insights of the city.
                    - Research local events, activities, food, transport, and accommodation information.
                    - Keep the information detailed.
                    - Avoid reusing the same input.
                    """,
        backstory=f"""A knowledgeable Tour and travel agent with extensive information 
                    about every city of India, its attractions, customs, food, locals and always updated 
                    about current events in the city.""",
        verbose=True,
        allow_delegation=True,
        tools=[tavily_tool, tool],
        llm=llm,
    )

    # Define the travel agent
    Travel_Agent = Agent(
        role="Itinerary Planner",
        goal=f"""Plan a detailed itinerary based on the factors like number of days, travelling from, travelling to, budget of trip.
                Travelling from: {tripfrom}
                Budget: {budget}
                Number of Days: {days}
                Trip to: {tripto}

                Important:
                    - Final output must contain all the detailed plan of the locations perfect for customs, culture 
                    information, tourist attractions, activities, food a traveller can follow.
                    - Avoid reusing the same input.""",
        backstory=f"""Itinerary planner who is well-versed with places in India and has expertise in planning an itinerary for any place within India.""",
        verbose=True,
        allow_delegation=True,
        context=[city_insights],
        tools=[tavily_tool, tool],
        llm=llm,
    )

    # Define tasks for the travel agent and city insights agent
    task1 = Task(
        description=f"""Perform detailed research about {tripfrom} and {tripto} to provide the Itinerary planner 
                deep analysis of accommodation, transport, culture, and other insights of the place.""",
        expected_output="Detailed research report",
        agent=city_insights,
    )

    task2 = Task(
        description=f"""Plan a detailed itinerary for the trip considering number of days, budget, and locations 
                        perfect for customs, culture information, tourist attractions, activities, food.""",
        expected_output="Detailed itinerary plan",
        agent=Travel_Agent,
    )

    # Create and run the crew
    itinerary_crew = Crew(
        agents=[city_insights, Travel_Agent],
        tasks=[task1, task2],
        verbose=2,
        process=Process.sequential,
    )

    crew_result = itinerary_crew.kickoff()
    return crew_result


class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange']  # Define a list of colors
        self.color_index = 0  # Initialize color index

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Apply different color and switch color index
            self.color_index = (self.color_index + 1) % len(self.colors)  # Increment color index and wrap around if necessary

            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        if "Itinerary Planner" in cleaned_data:
            # Apply different color 
            cleaned_data = cleaned_data.replace("Itinerary Planner", f":{self.colors[self.color_index]}[Itinerary Planner]")
        if "Tour and travel agent" in cleaned_data:
            cleaned_data = cleaned_data.replace("Tour and travel agent", f":{self.colors[self.color_index]}[Tour and Travel agent]")
        
        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []


def main():
    
    st.markdown("<h1 style='color: #004aad; text-align: center;'>Itinerary Planner</h1>", unsafe_allow_html=True)
    with st.expander("About the Team:"):
        left_co, cent_co,last_co = st.columns(3)
        with cent_co:
            st.image("logo.png")
        st.subheader("Agent 1")
        st.text("""       
        Role = Itinerary Planner
        Goal = Plan a detailed itinerary based on the factors like number of days, travelling from, travelling to, budget of trip.
        Backstory = Itinerary planner who is well versed with places of India and  has expertise in planning an itinerary for any place within India.
        Task = Plan a personalised itinerary.""")
        
        st.subheader("Agent 2")
        st.text("""       
        Role = Tour and travel agent
        Goal = Perform detailed research about {tripfrom} and {tripto} to provide the Itinerary planner 
                deep analysis of accommodation, transport, culture, and other insights of the place.
        Backstory = A knowledgeable Tour and travel agent with extensive information 
                    about every city of India, its attractions, customs, food, locals and always updated 
                    about current events in the city.
        Task = Provide detailed researched content to itinerary planner.""")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        days = st.text_input("Trip From : ")
    with col2:
        tripfrom = st.text_input('Trip To :')
    with col3:
        budget = st.text_input("Budget :")
    with col4:
        tripto = st.text_input("No. of Days:")


    
    if st.button("Run Analysis"):
        stopwatch_placeholder = st.empty()
        
        # Start the stopwatch
        start_time = time.time()
        with st.expander("Processing!"):
            sys.stdout = StreamToExpander(st)
            with st.spinner("Generating Results"):
                crew_result = create_crewai_setup(tripfrom,budget,days,tripto)

        end_time = time.time()
        total_time = end_time - start_time
        stopwatch_placeholder.text(f"Total Time Elapsed: {total_time:.2f} seconds")

        st.header("Results:")
        st.markdown(crew_result)


if __name__ == "__main__":
    main()
