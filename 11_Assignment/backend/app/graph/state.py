from typing import Annotated, List, Optional, TypedDict
import operator
from langchain_core.messages import BaseMessage

# This is the state of our graph
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next: Optional[str]
