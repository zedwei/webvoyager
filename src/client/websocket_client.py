from client.client import Client, ClientMode
from agent import Agent
import globals
import base64
import platform
import time
import websockets
import asyncio
import json
from colorama import Fore
from utils import gen_id


class WebSocketClient(Client):
    def __init__(self, port):
        self.mode = ClientMode.WEBSOCKET
        self.port = port

    async def run_server(self, websocket):
        print(Fore.GREEN + "New client connected")
        self.websocket = websocket

        # Wait for user input
        await self.user_query()

        # Navigate to OpenTable.com as starting point
        await self.navigate("https://www.opentable.com")

        # Start Agent loop
        agent = Agent()
        await agent.call_agent(globals.USER_QUERY, self)

        # async for message in websocket:
        #     print(f"Received: {message}")
        #     msg = json.loads(message)
        #     await websocket.send(f"Echo: {msg["id"]}")

    async def run(self):
        async with websockets.serve(self.run_server, "localhost", self.port):
            await asyncio.Future()

    async def receive(self, required_keys: set, correlate_id=None):
        if correlate_id:
            required_keys.add("correlate_id")

        while True:
            try:
                data_str = await self.websocket.recv()
                # print(f"{Fore.MAGENTA}Received: {data_str}")
                data = json.loads(data_str)
                if not required_keys.issubset(data.keys()):
                    print(
                        f"{Fore.RED}Required fields are missing. Some key in {required_keys} is missing in {data}"
                    )
                elif correlate_id and data["correlate_id"] != correlate_id:
                    print(
                        f"{Fore.RED}Coorelate Id doesn't match request Id. Expect: {correlate_id}, Received: {data["correlate_id"]}"
                    )
                else:
                    return data

            except:
                # TODO: inform client to retry
                print(f"{Fore.RED}JSON Parse error: {data_str}")
                pass

    async def send(self, data):
        await self.websocket.send(json.dumps(data))

    async def user_query(self):
        while not globals.USER_QUERY:
            data = await self.receive(required_keys={"id", "action", "content"})
            globals.USER_QUERY = data["content"]
            await self.send(
                {
                    "correlate_id": data["id"],
                    "action": "user_message_response",
                    "status": "succeeded",
                    "content": "",
                }
            )

    async def run_js(self, script):
        id = gen_id()
        await self.send(
            {
                "id": id,
                "action": "javascript",
                "content": f"{script}",
            }
        )
        response = await self.receive(
            required_keys={"content", "status"}, correlate_id=id
        )
        if response["status"] != "succeeded":
            print(Fore.RED + "Error in executing JavaScript.")
            return None

        try:
            response_obj = json.loads(response["content"])
            return response_obj[0]
        except:
            return None

    async def navigate(self, url):
        await self.run_js(f'window.location.href = "{url}"')

    async def screenshot(self):
        id = gen_id()
        await self.send(
            {
                "id": id,
                "action": "screenshot",
                "content": f"",
            }
        )
        response = await self.receive(required_keys={"content"}, correlate_id=id)
        image_str = response["content"]
        image_byte = base64.b64decode(image_str)

        return image_byte

    async def url(self):
        url = await self.run_js(f"window.location.href")
        return url

    async def click(self, x, y):
        # await self.run_js(
        #     "document.elementFromPoint("
        #     + str(x)
        #     + ","
        #     + str(y)
        #     + ').dispatchEvent(new MouseEvent("click", {bubbles: true, cancelable: true, clientX: '
        #     + str(x)
        #     + ", clientY: "
        #     + str(y)
        #     + ", view: window}))"
        # )

        # New implementation
        id = gen_id()
        await self.send(
            {
                "id": id,
                "action": "page.mouse.click",
                "content": "{'x': " + str(x) + ", 'y': " + str(y) + "}",
            }
        )
        await self.receive(required_keys=set(), correlate_id=id)

    async def type(self, x, y, text):
        # await self.run_js(f'document.elementFromPoint({x}, {y}).value="{text}"')

        # New implementation
        # Step 1: Click & set focus on the input box
        await self.click(x, y)
        time.sleep(1)

        # Step 2: Clear existing text
        select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
        await self.keypress(select_all)
        await self.keypress("Backspace")

        # Step 3: Input new text
        id = gen_id()
        await self.send(
            {
                "id": id,
                "action": "page.keyboard.type",
                "content": text,
            }
        )
        await self.receive(required_keys=set(), correlate_id=id)
        time.sleep(2)

        # Step 4: Press Enter
        await self.keypress("Enter")

    async def scroll(self, offset):
        await self.run_js(f"window.scrollBy(0, {offset})")

    async def go_back(self):
        await self.run_js(f"window.history.back()")

    async def search(self):
        await self.navigate("https://www.bing.com")

    async def user_clarify(self, question):
        print(Fore.YELLOW + f"Question: {question}" + Fore.GREEN)
        id = gen_id()
        await self.send(
            {
                "id": id,
                "action": "bot_message",
                "content": question,
                "request_input": True,
            }
        )

        response = await self.receive(required_keys={"content"}, correlate_id=id)
        print(Fore.GREEN + f"User's answer: {response["content"]}")

        return response["content"]

    async def keypress(self, key):
        id = gen_id()
        await self.send(
            {
                "id": id,
                "action": "page.keyboard.press",
                "content": key,
            }
        )
        await self.receive(required_keys=set(), correlate_id=id)
