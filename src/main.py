import asyncio
import os
import sys
from getpass import getpass
from colorama import init as initColorma, Fore
from client.local_client import LocalClient
from client.websocket_client import WebSocketClient


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


async def main():
    if len(sys.argv) > 1:
        client = WebSocketClient(int(sys.argv[1]))
    else:
        client = LocalClient()

    print(Fore.YELLOW + "Initiating browser and starting agent...")
    init()

    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
