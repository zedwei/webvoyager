import asyncio
import os
from playwright.async_api import async_playwright
from getpass import getpass
from agent import Agent
from colorama import init as initColorma, Fore
import constants


def _getpass(env_var: str):
    if not os.environ.get(env_var):
        os.environ[env_var] = getpass(
            f"Please input your OpenAI API Key (first time only): "
        )


def init():
    initColorma()

    # Get OpenAI API Key
    _getpass("OPENAI_API_KEY")

    # Choose the prompt file to use
    prompt_list = os.listdir("./src/prompts")
    print(Fore.WHITE + "Choose the prompt template:")
    for prompt_idx in range(len(prompt_list)):
        print(Fore.YELLOW + f"{prompt_idx+1}. {prompt_list[prompt_idx]}")
    print(Fore.WHITE + "Select: ", end=" ")
    prompt_file = input()
    constants.PROMPT_FILENAME = prompt_list[int(prompt_file) - 1]
    print()

    # Input query
    if not constants.USER_QUERY:
        print(Fore.WHITE + "Please input your query: " + Fore.YELLOW)
        constants.USER_QUERY = input()
    print()


async def main():
    os.system("cls")
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
    res = await agent.call_agent(constants.USER_QUERY, context, page)

    print(Fore.WHITE + "Final Response:")
    print(Fore.GREEN + res)


if __name__ == "__main__":
    init()
    asyncio.run(main())
