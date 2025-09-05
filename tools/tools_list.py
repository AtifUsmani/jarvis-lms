from langchain.tools import Tool
from tools.tools import get_temperature, get_humidity, get_date_time
from tools.system_tools import system_status_tool
from robots.spider_bot import esp_walk
from memory.memory import search_memories, get_all_memories, add_memory


tools = [
    Tool.from_function(
        name="get_date_time",
        func=get_date_time,
        description="Returns the current date and time."
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
    Tool(
        name="search_memories",
        func=search_memories,
        description="Search memory with the given query"
    ),
    Tool(
        name="get_all_memories",
        func=get_all_memories,
        description="Retrieve all memories about the user."
    ),
    Tool(
        name="add_memory",
        func=add_memory,
        description="Add messages to memory."
    )
]
