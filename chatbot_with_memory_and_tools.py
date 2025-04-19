# Refer - https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-2-enhancing-the-chatbot-with-tools

from langgraph.checkpoint.memory import MemorySaver # this will store the memory in RAM
# from langgraph.checkpoint.sqlite import SQliteSaver # this will store the memory in SQlite. For this, we need to install langchain-checkpoint-sqlite

# Creating an object of MemorySaver class
memory = MemorySaver()

# Getting groq-api-key from env
import os
from dotenv import load_dotenv
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

# loading groq llm model
from langchain_groq.chat_models import ChatGroq
# llm = ChatGroq(api_key=groq_api_key, model="llama-3.3-70b-versatile")
llm = ChatGroq(api_key=groq_api_key, model="llama-3.1-8b-instant")

# loading required tools from langchain -
from langchain_community.tools.tavily_search import TavilySearchResults
tavilyTool = TavilySearchResults(max_results=1)

# Defining a custom tool -
from langchain_community.tools import tool
@tool
def multiplier(a: int,b: int):
     """Mutliplies 2 integers"""
     return a*b

tools = [tavilyTool, multiplier]

# binding the llm with tools defined so that our bot can make use of the llm as well as the tools as and when needed -
llm_with_tools = llm.bind_tools(tools)

# langgraph bot -
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.errors import GraphRecursionError
# from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def chatbot(state: State):
    # print('\ncurrent state >', state)
    print('\nstate messages length >', len(state['messages']))

    # llm_invoke_result = llm_with_tools.invoke(state["messages"][-4:])
    llm_invoke_result = llm_with_tools.invoke(state["messages"])

    return {"messages": [llm_invoke_result]}
graph_builder.add_node("chatbot", chatbot)
tools_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tools_node)
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}, "recursion_limit": 10} # thread_id is like a session ID. Changing this id will make the bot forget the converstation history of the previous session. Setting a Recursion limit prevents langgraph from keeping on calling tools or the llm for finding the answer. By default this is 25, I've set it here to 10

def stream_graph_updates(user_input: str):
    # events = graph.stream(
    #     {"messages": [{"role": "user", "content": user_input}]},
    #     config,
    # )
    # for event in events:
    #     print('\nevent.values() >', event.values())
    #     for value in event.values():
    #         print('value >', value)
    #         print("\nAssistant:", value["messages"][-1].content)

    events = graph.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
    )
    # print('\nevents >', events)
    
    print("\nAssistant:", events["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except GraphRecursionError:
        print("Couldn't fetch result at the moment due to recursion error")
    # except:
    #     # fallback if input() is not available
    #     user_input = "What do you know about LangGraph?"
    #     print("\nUser: " + user_input)
    #     stream_graph_updates(user_input)
    #     break