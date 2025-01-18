from playwright.async_api import BrowserContext
from typing_extensions import TypedDict
from typing import List, Optional
from langchain_core.messages import BaseMessage
from extraction.extraction_prompt import ExtractionResponse

# from reasoning.reasoning_prompt import ReasoningResponse
from execution.execution_prompt import ExecutionResponse

from pydantic import BaseModel, Field


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


# Output Pydantic
class ReasoningResponse(BaseModel):
    thought: str = Field(
        description="A brief reasoning explaining why this action was chosen."
    )
    action: str = Field(
        description="A concrete description of the action to take. Please only include a single immediate next action to take. E.g. Update the party size selector on web page to 3."
    )


class ReasoningTrajectory:
    state: str
    action: str


# This represents the state of the agent
# as it proceeds through execution
class AgentState(TypedDict):
    browser: BrowserContext  # The Playwright browser that includes all opened pages
    input: str  # User request
    img: str  # b64 encoded screenshot
    bboxes: List[BBox]  # The bounding boxes from the browser annotation function
    extraction: ExtractionResponse
    reasoning: ReasoningResponse
    execution: ExecutionResponse
    scratchpad: List[BaseMessage]
    observation: str  # The most recent response from a tool
    date_today: str
    user_request: str  # A summary of user's requests so far
    reasoning_trajectory: List[ReasoningTrajectory]
