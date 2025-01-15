import asyncio
import os
import sys
import websockets
from getpass import getpass
from colorama import init as initColorma, Fore
from client.local_client import LocalClient
from client.websocket_client import WebSocketClient
import traceback
from utils import log_message


def _getpass(env_var: str):
    if not os.environ.get(env_var):
        os.environ[env_var] = getpass(
            f"Please input your OpenAI API Key (first time only): "
        )


def init():
    initColorma()

    _getpass("OPENAI_API_KEY")

    os.system("cls")


connected_clients = set()


async def handle_client(websocket):
    connected_clients.add(websocket)
    try:
        client = WebSocketClient()
        await client.run_server(websocket)
    except Exception:
        log_message("Error in handling client", Fore.RED)
        traceback.print_exc()
    finally:
        log_message("Client disconnected", Fore.RED)
        connected_clients.remove(websocket)


async def main():
    if len(sys.argv) > 1:
        init()
        log_message("Starting server...", Fore.YELLOW)
        async with websockets.serve(handle_client, "0.0.0.0", int(sys.argv[1])):
            await asyncio.Future()
    else:
        init()
        log_message("Initiating browser and starting agent...", Fore.YELLOW)
        client = LocalClient()
        await client.run()


if __name__ == "__main__":
    asyncio.run(main())
