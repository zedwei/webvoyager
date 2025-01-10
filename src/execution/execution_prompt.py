from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts.chat import MessagesPlaceholder
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate
from pydantic import BaseModel, Field
from typing import Optional
from globals import GLOBAL_PROMPT_TEMPLATE

# Prompt template
execution_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate(
            prompt=[
                PromptTemplate.from_file(f"./src/execution/execution_prompt.md"),
            ],
        ),
        HumanMessagePromptTemplate(
            prompt=[
                PromptTemplate.from_template("[Web Page]"),
                ImagePromptTemplate(
                    template={"url": "data:image/png;base64,{img}"},
                    input_variables=[
                        "img",
                    ],
                ),
                PromptTemplate.from_template("{bbox_descriptions}"),
                PromptTemplate.from_template("\n\nCurrent URL: {current_url}"),
            ],
        ),
        GLOBAL_PROMPT_TEMPLATE,
        HumanMessagePromptTemplate(
            prompt=[
                PromptTemplate.from_template(
                    "\n\n User's Request so far: \n {user_request}\n"
                ),
                PromptTemplate.from_template("\n Your task: {task_description}"),
            ]
        ),
    ],
    input_variables=[
        "bbox_descriptions",
        "img",
        "current_url",
        "task_description",
        "user_request",
    ],
)


# Output Pydantic
class ExecutionResponse(BaseModel):
    thought: str = Field(
        description='A description of the single action you\'re taking this turn. Restrict to the following actions: "Click", "Type", "Scroll up", "Scroll down", "Go back", "Clarify", "Navigate" and "Select". E.g. Type restaurant name in the search box; Click on "complete reservation" button; Navigate to "https://www.opentable.com", etc.'
    )
    action: str = Field(description="One Action type you choose.")
    label: Optional[int] = Field(
        description="The Numerical Label corresponding to the Web Element that requires interaction."
    )
    content: Optional[str] = Field(
        description="The string to type, or ask user, or answer, or URL string to navigate.",
        default="",
    )
    selectLabel: Optional[str] = Field(
        description="The label string of the target select option. Return -1 if this doesn't apply.",
        default="",
    )
