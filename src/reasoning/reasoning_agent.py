import globals
from interfaces import AgentState, ReasoningResponse, ReasoningTrajectory
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from extraction.extraction_prompt import ExtractionResponse
from reasoning.reasoning_prompt import prompt
from utils import print_debug
from mark_page import screenshot
from typing import List


def gen_trajectory_str(trajectory: List[ReasoningTrajectory]) -> str:
    return "\n\n".join(
        [
            f"Webpage: {item['state']}\n{("Action: " + item['action']) if item['action'] else ''}"
            for item in trajectory
        ]
    )


async def pre_process(state: AgentState):
    extraction: ExtractionResponse = state["extraction"]
    browser = state["browser"]
    url = await browser.url()
    state = await screenshot(state)

    # Send thoughts and action from extraction output as inner dialog to client for display
    await browser.inner_dialog(extraction.thought, extraction.user_request)

    # Append extracted state to the reasoning trajectory
    if not state.get("reasoning_trajectory"):
        state["reasoning_trajectory"] = []
    state["reasoning_trajectory"].append({"state": extraction.webpage_state, "action": None})

    # Send thoughts and action from extraction output as inner dialog to client for display
    await browser.inner_dialog(extraction.thought, extraction.user_request)

    # Append extracted state to the reasoning trajectory
    if not state.get("reasoning_trajectory"):
        state["reasoning_trajectory"] = []
    state["reasoning_trajectory"].append({"state": extraction.webpage_state, "action": None})

    return {
        **state,
        "request_name": extraction.request_name,
        "request_category": extraction.request_category,
        "request_category_search": extraction.request_category_search,
        "request_date": extraction.request_date,
        "request_time": extraction.request_time,
        "request_count": extraction.request_count,
        "status_name": extraction.status_name,
        "status_date": extraction.status_date,
        "status_time": extraction.status_time,
        "status_count": extraction.status_count,
        "webpage_category": extraction.webpage_category,
        "list_name": extraction.list_name,
        "list_time": extraction.list_time,
        "user_request": extraction.user_request,
        "current_url": url,
        "reasoning_trajectory_str": gen_trajectory_str(state["reasoning_trajectory"]),
    }


def post_process(response: ReasoningResponse):
    print_debug("Reasoning", response)

    return response


"""
The pipeline output of the extraction_agent is the following dictionary:
{**AgentState,
 "reasonging": response which is a dictionary of the extraction results of the type ReasoningResponse
}
"""
def reasoning_agent():
    llm = ChatOpenAI(model=globals.OPENAI_REASONING_MODEL, max_tokens=16384)
    llm = llm.with_structured_output(ReasoningResponse).with_retry(stop_after_attempt=3)

    return pre_process | RunnablePassthrough.assign(
        reasoning=prompt | llm | post_process
    )
