# Refer - https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-3-adding-memory-to-the-chatbot

# This code handles conversation memory of a bot based on the thread_id(session_id) and passes last 4 messages to the llm invoke function. Basically, the state will keep the history of the entire session but will pass only the most recent 4 messages to the llm for invoking.

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
llm = ChatGroq(api_key=groq_api_key, model="llama-3.3-70b-versatile")

# langgraph bot -
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END # Start and end nodes are also 
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def chatbot(state: State):
    print('\ncurrent state >', state)
    print('\nstate messages length >', len(state['messages']))
    
    return {"messages": [llm.invoke(state["messages"][-4:])]} # sending only the last messages to the llm

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
# the above 2 lines define the flow like this: START -> chatbot -> END

graph = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}} # this is like a session ID. Changing this id will make the bot forget the converstation history of the previous session.

def stream_graph_updates(user_input: str):
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
    )    
    for event in events:
        for value in event.values():
            print("\nAssistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("\nUser: " + user_input)
        stream_graph_updates(user_input)
        break