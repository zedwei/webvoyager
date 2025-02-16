import os
import platform
from openai import OpenAI
import base64
from colorama import Fore
import json
from datetime import datetime

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
TASK = "book a table at a steakhouse restaurant for 3 people on 1/28 9pm"

class Interpreter:

    def __init__(self, folder, prompt_file = "./src/webtrajectory/interpretor_prompt.md"):
        self.folder = folder
        self.schema = {
            "type": "object",
            "properties": {
                "user_request": {"type": "string"},
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
                "webpage_state": {"type": "string"},
                "thought": {"type": "string"},
                "agent_action": {"type": "string"},
                "webpage_state_after_action": {"type": "string"}
            },        
        }
        self.prompt_file = prompt_file

        self.html_schema = {
            "step": {"type": "integer"}            
        }
        self.html_schema["user_task"] = {"type": "string"}
        for key, details in self.schema["properties"].items():
            if key == "webpage_category":
                self.html_schema["webpage_url"] = {"type": "string"}
            self.html_schema[key] = details
        self.html_schema["img_before"] = {"type": "string"}
        self.html_schema["img_after"] = {"type": "string"}

    def load_based64_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
        
    def load_prompt(self):
        """Load the prompt from the specified file."""
        with open(self.prompt_file, "r") as file:
            return file.read()
        
    def generate_empty_response(self):
        empty_response = {}
    
        for key, details in self.schema["properties"].items():
            property_type = details.get("type")

            # Set default values based on property type
            if property_type == "string":
                empty_response[key] = ""
            elif property_type == "array":
                empty_response[key] = []
            elif property_type == "object":
                empty_response[key] = {}
            elif property_type in ["integer", "number"]:
                empty_response[key] = 0
            elif property_type == "boolean":
                empty_response[key] = False
            else:
                empty_response[key] = None  # Fallback for undefined types

        return empty_response
    
    def check_structured_response(self, structured_response):
         for key, details in self.schema["properties"].items():
            property_type = details.get("type")

            # Set default values based on property type
            if property_type == "string":
                if structured_response[key] == "":
                    structured_response[key] = "None"
            elif property_type == "array":
                if structured_response[key] == None:
                    structured_response[key] = []
            elif property_type == "object":
                if structured_response[key] == None:
                    structured_response[key] = {}
            elif property_type in ["integer", "number"]:
                if structured_response[key] == None:
                    structured_response[key] = 0
            elif property_type == "boolean":
                if structured_response[key] == None:
                    structured_response[key] = False

    def interpret(self, img_before, img_after, task, url, step):
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
                            "text": f"[Current URL]: {url}",
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
        
        response_json = response.to_dict()
        content = response_json["choices"][0]["message"]["content"]
        
        # Remove any markdown code block markers if present
        content = content.replace("```json", "").replace("```", "").strip()
        
        try:
            structured_response = json.loads(content)
            self.check_structured_response(structured_response)
            print(f"{Fore.WHITE}================= Interpreted LLM response for step: {step} =================")
            print(f"{Fore.GREEN}user_task: {Fore.YELLOW}{task}")
            for key, value in structured_response.items():
                if key == "webpage_category":
                    print(f"{Fore.GREEN}webpage_url: {Fore.YELLOW}{url}")
                print(f"{Fore.GREEN}{key}: {Fore.YELLOW}{value}")
            print("")
            return structured_response
        except json.JSONDecodeError:
            print(f"{Fore.RED}Failed to parse LLM response as JSON. Raw response:")
            print(f"{Fore.RED}{content}")
            empty_structured_response = self.generate_empty_response()
            return empty_structured_response
 
    def generate_html(self, steps):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                table { 
                    border-collapse: collapse; 
                    width: 100%; 
                    margin: 20px 0;
                }
                th, td { 
                    border: 1px solid #ddd; 
                    padding: 12px; 
                    text-align: left; 
                }
                th { 
                    background-color: #f2f2f2; 
                }
                img {
                    max-width: 500px;
                    height: auto;
                }
                .step-number {
                    font-weight: bold;
                    font-size: 1.2em;
                    background-color: #e6e6e6;
                }
            </style>
        </head>
        <body>
            <table>
                <tr>
        """
        # Add the rest of the table headers dynamically based on the schema
        for key in self.html_schema.keys():
            html_content += f"<th>{key.replace('_', ' ').capitalize()}</th>"
        
        html_content += """
                </tr>
        """
        
        # Add the actual table rows based on the steps
        for step in steps:
            html_content += f"""
                <tr>
                    <td class="step-number">Step {step["step"]}</td>
            """
            for key, value in step.items():
                if key == "img_before":
                    html_content += f"<td><img src='{value}' alt='Before'></td>"
                elif key == "img_after":
                    html_content += f"<td><img src='{value}' alt='After'></td>"
                elif key != "step":
                    html_content += f"<td>{value}</td>"
            html_content += "</tr>"

        html_content += """
            </table>
        </body>
        </html>
        """
        return html_content

    def run(self):
        trajectory_file = os.path.join(self.folder, "trajectory.json")

        trajectory_txt_path = os.path.join(self.folder, "trajectory.txt")
        if os.path.exists(trajectory_txt_path):
            os.remove(trajectory_txt_path)

        with open(trajectory_file, "r") as file:
            trajectory_data = json.load(file)

        steps = []
        step = 0

        for i in range(len(trajectory_data) - 1):
            current = trajectory_data[i]
            next_step = trajectory_data[i + 1]

            current_img_path = current["annotated"]
            next_img_path = next_step["annotated"]

            if platform.system() != "Windows":
                current_img_path = current_img_path.replace("\\", "/")
                next_img_path = next_img_path.replace("\\", "/")
            
            img_current = self.load_based64_image(current_img_path)
            img_next = self.load_based64_image(next_img_path)
            task = current["task"]
            url = current["url"]
            
            response = self.interpret(img_current, img_next, task, url, step)
            
            # Write to text file
            html_response = {}
            html_response["step"] = step
            with open(trajectory_txt_path, "a") as output_file:
                output_file.write(f"================= Interpreted LLM response for step: {step} =================\n")
                output_file.write(f"User task: {task}\n")
                html_response["user_task"] = task
                for key, value in response.items():
                    if key == "webpage_category":
                        output_file.write(f"Webpage URL: {url}\n")
                        html_response["webpage_url"] = url
                    output_file.write(f"{key.replace('_', ' ').capitalize()}: {value}\n")
                    html_response[key] = value
                output_file.write("\n")
                html_response["img_before"] = f"data:image/png;base64,{img_current}"
                html_response["img_after"] = f"data:image/png;base64,{img_next}"
                step += 1
                steps.append(html_response)

        # Generate and write HTML file
        html_content = self.generate_html(steps)
        with open(os.path.join(self.folder, "trajectory.html"), "w", encoding='utf-8') as html_file:
            html_file.write(html_content)

def select_data_folder():
    """
    Let user select a data folder from available recordings.
    Returns:
        str: Path to selected folder, or None if no folders found
    """
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

def main():
    
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    folder = select_data_folder()
    if folder:
        interpreter = Interpreter(folder)
        interpreter.run()

if __name__ == "__main__":
    main()