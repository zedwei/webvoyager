from playwright.async_api import Page, BrowserContext
from typing_extensions import TypedDict
from typing import List, Optional
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from typing import Optional


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
    progress: str


# This represents the state of the agent
# as it proceeds through execution
class AgentState(TypedDict):
    browser: BrowserContext # The Playwright browser that includes all opened pages
    # page: Page  # The Playwright web page lets us interact with the web environment
    input: str  # User request
    img: str  # b64 encoded screenshot
    # The bounding boxes from the browser annotation function
    bboxes: List[BBox]
    prediction: Prediction  # The Agent's output
    # A system message (or messages) containing the intermediate steps
    scratchpad: List[BaseMessage]
    observation: str  # The most recent response from a tool
    step: int # number of steps taken


# Pydantic
class ActionResponse(BaseModel):
    thought: str = Field(
        description="Your brief thoughts (briefly summarize the info that will help ANSWER)."
    )
    progress: str = Field(
        description="Your current step in the ACTION PLAN and a brief description"
    )
    action: str = Field(description="One Action type you choose.")
    label: Optional[int] = Field(
        description="The Numerical Label corresponding to the Web Element that requires interaction."
    )
    content: Optional[str] = Field(
        description="The string to type, or ask user, or answer, or URL string to navigate."
    )
