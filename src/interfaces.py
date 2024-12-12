from playwright.async_api import BrowserContext
from typing_extensions import TypedDict
from typing import List, Optional
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from datetime import date, time


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
    # page: Page  # The Playwright web page lets us interact with the web environment
    input: str  # User request
    img: str  # b64 encoded screenshot
    # The bounding boxes from the browser annotation function
    bboxes: List[BBox]
    prediction: Prediction  # The Agent's output
    # A system message (or messages) containing the intermediate steps
    scratchpad: List[BaseMessage]
    observation: str  # The most recent response from a tool
    step: int  # number of steps taken


class RestaurantBooking(TypedDict):
    rname: Optional[str] = Field(
        "Name of the restaurant shown on the current page")
    rdate: Optional[date] = Field(
        "date of the booking shown on the current page")
    rtime: Optional[time] = Field(
        "Time of the booking shown on the current page")
    rCount: Optional[int] = Field(
        "Number of people of the booking shown on the current page ")

# Pydantic


class ActionResponse(BaseModel):
    thought: str = Field(
        description="A breif description of the action you're trying to perform"
    )
    action: str = Field(description="One Action type you choose.")
    label: Optional[int] = Field(
        description="The Numerical Label corresponding to the Web Element that requires interaction."
    )
    content: Optional[str] = Field(
        description="The string to type, or ask user, or answer, or URL string to navigate."
    )
    selectLabel: Optional[str] = Field(
        description="The label string of the target select option"
    )
    status: RestaurantBooking
