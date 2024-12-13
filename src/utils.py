from os import system
from interfaces import AgentState, ActionResponse
from langgraph.graph import END
from langchain_core.messages import SystemMessage
from colorama import Fore
import constants

def format_descriptions(state):
    labels = []
    for i, bbox in enumerate(state["bboxes"]):
        text = bbox.get("ariaLabel") or ""
        if not text.strip():
            text = bbox["text"]
        el_type = bbox.get("type")
        labels.append(f'{i} (<{el_type}/>): "{text}"')
    bbox_descriptions = "\nValid Bounding Boxes:\n" + "\n".join(labels)

    page = state["browser"].pages[-1]
    url = f"Current URL: {page.url}"

    return {**state, "bbox_descriptions": bbox_descriptions, "current_url": url}

def print_status(name, current, requested):
    print(f"{Fore.WHITE}{name}: {Fore.YELLOW}{current}{Fore.WHITE}|{Fore.GREEN}{requested}")

def parse(response: ActionResponse) -> dict:
    system('cls')
    
    print(Fore.WHITE + "User query:")
    print(Fore.YELLOW + constants.USER_QUERY)
    print()
    
    print(Fore.WHITE + "Agent thoughts:")
    print(Fore.CYAN + response.thought)
    print()
    
    print(Fore.WHITE + "Action: " + Fore.GREEN + f"{response.action}")
    print(Fore.WHITE + "UI Element: " + Fore.GREEN + f"{response.label}")
    print(Fore.WHITE + "Content (optional): " + Fore.GREEN + f"{response.content}")
    print(Fore.WHITE + "Select label (optional): " + Fore.GREEN + f"{response.selectLabel}")

    print()
    print_status("Name", response.status["status_name"], response.status["request_name"])
    print_status("Date", response.status["status_date"], response.status["request_date"])
    print_status("Time", response.status["status_time"], response.status["request_time"])
    print_status("# of ppl", response.status["status_count"], response.status["request_count"])
    print(f"{Fore.WHITE}Matched per LLM? {Fore.GREEN if response.status["match"] else Fore.YELLOW}{response.status["match"]}")
    print()

    if not response.action:
        return {"action": "retry", "args": f"Could not parse LLM Output."}

    action = response.action
    action_input = []
    if action in ['Click', 'Type', 'ScrollUp', 'ScrollDown', 'Select']:
        action_input.append(response.label)
    
    if action in ['Type', 'ANSWER', 'Clarify', 'Navigate']:
        action_input.append(response.content)

    if action in ['Select']:
        action_input.append(response.selectLabel)

    return {"action": action, "args": action_input, "thought": response.thought}


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
        # last_line = txt.rsplit("\n", 1)[-1]
        # step = int(re.match(r"\d+", last_line).group()) + 1
        txt = txt.replace("end\"\"\"", "")
    else:
        txt = "Previous thoughts and actions taken (in order):\nText: \"\"\"\n"
        # step = 1
    scratchpad_step = state.get("step") or 0
    scratchpad_step = scratchpad_step + 1
    
    # txt += f"\n{step}. {state['observation']}"
    txt += f"\nStep {scratchpad_step}."
    txt += f"\nThought: {state['prediction']['thought']}"
    txt += f"\nAction: {state['observation']}"
    txt += f"\n"
    txt += "end\"\"\"\n"

    print(Fore.MAGENTA + txt)

    return {**state, "scratchpad": [SystemMessage(content=txt)], "step": scratchpad_step}
