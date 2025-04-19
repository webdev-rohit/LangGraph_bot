# defining this for maintaining conversation memory
from langgraph.checkpoint.memory import MemorySaver 
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

# importing tools
from used_tools import tools

# binding llm with tools
llm_with_tools = llm.bind_tools(tools)

# langgraph bot -
from models import State
from langgraph.graph import StateGraph, START, END # Start and end nodes
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.errors import GraphRecursionError
# from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

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

def answer_query(user_query, session_id):
    config = {"configurable": {"thread_id": session_id}, "recursion_limit": 10} # thread_id is like a session ID. Changing this id will make the bot forget the converstation history of the previous session. Setting a Recursion limit prevents langgraph from keeping on calling tools or the llm for finding the answer. By default this is 25, I've set it here to 10
    try:
        events = graph.invoke(
            {"messages": [{"role": "user", "content": user_query}]},
            config,
        )
        # print('\nevents >', events)
        print("\nAssistant:", events["messages"][-1].content)
        return events["messages"][-1].content
    except GraphRecursionError as e:
        print("Couldn't fetch result at the moment due to recursion error")
        return e
