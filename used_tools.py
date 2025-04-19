# loading required tools from langchain -

# this tool is like Google Search
from langchain_community.tools.tavily_search import TavilySearchResults
tavilyTool = TavilySearchResults(max_results=1)

# Defining a custom multiplier tool
from langchain_community.tools import tool
@tool
def multiplier(a: int,b: int):
    """Mutliplies 2 integers"""
    return a*b

tools = [tavilyTool, multiplier]