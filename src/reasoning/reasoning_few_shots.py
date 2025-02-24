import os
import platform
from colorama import Fore
import json
import re

class ReasoningFewShots:

    def __init__(self, data_folder_path = "./data"):
        self.data_folder_path = data_folder_path
        config_path = os.path.join(data_folder_path, "few-shots.txt")

        self.few_shot_file_paths = []
        try:
            with open(config_path, "r") as file:
                for line in file:
                    self.few_shot_file_paths.append(line.strip())
        except FileNotFoundError:
            print(f"Configuration file not found at {config_path}.")
            return

    def load_few_shots(self):
        self.few_shots = []
        for file_path in self.few_shot_file_paths:
            file_path = os.path.join(self.data_folder_path, file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as json_file:
                    few_shots = json.load(json_file)
                    self.few_shots += few_shots
            except FileNotFoundError:
                print(f"File not found: {file_path}")

    ############################################################################
    # This function is only needed if the few_shots are not in JSON format
    # and the problem is that the fields are hard coded, so we should avoid that
    ############################################################################
    def parse_few_shots(self, data):
        # Split based on step markers
        steps = re.split(r"={10} Interpreted LLM response for step: \d+ ={10}", data)
        steps = steps[1:]
        for step in steps:
            if not step.strip():
                continue  # Skip empty sections
            
            # Extract key fields using regex
            user_task = re.search(r"User task: (.+)", step)
            user_request = re.search(r"User request: (.+)", step)
            request_name = re.search(r"Request name: (.+)", step)
            request_category = re.search(r"Request category: (.+)", step)
            request_category_search = re.search(r"Request category search: (.+)", step)
            request_date = re.search(r"Request date: (.+)", step)
            request_time = re.search(r"Request time: (.+)", step)
            request_count = re.search(r"Request count: (.+)", step)
            status_name = re.search(r"Status name: (.+)", step)
            status_date = re.search(r"Status date: (.+)", step)
            status_time = re.search(r"Status time: (.+)", step)
            status_count = re.search(r"Status count: (.+)", step)
            
            list_name_match = re.search(r"List of names: (.+)", step)
            list_time_match = re.search(r"List of avail time: (.+)", step)
            list_name = list_name_match.group(1).split(", ") if list_name_match else []
            list_time = list_time_match.group(1).split(", ") if list_time_match else []

            webpage_url = re.search(r"Webpage URL: (.+)", step)
            webpage_category = re.search(r"Webpage category: (.+)", step)
            webpage_state = re.search(r"Webpage state: (.+)", step)
            thought = re.search(r"Thought: (.+)", step)
            action = re.search(r"Agent action: (.+)", step)
            webpage_state_after = re.search(r"Webpage state after action: (.+)", step)

            # Construct JSON object
            one_shot = {
                "user_task": user_task.group(1) if user_task else None,
                "user_request": user_request.group(1) if user_request else None,
                "request_name": request_name.group(1) if request_name else None,
                "request_category": request_category.group(1) if request_category else None,
                "request_category_search": request_category_search.group(1) if request_category_search else None,
                "request_date": request_date.group(1) if request_date else None,
                "request_time": request_time.group(1) if request_time else None,
                "request_count": request_count.group(1) if request_count else None,
                "status_name": status_name.group(1) if status_name else None,
                "status_date": status_date.group(1) if status_date else None,
                "status_time": status_time.group(1) if status_time else None,
                "status_count": status_count.group(1) if status_count else None,
                "list_name": list_name,
                "list_time": list_time,
                "webpage_url": webpage_url.group(1) if webpage_url else None,
                "webpage_category": webpage_category.group(1) if webpage_category else None,
                "webpage_state": webpage_state.group(1) if webpage_state else None,
                "thought": thought.group(1) if thought else None,
                "agent_action": action.group(1) if action else None,
                "webpage_state_after": webpage_state_after.group(1) if webpage_state_after else None
            }
            self.few_shots.append(one_shot)

    def generate_one_shot_prompt(self, one_shot, prompt_template):
        # Replace placeholders with actual values
        for key, value in one_shot.items():
            if isinstance(value, list):
                value = ", ".join(value)
            value = str(value)
            prompt_template = prompt_template.replace(f"{{{key}}}", str(value))

        return prompt_template

    def generate_few_shot_prompts(self, prompt_template_human_file_path = "./src/reasoning/reasoning_prompt_human.md"):
        try:
            with open(prompt_template_human_file_path, "r") as file:
                prompt_template = file.read()
        except FileNotFoundError:
            print(f"Prompt template file not found at {prompt_template_human_file_path}.")
            return

        few_shot_prompts = []
        for one_shot in self.few_shots:
            few_shot_prompts.append(self.generate_one_shot_prompt(one_shot, prompt_template) + "\n")
        
        return few_shot_prompts
    
    def generate_few_shot_responses(self):
        few_shot_responses = []
        for one_shot in self.few_shots:
            one_shot_response = (
                f"thought: {one_shot['thought']}\n"
                f"action: {one_shot['action']}\n"
                f"actions_to_avoid: {one_shot['actions_to_avoid']}"
            )
            few_shot_responses.append(one_shot_response)
        
        return few_shot_responses
    
def main():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    
    reasoning_few_shots = ReasoningFewShots()
    reasoning_few_shots.load_few_shots()
    few_shot_prompts = reasoning_few_shots.generate_few_shot_prompts()
    few_shot_responses = reasoning_few_shots.generate_few_shot_responses()
    for prompt, response in zip(few_shot_prompts, few_shot_responses):
        print(f"{Fore.WHITE}{prompt}")
        print(f"{Fore.YELLOW}{response}")
        print(f"{Fore.GREEN}{'='*50}")
        
   
if __name__ == "__main__":
    main()