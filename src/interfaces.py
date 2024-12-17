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
    request_name: str = Field(
        description="Derived Restaurant Name from [User Request] section")
    request_date: Optional[date] = Field(
        description="Derived Booking Date from [User Request] section")
    request_time: Optional[time] = Field(
        description="Derived Booking Time from [User Request] section")
    request_count: int = Field(
        description="Derived Party Size from [User Request] section")

    status_name: Optional[str] = Field(
        description="Derived Restaurant Name from [Current webpage] section")
    status_date: Optional[date] = Field(
        description="Derived Booking Date from [Current webpage] section")
    status_time: Optional[time] = Field(
        description="Derived Booking Time from [Current webpage] section")
    status_count: Optional[int] = Field(
        description="Derived Party Size from [Current webpage] section")

    match: bool = Field(
        description="Whether the restaurant name, date, time, and party size match between the [Current webpage] section and the [User Request] section"
    )
# Pydantic


class ActionResponse(BaseModel):
    thought: str = Field(
        description="A brief description of the action you're trying to perform"
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
