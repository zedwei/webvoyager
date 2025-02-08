import os
from openai import OpenAI
import base64
from colorama import Fore
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
TASK = "book a table at a steakhouse restaurant for 3 people on 1/28 9pm"

class Interpreter:

    def __init__(self, folder, prompt_file = "./src/webtrajectory/interpretor_prompt.md"):
        self.folder = folder
        self.schema = {
            "type": "object",
            "properties": {
                "thought": {"type": "string"},
                "request_name": {"type": "string"},
                "request_category": {"type": "string"},
                "request_category_search": {"type": "string"},
                "request_date": {"type": "string"},
                "request_time": {"type": "string"},
                "request_count": {"type": "string"},
                "status_name": {"type": "string"},
                "status_date": {"type": "string"},
                "status_time": {"type": "string"},
                "status_count": {"type": "string"},
                "list_name": {"type": "array"},
                "list_time": {"type": "array"},
                "webpage_category": {"type": "string"},
                "user_request": {"type": "string"},
                "webpage_state": {"type": "string"},
                "agent_action": {"type": "string"},
                "webpage_state_after_action": {"type": "string"}
            },        
        }
        self.prompt_file = prompt_file

    def load_based64_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
        
    def load_prompt(self):
        """Load the prompt from the specified file."""
        with open(self.prompt_file, "r") as file:
            return file.read()

    def interpret(self, img_before, img_after, task):
        prompt_template = self.load_prompt()
        prompt = prompt_template.replace("{schema}", json.dumps(self.schema, indent=4))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"{prompt}",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"[User's task]: {task}",
                        },
                        {
                            "type": "text",
                            "text": "[Here is the screeshot before the user action]:",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_before}"},
                        },
                        {
                            "type": "text",
                            "text": "[Here is the screeshot after the user action]:",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_after}"},
                        },
                    ],
                },
            ]
            #temperature=0.2
        )
        
        '''
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""You're tasked to observe the "User's task", "Screenshots" and "User's action" to generate JSON output following this JSON schema:
                                {json.dumps(self.schema, indent=4)}
                                Use the following instructions to generate the content for the JSON output:
                                1. Extract the restaurant booking parameters from the "User's task" and "Screenshot before the user action".
                                ### Parameters to extract:
                                 **Restaurant Name** (User input)
                                 **Restaurant Category** (User input)
                                 **Restaurant Category Search** (User input)
                                  - Please note that if user has **explicitly** expressed the intent in the "User's task" to perform a restaurant category search on OpenTable.com, 
                                  set **Restaurant Category Search** to 'True'. If user has **explicitly** expressed the intent in the "User's task" **not** to perform a restaurant category search on OpenTable.com,
                                  set **Restaurant Category Search** to 'False'. Otherwise, flag it as 'None' because it's ambiguous. Do not assume or hallucinate the user's intent.
                                 **Date** (User input)
                                 **Time** (User input)
                                 **Party Size** (User input)
                                 **Restaurant Name** (Web Page)
                                 **Restaurant Category** (Web Page)
                                 **Date** (Web Page)
                                 **Time** (Web Page)
                                 **Party Size** (Web Page)
                                 **Web Page Category** (Web Page)
                                  - Values: Homepage, Search result page, Detail page, Booking page
                                 **List of Restaurant Names** (Web Page)
                                  - If the web page is a Search result page, extract the list of all restaurant names displayed on the page.
                                 **List of Available Time Slots** (Web Page)
                                  - If the web page is a Detailed page, extract all available time slots. On an OpenTable.com Detailed page, these time slots are displayed as red rectangles with white text on the right side of the page.
                                2. Summarize the user's request from the "User's task" section.
                                  - Capture all essential details in a concise and clear manner, summarize what are specified and what are missing in terms of restaurant name, restaurant category, date, time, and party size, ensuring that the most recent verification code, if provided, is accurately included.
                                3. What's the webpage status before user's action.
                                4. What action the user took.
                                5. What's the webpage status after user's action.

                                Please also try to reason about the user's intention.
                                
                                You're given two screenshots before and after the action. 
                                There is annotation on the before screenshot regarding which element the user interacted with.
                                You're also given the task that user is trying to achieve. Please refer to it when you reason about user's intention
                                
                                ### For the "user's task":
                                - Understand natural language instructions and extract relevant details.
                                - If any parameters are missing, flag them as 'Not Specified.'
                                - Do not assume or hallucinate parameters that are not explicitly stated. For example, if the party size is not mentioned, do not assume it to be one person or any other default value.

                                ### For the "Screenshot before the user action":
                                - Identify key details displayed on the page, focusing on date, time, party size, restaurant name, and page category.
                                - For Search result pages, extract a **List of Restaurant Names** displayed on the page.
                                - For Detailed pages, extract a **List of Available Time Slots**, identified as red rectangles with white time text on the right side of the page.
                                - Assign the "Web Page Category" based on the structure and content of the web page, as well as the information in the current URL. Analyze the URL to infer the page type, considering common patterns like '/search', '/details', or '/booking' for guidance. Choose one of the following values: Homepage, Search result page, Detailed page, Booking page.
                                - Do not extract parameters from the web page URL as it may reflect outdated or incorrect information.
                                - Prioritize information explicitly visible or highlighted.
                                - Identify key details displayed on the page, focusing on date, time, party size, restaurant name, and page category.

                                ### Web Page Category for OpenTable.com URLs:
                                - When analyzing web pages from OpenTable.com, determine the category as follows:
                                - **Homepage**: The root domain (e.g., `opentable.com`). It features a horizontal list of restaurant cards displayed prominently in the middle. Avoid incorrectly tagging it as a Search result page, which typically displays a vertical list of restaurants.
                                - **Search result page**: Identified by the path `/s`, it includes a vertical list of restaurant results.Â 
                                - **Detailed page**: If a single restaurant name is explicitly listed on the page, along with a prominent image at the top and accompanying reviews.
                                - **Booking page**: If the path contains `/booking/` and the page content prompts the user to input contact information and includes a button to "complete reservation."
                                                                
                                """,
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
            temperature=0.2
        )
        '''

        #print(f"{Fore.MAGENTA}{response.model_dump_json}")
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
            #task = trajectory["task"]
            task = TASK
            response = self.interpret(img_before, img_after, task)
            with open(os.path.join(self.folder, "trajectory.txt"), "a") as output_file:
                output_file.write(f"Step {step}; User's task: {task}:\n")
                output_file.write(response + "\n\n")
                step += 1
