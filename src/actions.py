# %%
import asyncio
import time
from agent import AgentState
from colorama import Fore


async def click(state: AgentState):
    browser = state["browser"]
    click_args = state["execution"]["args"]
    if click_args is None or len(click_args) != 1:
        return f"Failed to click bounding box labeled as number {click_args}"
    bbox_id = click_args[0]
    bbox_id = int(bbox_id)
    try:
        bbox = state["bboxes"][bbox_id]
    except Exception:
        return f"Error: no bbox for : {bbox_id}"
    x, y = bbox["x"], bbox["y"]

    # Show a rectangle around the click target for 2 secs to inform user
    await browser.run_js(f"markRect({bbox_id})")
    time.sleep(2)
    await browser.run_js(f"unmarkPage()")

    await browser.click(x, y)

    return f"Clicked {bbox_id}: {bbox["text"] or bbox["ariaLabel"]}"


async def type_text(state: AgentState):
    browser = state["browser"]
    type_args = state["execution"]["args"]
    if type_args is None or len(type_args) != 2:
        return f"Failed to type in element from bounding box labeled as number {
            type_args}"
    bbox_id = type_args[0]
    bbox_id = int(bbox_id)
    bbox = state["bboxes"][bbox_id]
    x, y = bbox["x"], bbox["y"]
    text_content = type_args[1]

    await browser.run_js(f"markRect({bbox_id})")
    time.sleep(2)
    await browser.run_js(f"unmarkPage()")

    # await browser.click(x, y)
    await browser.type(x, y, text_content)

    return f"Typed {text_content} and submitted"


async def scroll(state: AgentState):
    # page = state["page"]
    browser = state["browser"]
    scroll_args = state["execution"]["args"]
    if scroll_args is None or len(scroll_args) != 1:
        return "Failed to scroll due to incorrect arguments."

    bbox_id = scroll_args[0]
    bbox_id = int(bbox_id)
    direction = "up" if state["execution"]["action"].lower() == "scrollup" else "down"

    # TODO: missing support of scroll within an element
    scroll_amount = 500
    offset = -scroll_amount if direction.lower() == "up" else scroll_amount
    await browser.scroll(offset)

    return f"Scrolled {direction} in window"


async def wait(state: AgentState):
    sleep_time = 5
    await asyncio.sleep(sleep_time)
    return f"Waited for {sleep_time}s."


async def go_back(state: AgentState):
    browser = state["browser"]
    await browser.go_back()
    return f"Navigated back a page to {browser.pages[-1].url}."


async def navigate(state: AgentState):
    browser = state["browser"]
    navigate_args = state["execution"]["args"]
    if navigate_args is None or len(navigate_args) < 1:
        return "Failed to scroll due to incorrect arguments."
    url = navigate_args[0]
    try:
        await browser.navigate(url)
    except:
        return f"Failed to navigate to {url}."

    return f"Navigated to {url}"


async def to_search(state: AgentState):
    browser = state["browser"]
    await browser.search()
    return "Navigated to bing.com."


async def human_signin(state: AgentState):
    browser = state["browser"]
    await browser.user_clarify(
        "Please manually sign-in to continue the flow. Press Enter once it's signed in."
    )

    return "User manually signed in."


async def ask(state: AgentState):
    browser = state["browser"]

    ask_args = state["execution"]["args"]
    if ask_args is None or len(ask_args) < 1:
        return f"Failed to ask question to user."

    user_input = await browser.user_clarify(ask_args[0])

    # Append user input to ask_args so it can be used in scratchpad update
    ask_args.append(user_input)
    return (
        f'Clarification question: "{ask_args[0]}"\nAnswer from user: "{user_input}"\n'
    )


async def select(state: AgentState):
    try:
        browser = state["browser"]
        select_args = state["execution"]["args"]
        if select_args is None or len(select_args) < 2:
            return f"The Numerical_Label or target label to select is missing in the response."

        bbox_id = select_args[0]
        bbox_id = int(bbox_id)
        value = select_args[1]

        bbox = state["bboxes"][bbox_id]
        x, y = bbox["x"], bbox["y"]

        offset = await browser.run_js(f'getSelectOffset({bbox_id}, "{value}")')

        # Start interacting with browser
        # Step 1: Expand the selection list
        await browser.click(x, y)
        time.sleep(2)

        # Step 2: Press Up or Down keyboard to select the target value
        for _ in range(abs(offset)):
            await browser.keypress("ArrowDown" if offset > 0 else "ArrowUp")

        # Step 3: Press Enter to confirm selection
        await browser.keypress("Enter")
    except:
        return f"Failed to select the target item in the dropdown list. Try clicking the target instead."
    else:
        return f"Selected the target item in the dropdown list."
    
def update_observation(observation):
    return {"observation": observation}
