import asyncio
import base64
import time
from langchain_core.runnables import chain as chain_decorator

# Some javascript we will run on each step
# to take a screenshot of the page, select the
# elements to annotate, and add bounding boxes
with open("./src/mark_page.js") as f:
    mark_page_script = f.read()


@chain_decorator
async def mark_page(page):
    await page.evaluate(mark_page_script)
    for _ in range(10):
        try:
            bboxes = await page.evaluate("markPage()")
            break
        except Exception:
            # May be loading...
            asyncio.sleep(3)
    screenshot = await page.screenshot()

    # Ensure the bboxes don't follow us around
    # RANWEI: Keep bounding box for debugging purpose
    await page.evaluate("unmarkPage()")
    return {
        "img": base64.b64encode(screenshot).decode(),
        "bboxes": bboxes,
    }


async def mark_rect_once(page, index):
    await page.evaluate(f"markRect({index})")
    time.sleep(3)
    await page.evaluate("unmarkPage()")


async def annotate(state):
    time.sleep(2)
    marked_page = await mark_page.with_retry().ainvoke(state["page"])
    return {**state, **marked_page}
