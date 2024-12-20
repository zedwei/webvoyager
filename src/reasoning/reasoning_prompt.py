from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from globals import GLOBAL_PROMPT_TEMPLATE

# Prompt template
reasoning_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate(
            prompt=[
                PromptTemplate.from_file(f"./src/reasoning/reasoning_prompt_system.md"),
            ],
        ),
        GLOBAL_PROMPT_TEMPLATE,
        HumanMessagePromptTemplate(
            prompt=[
                PromptTemplate.from_file(
                    f"./src/reasoning/reasoning_prompt_human.md",
                    input_variables=[
                        "request_name",
                        "request_date",
                        "request_time",
                        "request_count",
                        "status_name",
                        "status_date",
                        "status_time",
                        "status_count",
                        "webpage_category",
                        "list_name",
                        "list_time",
                    ],
                ),
            ],
        ),
    ],
    input_variables=[
        "request_name",
        "request_date",
        "request_time",
        "request_count",
        "status_name",
        "status_date",
        "status_time",
        "status_count",
        "webpage_category",
        "list_name",
        "list_time",
    ],
)


# Output Pydantic
class ReasoningResponse(BaseModel):
    thought: str = Field(
        description="A brief reasoning explaining why this action was chosen."
    )
    action: str = Field(description="A concrete description of the action to take.")
