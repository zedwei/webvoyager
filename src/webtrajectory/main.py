from client import Client
from interpretor import Interpreter
import asyncio

# MODE = 0 # Recording
MODE = 1  # Interpreting
FOLDER = "./data/2025-01-24_15-56-16"

TASK = "book a table for 3 people on 1/28 9pm"

async def main():
    if MODE == 0:
        client = Client()
        await client.init(TASK)
        while True:
            await asyncio.sleep(1)
    elif MODE == 1:
        interpreter = Interpreter(FOLDER)
        interpreter.run()


if __name__ == "__main__":
    asyncio.run(main())
