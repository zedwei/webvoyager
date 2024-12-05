import asyncio
import os

from playwright.async_api import async_playwright
from getpass import getpass
from agent import Agent


def _getpass(env_var: str):
    if not os.environ.get(env_var):
        os.environ[env_var] = getpass(f"{env_var}=")


async def main():
    _getpass("OPENAI_API_KEY")

    print("Agent started")
    agent = Agent()

    browser = await async_playwright().start()
    # # We will set headless=False so we can watch the agent navigate the web.
    # browser = await browser.chromium.launch(channel="msedge", headless=False, args=None)

    browser = await browser.chromium.launch_persistent_context(
        channel="msedge",
        headless=False,
        user_data_dir=fr"C:\Users\ranwei\AppData\Local\Microsoft\Edge\User Data",
        args=[fr"--profile-directory=Profile 2"]
    )

    page = await browser.new_page()
    _ = await page.goto("https://www.google.com")

    # _ = await page.goto("https://www.google.com/travel/flights")

    res = await agent.call_agent("book a table in little lamb hotpot bellevue tonight at 8pm for 3 people", page)
    # res = await agent.call_agent("book a table in little lamb hotpot bellevue", page)
    # res = await agent.call_agent("book a fine diner for me tonight", page)
    print(f"Final response: {res}")

if __name__ == "__main__":
    asyncio.run(main())
