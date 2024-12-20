import globals
from interfaces import AgentState
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from extraction.extraction_prompt import ExtractionResponse
from reasoning.reasoning_prompt import reasoning_prompt, ReasoningResponse
from utils import print_debug


def pre_process(state: AgentState):
    extraction: ExtractionResponse = state["extraction"]

    return {
        **state,
        "request_name": extraction.request_name,
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
    }


def post_process(response: ReasoningResponse):
    print_debug("Reasoning", response)
    return response


def reasoning_agent():
    llm = ChatOpenAI(model=globals.OPENAI_REASONING_MODEL, max_tokens=16384)
    llm = llm.with_structured_output(ReasoningResponse).with_retry(stop_after_attempt=3)

    return pre_process | RunnablePassthrough.assign(
        reasoning=reasoning_prompt | llm | post_process
    )
