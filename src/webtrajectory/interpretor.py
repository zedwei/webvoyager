import os
from openai import OpenAI
import base64
from colorama import Fore
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class Interpreter:

    def __init__(self, folder):
        self.folder = folder

    def load_based64_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def interpret(self, img_before, img_after, task):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You're tasked to observe a user action in web browser and describe: 
                                1. What's the webpage status before user's action.
                                2. What action the user took.
                                3. What's the webpage status after user's action.

                                Please also try to reason about the user's intention.
                                
                                You're given two screenshots before and after the action. 
                                There is annotation on the before screenshot regarding which element the user interacted with.
                                You're also given the task that user is trying to achieve. Please refer to it when you reason about user's intention""",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"User's task: {task}",
                        },
                        {
                            "type": "text",
                            "text": "Here is the screeshot before the user action.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_before}"},
                        },
                        {
                            "type": "text",
                            "text": "Here is the screeshot after the user action.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_after}"},
                        },
                    ],
                },
            ],
        )

        print(f"{Fore.MAGENTA}{response.model_dump_json}")
        response_json = response.to_dict()
        print(f"{Fore.YELLOW}{response_json["choices"][0]["message"]["content"]}")
        return response_json["choices"][0]["message"]["content"]

    def run(self):
        trajectory_file = os.path.join(self.folder, "trajectory.json")

        trajectory_txt_path = os.path.join(self.folder, "trajectory.txt")
        if os.path.exists(trajectory_txt_path):
            os.remove(trajectory_txt_path)

        with open(trajectory_file, "r") as file:
            trajectory_data = json.load(file)

        step = 0
        for trajectory in trajectory_data:
            img_before = self.load_based64_image(trajectory["before_annotated"])
            img_after = self.load_based64_image(trajectory["after"])
            task = trajectory["task"]
            response = self.interpret(img_before, img_after, task)
            with open(os.path.join(self.folder, "trajectory.txt"), "a") as output_file:
                output_file.write(f"Step {step}:\n")
                output_file.write(response + "\n\n")
                step += 1
