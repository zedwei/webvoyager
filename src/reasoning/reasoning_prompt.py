from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from globals import GLOBAL_PROMPT_TEMPLATE
from interfaces import AgentState


def retrieve_prompt(page_category: str):
    if page_category and "home".casefold() in page_category.casefold():
        return PromptTemplate.from_file(f"./src/reasoning/opentable/homepage_prompt.md")
    elif page_category and "search".casefold() in page_category.casefold():
        return PromptTemplate.from_file(f"./src/reasoning/opentable/search_prompt.md")
    elif page_category and "detail".casefold() in page_category.casefold():
        return PromptTemplate.from_file(f"./src/reasoning/opentable/detailed_prompt.md")
    elif page_category and "booking".casefold() in page_category.casefold():
        return PromptTemplate.from_file(f"./src/reasoning/opentable/booking_prompt.md")
    else:
        return PromptTemplate.from_file(f"./src/reasoning/reasoning_prompt_system.md")


# Dynamic prompt template
def prompt(state: AgentState):
    page_category = state["extraction"].webpage_category
    system_prompt = retrieve_prompt(page_category)
    return ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate(
                prompt=[
                    system_prompt,
                ],
            ),
            GLOBAL_PROMPT_TEMPLATE,
            # System template to include reasoning trajectory
            SystemMessagePromptTemplate(
                prompt=[
                    PromptTemplate.from_file(
                        f"./src/reasoning/reasoning_trajectory.md"
                    )
                ]
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
            HumanMessagePromptTemplate(
                prompt=[
                    PromptTemplate.from_file(
                        f"./src/reasoning/reasoning_prompt_human.md"
                    ),
                ],
            ),
        ],
        input_variables=[
            "request_name",
            "request_category",
            "request_category_search",
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
            "current_url",
            "img",
            "current_url",
            "reasoning_trajectory_str",
        ],
    )
