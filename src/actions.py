# %%
import asyncio
import platform
import time
from agent import AgentState
from mark_page import mark_rect_once
from colorama import Fore


async def click(state: AgentState):
    # - Click [Numerical_Label]
    # page = state["page"]
    page = state["browser"].pages[-1]
    click_args = state["prediction"]["args"]
    if click_args is None or len(click_args) != 1:
        return f"Failed to click bounding box labeled as number {click_args}"
    bbox_id = click_args[0]
    bbox_id = int(bbox_id)
    try:
        bbox = state["bboxes"][bbox_id]
    except Exception:
        return f"Error: no bbox for : {bbox_id}"
    x, y = bbox["x"], bbox["y"]

    await mark_rect_once(page, bbox_id)

    await page.mouse.click(x, y)
    # TODO: In the paper, they automatically parse any downloaded PDFs
    # We could add something similar here as well and generally
    # improve response format.
    return f"Clicked {bbox_id}: {bbox["text"] or bbox["ariaLabel"]}"


async def type_text(state: AgentState):
    # page = state["page"]
    page = state["browser"].pages[-1]
    type_args = state["prediction"]["args"]
    if type_args is None or len(type_args) != 2:
        return f"Failed to type in element from bounding box labeled as number {
            type_args}"
    bbox_id = type_args[0]
    bbox_id = int(bbox_id)
    bbox = state["bboxes"][bbox_id]
    x, y = bbox["x"], bbox["y"]
    text_content = type_args[1]
    await mark_rect_once(page, bbox_id)
    await page.mouse.click(x, y)
    # Check if MacOS
    select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
    await page.keyboard.press(select_all)
    await page.keyboard.press("Backspace")
    await page.keyboard.type(text_content)
    time.sleep(2)
    await page.keyboard.press("Enter")
    return f"Typed {text_content} and submitted"


async def scroll(state: AgentState):
    # page = state["page"]
    page = state["browser"].pages[-1]
    scroll_args = state["prediction"]["args"]
    if scroll_args is None or len(scroll_args) != 1:
        return "Failed to scroll due to incorrect arguments."

    bbox_id = scroll_args[0]
    bbox_id = int(bbox_id)
    direction = "up" if state["prediction"]["action"].lower() == "scrollup" else "down"

    if bbox_id == -1:
        # Not sure the best value for this:
        scroll_amount = 500
        scroll_direction = (
            -scroll_amount if direction.lower() == "up" else scroll_amount
        )
        await page.evaluate(f"window.scrollBy(0, {scroll_direction})")
    else:
        # Scrolling within a specific element
        scroll_amount = 200
        bbox = state["bboxes"][bbox_id]
        x, y = bbox["x"], bbox["y"]
        scroll_direction = (
            -scroll_amount if direction.lower() == "up" else scroll_amount
        )
        await page.mouse.move(x, y)
        await page.mouse.wheel(0, scroll_direction)

    return f"Scrolled {direction} in {'window' if bbox_id == -1 else 'element'}"


async def wait(state: AgentState):
    sleep_time = 5
    await asyncio.sleep(sleep_time)
    return f"Waited for {sleep_time}s."


async def go_back(state: AgentState):
    # page = state["page"]
    page = state["browser"].pages[-1]
    await page.go_back()
    return f"Navigated back a page to {page.url}."


async def navigate(state: AgentState):
    page = state["browser"].pages[-1]
    navigate_args = state["prediction"]["args"]
    if navigate_args is None or len(navigate_args) < 1:
        return "Failed to scroll due to incorrect arguments."
    url = navigate_args[0]
    try:
        await page.goto(url)
    except:
        return f"Failed to navigate to {url}."

    return f"Navigated to {url}"


async def to_search(state: AgentState):
    # page = state["page"]
    page = state["browser"].pages[-1]
    # await page.goto("https://www.google.com/")
    # return "Navigated to google.com."
    await page.goto("https://www.bing.com/")
    return "Navigated to bing.com."


async def human_signin(state: AgentState):
    user_input = input(
        "Please manually sign-in to continue the flow. Press Enter once it's signed in."
    )
    return "User manually signed in."


async def ask(state: AgentState):
    ask_args = state["prediction"]["args"]
    if ask_args is None or len(ask_args) < 1:
        return f"Failed to ask question to user."

    print(Fore.WHITE + "Please type your answer to this question:")
    print(Fore.YELLOW + f"Question: {ask_args[0]}" + Fore.GREEN)
    user_input = input()
    
    # Append user input to ask_args so it can be used in scratchpad update
    ask_args.append(user_input) 
    return f'Question: "{ask_args[0]}"  Answer from user: "{user_input}"'


async def select(state: AgentState):
    try:
        page = state["browser"].pages[-1]
        select_args = state["prediction"]["args"]
        if select_args is None or len(select_args) < 2:
            return (
                f"The Numerical_Label or target label to select is missing in the response."
            )

        bbox_id = select_args[0]
        bbox_id = int(bbox_id)
        value = select_args[1]

        bbox = state["bboxes"][bbox_id]
        x, y = bbox["x"], bbox["y"]

        offset = await page.evaluate(f'getSelectOffset({bbox_id}, "{value}")')
        
        # Start interacting with browser
        # Step 1: Expand the selection list
        await page.mouse.click(x, y)
        time.sleep(2)

        # Step 2: Press Up or Down keyboard to select the target value
        for _ in range(abs(offset)):
            await page.keyboard.press("ArrowDown" if offset > 0 else "ArrowUp")
            time.sleep(0.2)

        # Step 3: Press Enter to confirm selection
        await page.keyboard.press("Enter")
    except:
        return f"Failed to select the target item in the dropdown list. Try clicking the target instead."
    else:
        return f"Selected the target item in the dropdown list."

