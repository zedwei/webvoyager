from playwright.async_api import async_playwright
from client.client import Client, ClientMode
import globals
import platform
import time
from colorama import Fore


class LocalClient(Client):
    def __init__(self):
        self.mode = ClientMode.LOCAL

    async def init(self):
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

        return await super().init()

    async def user_query(self):
        # Input query
        if not globals.USER_QUERY:
            print(Fore.WHITE + "Please input your query: " + Fore.YELLOW)
            globals.USER_QUERY = input()
        print()
        return await super().user_query()

    async def navigate(self, url):
        await self.context.pages[-1].goto(url)
        return await super().navigate()

    async def click(self, x, y):
        await self.context.pages[-1].mouse.click(x, y)
        return await super().click(x, y)

    async def run_js(self, script):
        try:
            response = await self.context.pages[-1].evaluate(script)
        except:
            print(Fore.RED + "Error in executing JavaScript.")
            response = None
        return response

    async def type(self, text):
        page = self.context.pages[-1]
        select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
        await page.keyboard.press(select_all)
        await page.keyboard.press("Backspace")
        await page.keyboard.type(text)
        time.sleep(2)
        await page.keyboard.press("Enter")
        return await super().type(text)

    async def keypress(self, key):
        await self.context.pages[-1].keyboard.press(key)
        time.sleep(0.2)
        return await super().keypress(key)

    async def scroll(self, offset):
        await self.run_js(f"window.scrollBy(0, {offset})")
        return await super().scroll(offset)

    async def go_back(self):
        page = self.context.pages[-1]
        await page.go_back()
        return await super().go_back()

    async def navigate(self, url):
        page = self.context.pages[-1]
        await page.goto(url)
        return await super().navigate(url)

    async def search(self):
        page = self.context.pages[-1]
        await page.goto("https://www.bing.com")
        return await super().search()

    async def user_clarify(self, question):
        print(Fore.WHITE + "Please type your answer to this question:")
        print(Fore.YELLOW + f"Question: {question}" + Fore.GREEN)
        user_input = input()
        return user_input

    async def screenshot(self):
        return await self.context.pages[-1].screenshot()

    async def url(self):
        return self.context.pages[-1].url
