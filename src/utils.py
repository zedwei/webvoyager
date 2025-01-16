from interfaces import AgentState
from colorama import Fore
from langchain_core.messages import HumanMessage
from extraction.extraction_prompt import ExtractionResponse
from interfaces import ReasoningResponse
from execution.execution_prompt import ExecutionResponse
import globals
import uuid
import os
from datetime import datetime


def select_tool(state: AgentState):
    action = state["execution"]["action"]

    if action == "retry":
        return "execution_agent"
    return action


def get_log_file_path():
    return os.path.join("logs", f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")


def log_to_file(message: str):
    log_file_path = get_log_file_path()
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    with open(log_file_path, "a") as log_file:
        log_file.write(message + "\n")


def print_key_value(key, value):
    print(f"{Fore.WHITE}{key}: {Fore.GREEN}{value}")


def print_debug(stage, response):
    print(f"{Fore.YELLOW}{stage}")
    if stage == "Extraction":
        extraction: ExtractionResponse = response
        print_key_value("Name(user)", extraction.request_name)
        print_key_value("Date(user)", extraction.request_date)
        print_key_value("Time(user)", extraction.request_time)
        print_key_value("Size(user)", extraction.request_count)

        print_key_value("Name(webpage)", extraction.status_name)
        print_key_value("Date(webpage)", extraction.status_date)
        print_key_value("Time(webpage)", extraction.status_time)
        print_key_value("Size(webpage)", extraction.status_count)

        print_key_value("Page category(webpage)", extraction.webpage_category)

        print_key_value("List of names(webpage)", extraction.list_name)
        print_key_value("List of avail time(webpage)", extraction.list_time)

        print_key_value("Summary of user input", extraction.user_request)
        print_key_value("Summary of webpage state", extraction.webpage_state)
        print_key_value("LLM thoughts", extraction.thought)

    elif stage == "Reasoning":
        reasoning: ReasoningResponse = response
        print_key_value("Action", reasoning.action)
        print_key_value("LLM thoughts", reasoning.thought)

    elif stage == "Execution":
        execution: ExecutionResponse = response
        print_key_value("Action", execution.action)
        print_key_value("Label", execution.label)
        print_key_value("Content", execution.content)
        print_key_value("Select label", execution.selectLabel)
        print_key_value("LLM thoughts", execution.thought)

        print()
    else:
        print(f"{Fore.WHITE}{response.model_dump_json()}")


async def update_scratchpad(state: AgentState):
    scratchpad = state.get("scratchpad")
    if scratchpad:
        txt = scratchpad[0].content
    else:
        txt = f"[User Request]\n{globals.USER_QUERY}\n"

    if state["execution"]["action"].lower() == "clarify":

        # Aggregate all user inputs and ground LLM
        # TODO: error handling if args array is  ill-formated
        ask_args = state["execution"]["args"]
        if ask_args and len(ask_args) >= 2:
            question = ask_args[0]
            answer = ask_args[-1]
            txt = txt + f"\nClarification question: {question}\n"
            txt = txt + f"Answer: {answer}\n"

    browser = state["browser"]
    execution: ExecutionResponse = state["execution"]
    await browser.inner_dialog(execution.thought, execution.action)

    return {**state, "scratchpad": [HumanMessage(content=txt)]}


def gen_id():
    # return str(uuid.uuid4())
    return "df1e4077-59c6-4b8a-9e1f-f45b3e68f54e"  # hardcode id for testing purpose


def log_message(message: str, color: str = Fore.RESET):
    log_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}"
    print(color + log_msg)
    log_to_file(log_msg)
