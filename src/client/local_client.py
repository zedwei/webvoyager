from playwright.async_api import async_playwright
from client.client import Client, ClientMode
from agent import Agent
import globals
import platform
import time
from colorama import Fore


class LocalClient(Client):
    def __init__(self):
        self.mode = ClientMode.LOCAL

    async def run(self):
        browser = await async_playwright().start()

        # By default the agent will operate on a private window of the default profile
        browser = await browser.chromium.launch(
            channel="msedge", headless=False, args=["--window-position=0,0"]
        )
        self.context = await browser.new_context(
            viewport={"width": 1280, "height": 1080}
        )
        await self.context.new_page()

        # This is used to point to a specific signedin user folder
        # self.context = await browser.chromium.launch_persistent_context(
        #     channel="msedge",
        #     headless=False,
        #     user_data_dir=fr"C:\Users\ranwei\AppData\Local\Microsoft\Edge\User Data",
        #     args=[fr"--profile-directory=Profile 2", "--window-position=0,0"],
        #     viewport={"width": 1280, "height": 1080}
        # )

        # Wait for user input
        await self.user_query()

        # Navigate to OpenTable.com as starting point
        await self.navigate("https://www.opentable.com")

        # Start Agent loop
        agent = Agent()
        await agent.call_agent(globals.USER_QUERY, self)

    async def user_query(self):
        # Input query
        if not globals.USER_QUERY:
            print(Fore.WHITE + "Please input your query: " + Fore.YELLOW)
            globals.USER_QUERY = input()
        print()

    async def navigate(self, url):
        await self.context.pages[-1].goto(url)

    async def click(self, x, y):
        await self.context.pages[-1].mouse.click(x, y)

    async def run_js(self, script):
        try:
            response = await self.context.pages[-1].evaluate(script)
        except:
            print(Fore.RED + "Error in executing JavaScript.")
            response = None
        return response

    async def type(self, x, y, text):
        page = self.context.pages[-1]
        await page.mouse.click(x, y)
        time.sleep(1)
        select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
        await page.keyboard.press(select_all)
        await page.keyboard.press("Backspace")
        await page.keyboard.type(text)
        time.sleep(2)
        await page.keyboard.press("Enter")

    async def scroll(self, offset):
        await self.run_js(f"window.scrollBy(0, {offset})")

    async def go_back(self):
        page = self.context.pages[-1]
        await page.go_back()

    async def search(self):
        page = self.context.pages[-1]
        await page.goto("https://www.bing.com")

    async def user_clarify(self, question):
        print(Fore.WHITE + "Please type your answer to this question:")
        print(Fore.YELLOW + f"Question: {question}" + Fore.GREEN)
        user_input = input()
        return user_input

    async def screenshot(self):
        return await self.context.pages[-1].screenshot()

    async def url(self):
        return self.context.pages[-1].url
    
    async def keypress(self, key):
        await self.context.pages[-1].keyboard.press(key)
        time.sleep(0.2)
