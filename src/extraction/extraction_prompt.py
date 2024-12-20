from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts.chat import MessagesPlaceholder
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time
from globals import GLOBAL_PROMPT_TEMPLATE

# Prompt template
extraction_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate(
            prompt=[
                PromptTemplate.from_file(f"./src/extraction/extraction_prompt.md"),
            ],
        ),
        HumanMessagePromptTemplate(
            prompt=[
                PromptTemplate.from_template("[Web Page]\n"),
                ImagePromptTemplate(
                    template={"url": "data:image/png;base64,{img}"},
                    input_variables=[
                        "img",
                    ],
                ),
                PromptTemplate.from_template("\n\nCurrent URL: {current_url}"),
            ],
        ),
        GLOBAL_PROMPT_TEMPLATE,
        MessagesPlaceholder(
            optional=True,
            variable_name="scratchpad",
        ),
    ],
    input_variables=[
        "bbox_descriptions",
        "img",
        "current_url",
    ],
    partial_variables={"scratchpad": []},
)


# Output Pydantic
class ExtractionResponse(BaseModel):
    thought: str = Field(
        description="A summary of where each parameter was extracted from"
    )
    request_name: Optional[str] = Field(description="Restaurant Name from user input")
    request_date: Optional[date] = Field(description="Date from user input")
    request_time: Optional[time] = Field(description="Time from user input")
    request_count: Optional[int] = Field(description="Party size from user input")

    status_name: Optional[str] = Field(description="Restaurant from web page")
    status_date: Optional[date] = Field(description="Date from web page")
    status_time: Optional[time] = Field(description="Time from web page")
    status_count: Optional[int] = Field(description="Party size from web page")

    list_name: Optional[List[str]] = Field(
        description="List of restaurant names displayed on the search result page"
    )
    list_time: Optional[List[time]] = Field(
        description="List of availabile time slot on the detailed page"
    )

    webpage_category: Optional[str] = Field(
        description="Web page category. Values: Homepage, Search result page, Detailed page, Booking page."
    )

    user_request: Optional[str] = Field(
        description="A summary of user's query along with responses to any clarification questions provided in the [User Request] section"
    )
