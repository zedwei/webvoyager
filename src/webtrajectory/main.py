from client import Client
from interpretor import Interpreter
import asyncio
from colorama import Fore
import os
from datetime import datetime

# MODE = 0 # Recording
MODE = 1  # Interpreting
FOLDER = "./data/2025-01-24_15-56-16"

DEFAULT_TASK = "book a table at wild ginger seattle for 3 people on 2/10 9pm"


def get_mode():
    mode_input = (
        input(
            f"{Fore.YELLOW}Enter mode (0 for Recording, 1 for Interpreting) [default 0]: "
        )
        or "0"
    )

    if mode_input.isdigit():
        return int(mode_input)
    else:
        print("Invalid input. Defaulting to Interpreting mode.")
        return 1


def select_data_folder():
    # List all subfolders in ./data
    data_folders = [
        f for f in os.listdir("./data") if os.path.isdir(os.path.join("./data", f))
    ]

    if not data_folders:
        print(f"{Fore.RED}No data folders found in ./data/")
        return None

    # Sort folders by creation time (newest first)
    data_folders.sort(
        key=lambda x: datetime.strptime(x, "%Y-%m-%d_%H-%M-%S"), reverse=True
    )

    # Print available folders
    print(f"{Fore.CYAN}Available data folders:")
    for i, folder in enumerate(data_folders):
        print(f"{i + 1}. {folder}")

    # Ask user to pick a folder
    folder_input = input(f"{Fore.YELLOW}Select folder number [default 1]: ") or "1"

    if (
        not folder_input.isdigit()
        or int(folder_input) < 1
        or int(folder_input) > len(data_folders)
    ):
        selected_folder = data_folders[0]
    else:
        selected_folder = data_folders[int(folder_input) - 1]

    print(f"{Fore.GREEN}Using folder: {selected_folder}")
    return os.path.join("./data", selected_folder)


async def main():

    MODE = get_mode()

    if MODE == 0:
        TASK = (
            input(f"{Fore.YELLOW}Enter task [default {DEFAULT_TASK}]: ") or DEFAULT_TASK
        )
        client = Client()
        await client.init(TASK)
        while True:
            await asyncio.sleep(1)
    elif MODE == 1:
        FOLDER = select_data_folder()
        if not FOLDER:
            return

        interpreter = Interpreter(FOLDER)
        interpreter.run()


if __name__ == "__main__":
    asyncio.run(main())
