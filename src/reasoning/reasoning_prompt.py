from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain.schema import AIMessage, SystemMessage
from pydantic import BaseModel, Field
from globals import GLOBAL_PROMPT_TEMPLATE, ENABLE_FEW_SHOTS, ADD_FEW_SHOT_EXAMPLES
from interfaces import AgentState
from reasoning.reasoning_few_shots import ReasoningFewShots

def retrieve_prompt(page_category: str):
    if ENABLE_FEW_SHOTS:
        return PromptTemplate.from_file(f"./src/reasoning/reasoning_few_shots.md")
    else:
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
    
    few_shot_examples = []
    if ADD_FEW_SHOT_EXAMPLES:
        few_shots = ReasoningFewShots()
        few_shots.load_few_shots()
        few_shot_prompts = few_shots.generate_few_shot_prompts()
        few_shot_responses = few_shots.generate_few_shot_responses()

        for i, (prompt_text, response_text) in enumerate(zip(few_shot_prompts, few_shot_responses), 1):
            few_shot_examples.append(
                HumanMessagePromptTemplate(
                    prompt=[PromptTemplate.from_template(
                        f"[Example {i}]\n\n"
                        f"## Example inputs:\n\n"
                        f"{prompt_text}\n\n"
                        f"## Example responses:\n\n"
                        f"{response_text}"
                    )]
                )
            )

    # Build the messages list
    messages = [
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
    ]

    # Add few-shot examples if enabled
    if ADD_FEW_SHOT_EXAMPLES:
        messages.append(
            SystemMessage(
                content="The following are examples of logical reasoning about what action to take. Learn from these examples and apply a similar approach to \"[Future User Task]\"."
            )
        )
        messages.extend(few_shot_examples)

    # Add the final human message templates
    messages.extend([
        HumanMessagePromptTemplate(
            prompt=[
                PromptTemplate.from_template("[Future User Task]\n"),
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
    ])

    return ChatPromptTemplate(
        messages=messages,
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
            "user_request",
            "webpage_state",
            "reasoning_trajectory_str"
        ],
    )
