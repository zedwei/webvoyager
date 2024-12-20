import asyncio
import os
from playwright.async_api import async_playwright
from getpass import getpass
from agent import Agent
from colorama import init as initColorma, Fore
import globals


def _getpass(env_var: str):
    if not os.environ.get(env_var):
        os.environ[env_var] = getpass(
            f"Please input your OpenAI API Key (first time only): "
        )


def init():
    initColorma()

    # Get OpenAI API Key
    _getpass("OPENAI_API_KEY")

    os.system("cls")

    # Input query
    if not globals.USER_QUERY:
        print(Fore.WHITE + "Please input your query: " + Fore.YELLOW)
        globals.USER_QUERY = input()
    print()


async def main():
    print(Fore.YELLOW + "Initiating browser and starting agent...")

    agent = Agent()
    browser = await async_playwright().start()

    # By default the agent will operate on a private window of the default profile
    browser = await browser.chromium.launch(
        channel="msedge", headless=False, args=["--window-position=0,0"]
    )
    context = await browser.new_context(viewport={"width": 1280, "height": 1080})

    # This is used to point to a specific signedin user folder
    # context = await browser.chromium.launch_persistent_context(
    #     channel="msedge",
    #     headless=False,
    #     user_data_dir=fr"C:\Users\ranwei\AppData\Local\Microsoft\Edge\User Data",
    #     args=[fr"--profile-directory=Profile 2", "--window-position=0,0"],
    #     viewport={"width": 1280, "height": 1080}
    # )

    page = await context.new_page()

    # _ = await page.goto("https://www.google.com")
    # _ = await page.goto("https://www.bing.com")
    await page.goto("https://www.opentable.com")
    # await page.goto("https://www.opentable.com/matts-rotisserie-and-oyster-lounge?originId=1e72004c-6c35-4254-aaaa-f5798c9a1706&corrid=1e72004c-6c35-4254-aaaa-f5798c9a1706&avt=eyJ2IjoyLCJtIjoxLCJwIjowLCJzIjowLCJuIjowfQ")
    # await page.goto("https://www.opentable.com/s?dateTime=2024-12-19T19%3A00%3A00&covers=2&latitude=47.6722&longitude=-122.1257&term=wild%20ginger%20&shouldUseLatLongSearch=true&originCorrelationId=0bb98f84-070c-4a67-b1ac-c9cdaae20a17&corrid=f0d11a68-64ad-4cb3-9a14-5d6a6e72ee5c&intentModifiedTerm=wild%20ginger&metroId=2&originalTerm=wild%20ginger%20&pinnedRid=39454&queryUnderstandingType=default&sortBy=web_conversion")

    await agent.call_agent(globals.USER_QUERY, context)


if __name__ == "__main__":
    init()
    asyncio.run(main())
