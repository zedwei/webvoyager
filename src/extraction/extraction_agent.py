from langchain_core.messages import HumanMessage
import globals
from interfaces import AgentState
from mark_page import screenshot
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from extraction.extraction_prompt import extraction_prompt, ExtractionResponse
from utils import print_debug


async def pre_process(state: AgentState):
    scratchpad = state["scratchpad"]
    if not scratchpad:
        scratchpad = [HumanMessage(content=f"[User Request]\n{globals.USER_QUERY}\n")]

    browser = state["browser"]
    url = await browser.url()

    return {
        **state,
        "current_url": url,
        "scratchpad": scratchpad,
    }


def post_process(response: ExtractionResponse):
    print_debug("Extraction", response)
    return response

"""
The pipeline output of the extraction_agent is the following dictionary:
{**AgentState,
 extraction: response which is which is a dictionary of the extraction results of the type ExtractionResponse
}
"""
def extraction_agent():
    llm = ChatOpenAI(model=globals.OPENAI_EXTRACTION_MODEL, max_tokens=16384)
    llm = llm.with_structured_output(ExtractionResponse).with_retry(
        stop_after_attempt=3
    )

    return screenshot | RunnablePassthrough.assign(
        extraction=pre_process | extraction_prompt | llm | post_process
    )
