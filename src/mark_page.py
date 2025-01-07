import asyncio
import base64
import time
from langchain_core.runnables import chain as chain_decorator
from colorama import Fore

# Some javascript we will run on each step
# to take a screenshot of the page, select the
# elements to annotate, and add bounding boxes
with open("./src/mark_page.js") as f:
    mark_page_script = f.read()


@chain_decorator
async def mark_page(browser):
    await browser.run_js(mark_page_script)
    for _ in range(10):
        try:
            bboxes = await browser.run_js("markPage()")
            break
        except Exception:
            # May be loading...
            await asyncio.sleep(3)
    screenshot = await browser.screenshot()

    # Ensure the bboxes don't follow us around
    # RANWEI: Keep bounding box for debugging purpose
    await browser.run_js("unmarkPage()")

    # print(Fore.YELLOW + f"Marked page with {len(bboxes)} bboxes.")

    return {
        "img": base64.b64encode(screenshot).decode(),
        "bboxes": bboxes,
    }


async def annotate(state):
    await asyncio.sleep(2)
    browser = state["browser"]
    marked_page = await mark_page.with_retry().ainvoke(browser)
    return {**state, **marked_page}


async def screenshot(state):
    await asyncio.sleep(2)
    browser = state["browser"]
    screenshot = await browser.screenshot()
    return {
        **state,
        "img": base64.b64encode(screenshot).decode(),
    }
