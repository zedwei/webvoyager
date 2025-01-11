import globals
from interfaces import AgentState, ReasoningResponse
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from execution.execution_prompt import ExecutionResponse, execution_prompt
from mark_page import annotate
from utils import print_debug


async def pre_process(state: AgentState):
    reasoning: ReasoningResponse = state["reasoning"]

    labels = []
    for i, bbox in enumerate(state["bboxes"]):
        ariaLabel = bbox.get("ariaLabel") or ""
        ariaLabel = ariaLabel.strip()
        text = bbox["text"] or ""
        el_type = bbox.get("type")
        if ariaLabel != "" or text != "":
            labels.append(f"{i} | <{el_type}> | {ariaLabel} | {text}")
    bbox_descriptions = (
        "\nValid Bounding Boxes:"
        + '\n Format: "Numerical_Label | HTML element tag | Aria Label | Text "'
        + "\n Data: \n"
        + "\n".join(labels)
    )
    browser = state["browser"]
    url = await browser.url()

    return {
        **state,
        "bbox_descriptions": bbox_descriptions,
        "task_description": reasoning.action,
        "current_url": url,
    }


def post_process(response: ExecutionResponse) -> dict:
    print_debug("Execution", response)

    if not response.action:
        return {"action": "retry", "args": f"Could not parse LLM Output."}

    action = response.action
    action_input = []
    if action in ["Click", "Type", "ScrollUp", "ScrollDown", "Select"]:
        action_input.append(response.label)

    if action in ["Type", "ANSWER", "Clarify", "Navigate"]:

        action_input.append(response.content)

    if action in ["Select"]:
        action_input.append(response.selectLabel)

    return {"action": action, "args": action_input, "thought": response.thought}


def execution_agent():
    llm = ChatOpenAI(model=globals.OPENAI_EXECUTION_MODEL, max_tokens=16384)
    llm = llm.with_structured_output(ExecutionResponse).with_retry(stop_after_attempt=3)

    return annotate | RunnablePassthrough.assign(
        execution=pre_process | execution_prompt | llm | post_process
    )
