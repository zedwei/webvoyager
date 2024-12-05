import re
from os import system
from interfaces import AgentState, ActionResponse
from langgraph.graph import END
from langchain_core.messages import SystemMessage
from colorama import Fore
from constants import USER_QUERY

def format_descriptions(state):
    labels = []
    for i, bbox in enumerate(state["bboxes"]):
        text = bbox.get("ariaLabel") or ""
        if not text.strip():
            text = bbox["text"]
        el_type = bbox.get("type")
        labels.append(f'{i} (<{el_type}/>): "{text}"')
    bbox_descriptions = "\nValid Bounding Boxes:\n" + "\n".join(labels)
    return {**state, "bbox_descriptions": bbox_descriptions}


def parse(response: ActionResponse) -> dict:
    system('cls')
    
    print(Fore.WHITE + "User query:")
    print(Fore.YELLOW + USER_QUERY)
    print()

    print(Fore.WHITE + "Agent thoughts:")
    print(Fore.CYAN + response.thought)
    print()
    
    if not response.action:
        return {"action": "retry", "args": f"Could not parse LLM Output."}

    action = response.action
    action_input = []
    if action in ['Click', 'Type']:
        action_input.append(response.label)
    
    if action in ['Type', 'ANSWER', 'Clarify']:
        action_input.append(response.content)

    return {"action": action, "args": action_input}


def select_tool(state: AgentState):
    # Any time the agent completes, this function
    # is called to route the output to a tool or
    # to the end user.
    action = state["prediction"]["action"]

    # if action == "ANSWER":
    if "ANSWER" in action:  # Bug fix: the response is "ANSWER;"
        return END
    if action == "retry":
        return "agent"
    return action


def update_scratchpad(state: AgentState):
    """After a tool is invoked, we want to update
    the scratchpad so the agent is aware of its previous steps"""
    old = state.get("scratchpad")
    if old:
        txt = old[0].content
        last_line = txt.rsplit("\n", 1)[-1]
        step = int(re.match(r"\d+", last_line).group()) + 1
    else:
        txt = "Previous action observations:"
        step = 1
    txt += f"\n{step}. {state['observation']}"

    print(Fore.MAGENTA + txt)

    return {**state, "scratchpad": [SystemMessage(content=txt)]}
