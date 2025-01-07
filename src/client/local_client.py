from playwright.async_api import async_playwright
from client.client import Client, ClientMode
import globals
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

    async def user_input(self):
        # Input query
        if not globals.USER_QUERY:
            print(Fore.WHITE + "Please input your query: " + Fore.YELLOW)
            globals.USER_QUERY = input()
        print()
        return await super().user_input()

    async def navigate(self, url):
        await self.context.pages[-1].goto(url)
        return await super().navigate()
