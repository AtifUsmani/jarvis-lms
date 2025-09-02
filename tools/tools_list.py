from datetime import datetime
from langchain.tools import Tool
from tools.tools import get_temperature, get_humidity, remember_fact, recall_fact
from tools.weather import get_weather
from tools.system_tools import system_status_tool
from robots.spider_bot import esp_walk

def get_time(_):
    return f"The current time is {datetime.now().strftime('%H:%M:%S')}"

tools = [
    Tool.from_function(
        name="get_time",
        func=get_time,
        description="Returns the current time."
    ),
    Tool.from_function(
        name="get_weather",
        func=get_weather,
        description="Returns the current weather."
    ),
    Tool.from_function(
        name="esp_walk",
        func=esp_walk,
        description="Makes the spider bot move forward."
    ),
    Tool.from_function(
        name="get_temperature",
        func=get_temperature,
        description="Gets the current room temperature from Home Assistant."
    ),
    Tool.from_function(
        name="get_humidity",
        func=get_humidity,
        description="Returns the humidity."
    ),
    Tool(
        name="SystemStatus",
        func=system_status_tool,
        description="Check real-time CPU, RAM, disk, network, and GPU usage."
    ),
    # Tool.from_function(
    #     name="remember_fact",
    #     func=remember_fact,
    #     description="Use this to store facts or user preferences in memory. Input should be in the format: '<key>: <value>'."
    # ),
    # Tool.from_function(
    #     name="recall_fact",
    #     func=recall_fact,
    #     description="Use this to recall facts or preferences stored earlier. Input should be the key you want to retrieve."
    # )
]
