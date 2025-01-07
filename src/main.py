import asyncio
import os
from getpass import getpass
from agent import Agent
from colorama import init as initColorma, Fore
import globals
from client.local_client import LocalClient

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
    print(Fore.YELLOW + "Initiating browser and starting agent...")

    # Initialization
    init()
    agent = Agent()
    client = LocalClient()
    await client.init()
    
    # Wait for user input
    await client.user_input()

    # Navigate to OpenTable.com as starting point
    await client.navigate("https://www.opentable.com")

    # Start Agent loop
    await agent.call_agent(globals.USER_QUERY, client.context)


if __name__ == "__main__":
    asyncio.run(main())
