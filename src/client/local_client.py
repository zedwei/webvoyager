from playwright.async_api import async_playwright
from client.client import Client, ClientMode
from agent import Agent
import globals
import platform
import time
import os
from colorama import Fore
from PIL import Image
from io import BytesIO


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

        ### For the purpose of quickly testing the actions. Keep it for now. ###
        # await self.test_select()

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
        image_byte = await self.context.pages[-1].screenshot()
        if globals.USE_HALF_RESOLUTION_SCREENSHOT:
            # Half resolution
            image = Image.open(BytesIO(image_byte))
            new_size = (int(image.width * 0.5), int(image.height * 0.5))
            resized_image = image.resize(new_size)
            output = BytesIO()
            resized_image.save(output, format=image.format)
            image_byte = output.getvalue()

        return image_byte

    async def url(self):
        return self.context.pages[-1].url

    async def keypress(self, key):
        await self.context.pages[-1].keyboard.press(key)
        time.sleep(0.2)

    async def inner_dialog(self, thoughts, action):
        return await super().inner_dialog(thoughts, action)

    """
    The following code is for the purpose of testing the actions. Keep them for now.
    """
    async def test_select(self):
        await self.navigate("https://www.opentable.com/r/wild-ginger-bellevue?corrid=61c9eade-d6c3-41d2-a29e-97510792f1ef&p=2&sd=2025-02-13T01%3A15%3A00")
        #await self.navigate("https://www.opentable.com/")
        await self.select_for_test("Party size selector", 3)

    async def select_for_test(self, aria_label, value):
        #element = await self.context.pages[-1].evaluate("document.querySelector('select[aria-label=\"Party size selector\"]')")
        #print(f"{Fore.RED}Element found: {element}")
        #hidden = await self.context.pages[-1].evaluate(
        #    "window.getComputedStyle(document.querySelector('select[aria-label=\"Party size selector\"]')).display"
        #)
        #print(f"{Fore.RED}Element display style: {hidden}")
        #is_attached = await self.context.pages[-1].evaluate(
        #    "document.querySelector('select[aria-label=\"Party size selector\"]') !== null"
        #)
        #print(f"{Fore.RED}Element attached in JavaScript: {is_attached}")

        elements = await self.context.pages[-1].locator("select[aria-label='Party size selector']").all()
        print(f"Number of matching elements: {len(elements)}")

        for element in elements:
            if await element.is_visible():
                await element.click()
        #                        
                # Get the bounding box of the clicked element
                #bbox = await element.bounding_box()
                #print(f"Bounding Box: {bbox}")

                break

        #await self.click(938, 465)
        # Send ArrowDown and Enter via AppleScript
        script = """
        osascript -e 'tell application "System Events" to key code 125'  # Arrow Down
        osascript -e 'tell application "System Events" to key code 36'   # Enter
        """

        os.system(script)


        #await self.context.pages[-1].keyboard.press("ArrowDown")
        #await self.context.pages[-1].keyboard.press("ArrowDown")
                
        #visible_elements = await self.context.pages[-1].locator("*").all_text_contents()
        #await self.context.pages[-1].locator("div", has_text="3 people").click()

        #print(f"Visible elements after dropdown click: {visible_elements}")
       
        #if bbox:
        #    print(f"Dropdown Bounding Box: {bbox}")
        #    x = bbox["x"] + bbox["width"] / 2  # Click center horizontally
        #    option_height = 30  # Estimated height per option
        #    y = bbox["y"] + bbox["height"] + (option_height * 2)  # Click the third option

            # Click at the computed coordinates
        #    await self.context.pages[-1].mouse.click(x, y)

        #await self.context.pages[-1].select_option("select[aria-label='Party size selector']", "3")
        

        #await self.context.pages[-1].wait_for_selector("select[aria-label='Party size selector']", state="attached", timeout=5000)
        #await self.context.pages[-1].click("select[aria-label='Party size selector']", force=True)
        #await self.context.pages[-1].wait_for_timeout(1000)  # Let UI update
        #await self.context.pages[-1].select_option("select[aria-label='Party size selector']", "3")
        
        #for frame in self.context.pages[-1].frames:
        #    select_exists = await frame.evaluate(
        #        "document.querySelector('select[aria-label=\"Party size selector\"]') !== null"
        #    )
        #    print(f"{Fore.WHITE}Frame URL: {frame.url} | Contains dropdown: {Fore.GREEN}{select_exists}")
        
        #is_attached = await self.context.pages[-1].locator("select[aria-label='Party size selector']").is_attached()
        #print(f"{Fore.RED}Element is attached: {is_attached}")
        
        #is_visible = await self.context.pages[-1].locator("select[aria-label='Party size selector']").is_visible()
        #print(f"{Fore.RED}Is the dropdown visible? {is_visible}")

        #await self.context.pages[-1].locator("select[aria-label='Party size selector']").scroll_into_view_if_needed()
        #await self.context.pages[-1].wait_for_timeout(1000)  # Small delay to allow rendering

        # Wait for the dropdown to be available
        # await self.context.pages[-1].wait_for_selector(f"select[aria-label='{aria_label}']")
        
        # Get all options inside the select dropdown
        #options = await page.locator(f"select[aria-label='{aria_label}'] option").all()

        # Iterate over options to find the matching text
        #for option in options:
        #    text = option.evaluate("node => node.innerText").strip()  # Get visible text
        #    option_value = option.get_attribute("value")  # Get corresponding value
        #    if text == value:
        #        break
        
        # Select the option
        #await self.context.pages[-1].select_option(f"select[aria-label='{aria_label}']", f"{value}")