import os
from openai import OpenAI
import base64
from colorama import Fore
import json
from datetime import datetime

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class Interpreter:

    def __init__(self, folder):
        self.folder = folder

    def load_based64_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def interpret(self, img_before, img_after, task, url):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You're tasked to observe a user action in web browser. You're given two screenshots before and after the action with annotation of mouse position. 
                                Please provide your response in the following JSON format:
                                {
                                    "webpage_status": "description of webpage status before action, ignoring mouse annotation",
                                    "action": "description of what action user took, referring to mouse annotations",
                                    "thoughts": "reasoning about user's intention"
                                }
                                
                                You're also given the task that user is trying to achieve. Please refer to it when you reason about user's intention.""",
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
                            "text": f"Current URL: {url}",
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
        content = response_json["choices"][0]["message"]["content"]
        
        # Remove any markdown code block markers if present
        content = content.replace("```json", "").replace("```", "").strip()
        
        try:
            structured_response = json.loads(content)
            print(f"{Fore.YELLOW}Webpage Status: {structured_response['webpage_status']}")
            print(f"{Fore.YELLOW}Action: {structured_response['action']}")
            print(f"{Fore.YELLOW}Thoughts: {structured_response['thoughts']}")
            return structured_response
        except json.JSONDecodeError:
            print(f"{Fore.RED}Failed to parse LLM response as JSON. Raw response:")
            print(f"{Fore.RED}{content}")
            return {
                "webpage_status": "Error parsing response",
                "action": "Error parsing response",
                "thoughts": "Error parsing response"
            }

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
                    <th>Step</th>
                    <th>Webpage Status</th>
                    <th>Action</th>
                    <th>Thoughts</th>
                    <th>Before Image</th>
                    <th>After Image</th>
                </tr>
        """
        
        for step in steps:
            html_content += f"""
                <tr>
                    <td class="step-number">Step {step['step']}</td>
                    <td>{step['webpage_status']}</td>
                    <td>{step['action']}</td>
                    <td>{step['thoughts']}</td>
                    <td><img src="{step['img_before']}" alt="Before"></td>
                    <td><img src="{step['img_after']}" alt="After"></td>
                </tr>
            """
        
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
            
            img_current = self.load_based64_image(current["annotated"])
            img_next = self.load_based64_image(next_step["annotated"])
            task = current["task"]
            url = current["url"]
            
            response = self.interpret(img_current, img_next, task, url)
            
            # Store step information for HTML generation
            steps.append({
                'step': step,
                'webpage_status': response['webpage_status'],
                'action': response['action'],
                'thoughts': response['thoughts'],
                'img_before': f"data:image/png;base64,{img_current}",
                'img_after': f"data:image/png;base64,{img_next}"
            })
            
            # Write to text file
            with open(os.path.join(self.folder, "trajectory.txt"), "a") as output_file:
                output_file.write(f"Step {step}:\n")
                output_file.write(f"Webpage Status: {response['webpage_status']}\n")
                output_file.write(f"Action: {response['action']}\n")
                output_file.write(f"Thoughts: {response['thoughts']}\n\n")
                step += 1
        
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
    folder = select_data_folder()
    if folder:
        interpreter = Interpreter(folder)
        interpreter.run()

if __name__ == "__main__":
    main()
