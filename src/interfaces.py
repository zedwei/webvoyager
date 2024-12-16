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
        "Name of the restaurant in user's request instead of from current web page")
    request_date: Optional[date] = Field(
        "date of the booking in user's request instead of from current web page")
    request_time: Optional[time] = Field(
        "Time of the booking in user's request instead of from current web page")
    request_count: int = Field(
        "Number of people of the booking in user's request instead of from current web page")

    name_user: str = Field(
        "If you know the requested restaurant name by user, briefly explain where you got it. E.g. from user typed, or from observation image.")
    date_user: str = Field(
        "If you know the requested booking date by user, briefly explain where you got it. E.g. from user typed, or from observation image.")
    time_user: str = Field(
        "If you know the requested booking time by user, briefly explain where you got it. E.g. from user typed, or from observation image.")
    count_user: str = Field(
        "If you know the requested number of people by user, briefly explain where you got it. E.g. from user typed, or from observation image.")

    status_name: Optional[str] = Field(
        "Name of the restaurant in user's request")
    status_date: Optional[date] = Field(
        "date of the booking in user's request")
    status_time: Optional[time] = Field(
        "Time of the booking in user's request")
    status_count: Optional[int] = Field(
        "Number of people of the booking in user's request")

    match: bool = Field(
        "Whether the restaurant name, date, time, and number of people on the current webpage match user's request"
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
