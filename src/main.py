import asyncio
import os
import sys
import websockets
from getpass import getpass
from colorama import init as initColorma, Fore
from client.local_client import LocalClient
from client.websocket_client import WebSocketClient
import traceback


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
        print(Fore.RED + "Error in handling client")
        traceback.print_exc()
    finally:
        print(Fore.RED + "Client disconnected")
        connected_clients.remove(websocket)


async def main():
    if len(sys.argv) > 1:
        async with websockets.serve(handle_client, "localhost", 8765):
            await asyncio.Future()
        client = WebSocketClient(int(sys.argv[1]))
    else:
        client = LocalClient()

    print(Fore.YELLOW + "Initiating browser and starting agent...")
    init()

    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
