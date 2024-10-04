
from typing import List, Any
from pydantic import BaseModel


# Define the GraphState model
class GraphState(BaseModel):
    question: str
    answer: str = ""
    chat_history: List[str] = []
    next_step: str = "start"

