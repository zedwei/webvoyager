from playwright.async_api import BrowserContext
from typing_extensions import TypedDict
from typing import List, Optional
from langchain_core.messages import BaseMessage
from extraction.extraction_prompt import ExtractionResponse
from reasoning.reasoning_prompt import ReasoningResponse
from execution.execution_prompt import ExecutionResponse


class BBox(TypedDict):
    x: float
    y: float
    text: str
    type: str
    ariaLabel: str


class Prediction(TypedDict):
    action: str
    args: Optional[List[str]]
    thought: str


# This represents the state of the agent
# as it proceeds through execution
class AgentState(TypedDict):
    browser: BrowserContext  # The Playwright browser that includes all opened pages
    input: str  # User request
    img: str  # b64 encoded screenshot
    bboxes: List[BBox]  # The bounding boxes from the browser annotation function
    extraction: ExtractionResponse
    reasoning: ReasoningResponse
    execution: dict
    scratchpad: List[BaseMessage]
    observation: str  # The most recent response from a tool
    date_today: str
    user_request: str # A summary of user's requests so far
    
