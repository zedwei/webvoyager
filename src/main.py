import asyncio
import os

from playwright.async_api import async_playwright
# import nest_asyncio
from getpass import getpass
from agent import Agent


def _getpass(env_var: str):
    if not os.environ.get(env_var):
        os.environ[env_var] = getpass(f"{env_var}=")


async def main():
    _getpass("OPENAI_API_KEY")
    # nest_asyncio.apply()

    print("Agent started")
    agent = Agent()

    browser = await async_playwright().start()
    # # We will set headless=False so we can watch the agent navigate the web.
    browser = await browser.chromium.launch(channel="msedge", headless=False, args=None)
    # # browser = await playwright.sync_api..chromium.launch(headless=False, args=None)
    page = await browser.new_page()
    _ = await page.goto("https://www.google.com")

    # _ = await page.goto("https://www.google.com/travel/flights")

    # res = await call_agent("Could you explain the WebVoyager paper (on arxiv)?", page)
    # res = await call_agent("help me check what's the latest nvidia stock price", page)
    # res = await call_agent("help me get the latest ipad mini deals on dealsea", page)
    # res = await call_agent("help me check availability of seastar restaurant for tonight for 2 person", page)
    # res = await call_agent("Find the cost of a 2-year protection for PS4 on Amazon.", page)
    # res = await agent.call_agent("Find the non-stop one-way flight price from SEA to LAX on christmas eve from Delta airline", page)
    # res = await agent.call_agent("Find the lowest cost of a XBox series X on Amazon/bestbuy/newegg.", page)
    res = await agent.call_agent("book a table in little lamb hotpot bellevue tonight at 8pm for 3 people", page)
    print(f"Final response: {res}")

if __name__ == "__main__":
    asyncio.run(main())
