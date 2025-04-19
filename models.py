from pydantic import BaseModel, Field
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
import uuid

class AskInput(BaseModel):
    user_query: str =  Field(...,description="The question asked by the user", example="What is the status of my ticket?")
    session_id: uuid.UUID = Field(..., description="Unique identifier for a user session")

class State(TypedDict):
    messages: Annotated[list, add_messages]