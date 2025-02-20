import os
import platform
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate
import base64
from colorama import Fore
import json
from datetime import datetime, time, date
from typing import Optional, List
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from extraction.extraction_prompt import ExtractionResponse
from interfaces import ReasoningResponse

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, time)):
            return str(obj)
        return super().default(obj)

def format_time_value(value):
    """Format a time value to 12-hour format with AM/PM"""
    if isinstance(value, time):
        return value.strftime("%I:%M %p").lstrip("0")
    elif isinstance(value, date):
        return value.strftime("%m/%d/%Y")
    elif isinstance(value, list):
        if all(isinstance(x, time) for x in value):
            return [t.strftime("%I:%M %p").lstrip("0") for t in value]
        elif all(isinstance(x, date) for x in value):
            return [d.strftime("%m/%d/%Y") for d in value]
    return value

# Initialize LLMs
extraction_llm = ChatOpenAI(
    model="gpt-4o",
    max_tokens=16384
).with_structured_output(ExtractionResponse).with_retry(
    stop_after_attempt=3
)

reasoning_llm = ChatOpenAI(
    model="gpt-4o",
    max_tokens=16384
).with_structured_output(ReasoningResponse).with_retry(
    stop_after_attempt=3
)

class Interpreter:

    def __init__(self, folder):
        self.folder = folder

        # Initialize HTML schema with ordered fields
        self.html_schema = {
            "step": {"type": "integer"},
            "user_task": {"type": "string"}            
        }
        
        
        # Add fields from ExtractionResponse in order of definition
        extraction_schema = ExtractionResponse.model_json_schema()
        for field_name in extraction_schema["properties"]:
            field_info = extraction_schema["properties"][field_name]
            self.html_schema[field_name] = {"type": field_info.get("type", "string")}
            if field_name == "webpage_category":
                self.html_schema["webpage_url"] = {"type": "string"}
        

        # Add fields from ReasoningResponse in order of definition
        reasoning_schema = ReasoningResponse.model_json_schema()
        for field_name in reasoning_schema["properties"]:
            field_info = reasoning_schema["properties"][field_name]
            self.html_schema[field_name] = {"type": field_info.get("type", "string")}

        self.html_schema["img_before"] = {"type": "string"}
        self.html_schema["img_after"] = {"type": "string"}

        self.extraction_prompt_path = "./src/extraction/extraction_prompt.md"
        self.reasoning_prompt_human_path = "./src/webtrajectory/reasoning_prompt_human.md"
        self.reasoning_prompt_system_path = "./src/webtrajectory/reasoning_prompt.md"
        self.reasoning_prompt_ot_booking_path = "./src/webtrajectory/opentable/booking_prompt.md"
        self.reasoning_prompt_ot_detailed_path = "./src/webtrajectory/opentable/detailed_prompt.md"
        self.reasoning_prompt_ot_homepage_path = "./src/webtrajectory/opentable/homepage_prompt.md"
        self.reasoning_prompt_ot_search_path = "./src/webtrajectory/opentable/search_prompt.md"
        

    def load_based64_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
        
    def load_prompt(self):
        """Load the prompt from the specified file."""
        with open(self.prompt_file, "r") as file:
            return file.read()
        
    def generate_empty_response(self):
        empty_response = {}
    
        for key in self.html_schema.keys():
            
            empty_response[key] = None  # Default to None for all properties

            """ We shouldn't need these default values, but leave them here for now
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
            """

        return empty_response
    
    def check_structured_response(self, structured_response):
         for key, details in self.html_schema.items():
            property_type = details.get("type")

            # Set default values based on property type
            if property_type == "string":
                if structured_response[key] == "" or structured_response[key] == "Not Specified":
                    structured_response[key] = "None"
            elif property_type == "array":
                if structured_response[key] == []:
                    structured_response[key] = None
            elif property_type == "object":
                if structured_response[key] == {}:
                    structured_response[key] = None

            """ We shouldn't need these default values, but leave them here for now
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
            """

    def generate_reasoning_human_prompt(self, task, extraction_data):
        try:
            with open(self.reasoning_prompt_human_path, "r") as file:
                prompt_template = file.read()
        except FileNotFoundError:
            print(f"Prompt template file not found at {self.reasoning_prompt_human_path}.")
            return

        # prompt_template = prompt_template.replace("{user_request}", task)
        for key, value in extraction_data.model_dump().items():
            value = format_time_value(value)
            prompt_template = prompt_template.replace(f"{{{key}}}", str(value))
        
        return prompt_template

    def retrieve_prompt(self, page_category: str):
        if page_category and "home".casefold() in page_category.casefold():
            return PromptTemplate.from_file(self.reasoning_prompt_ot_homepage_path)
        elif page_category and "search".casefold() in page_category.casefold():
            return PromptTemplate.from_file(self.reasoning_prompt_ot_search_path)
        elif page_category and "detail".casefold() in page_category.casefold():
            return PromptTemplate.from_file(self.reasoning_prompt_ot_detailed_path)
        elif page_category and "booking".casefold() in page_category.casefold():
            return PromptTemplate.from_file(self.reasoning_prompt_ot_booking_path)
        else:
            return PromptTemplate.from_file(self.reasoning_prompt_system_path)
    
    def interpret(self, img_before, img_after, task, url, step):
        """Interpret the current state and generate next action."""
        # Step 1: Extraction
        # extraction_prompt = self.load_prompt()
        
        # Create chat prompt template
        extraction_template = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate(
                    prompt=[
                        PromptTemplate.from_file(self.extraction_prompt_path),
                    ],
                ),
                HumanMessagePromptTemplate(
                    prompt=[
                        PromptTemplate.from_template("[Web Page]\n"),
                        ImagePromptTemplate(
                            template={"url": "data:image/png;base64,{img}"},
                            input_variables=["img"]
                        ),
                        PromptTemplate.from_template("\n\nCurrent URL: {url}\n"),
                        PromptTemplate.from_template("[User Request]\n{task}")
                    ]
                )
            ]
        )
        
        # Format the messages with our data
        extraction_messages = extraction_template.format_messages(
            img=img_before,
            url=url,
            task=task
        )

        # Run extraction
        extraction_response = extraction_llm.invoke(extraction_messages)
        
        # Step 2: Reasoning
        system_prompt = self.retrieve_prompt(extraction_response.webpage_category)
        reasoning_human_prompt = self.generate_reasoning_human_prompt(task, extraction_response)
        
        reasoning_template = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate(
                    prompt=system_prompt
                ),
                HumanMessagePromptTemplate(
                    prompt=[
                        PromptTemplate.from_template("[Web Page]\n"),
                        ImagePromptTemplate(
                            template={"url": "data:image/png;base64,{img}"},
                            input_variables=["img"]
                        ),
                        PromptTemplate.from_template("\n\nCurrent URL: {url}\n"),
                        PromptTemplate.from_template(reasoning_human_prompt)
                    ]
                )
            ]
        )

        # Format the messages with our data
        reasoning_messages = reasoning_template.format_messages(
            img=img_before,
            url=url
        )

        # Run reasoning
        reasoning_response = reasoning_llm.invoke(reasoning_messages)
        
        # Generate the interpretor's response
        interpretation_response = {}
        for key, value in extraction_response.model_dump().items():
            interpretation_response[key] = format_time_value(value)
        for key, value in reasoning_response.model_dump().items():
            interpretation_response[key] = format_time_value(value)

        print(f"{Fore.WHITE}================= Interpreted LLM response for step: {step} =================")
        print(f"{Fore.GREEN}user_task: {Fore.YELLOW}{task}")
        for key, value in interpretation_response.items():
            print(f"{Fore.GREEN}{key}: {Fore.YELLOW}{value}")
        print("")

        return interpretation_response
    
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
        few_shots = []

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
            one_shot = {}
            with open(trajectory_txt_path, "a") as output_file:
                output_file.write(f"================= Interpreted LLM response for step: {step} =================\n")
                output_file.write(f"User task: {task}\n")
                html_response["user_task"] = task
                one_shot["user_task"] = task
                for key, value in response.items():
                    if key == "webpage_category":
                        output_file.write(f"Webpage URL: {url}\n")
                        html_response["webpage_url"] = url
                        one_shot["webpage_url"] = url
                    value = format_time_value(value)
                    output_file.write(f"{key.replace('_', ' ').capitalize()}: {value}\n")
                    html_response[key] = value
                    one_shot[key] = value
                output_file.write("\n")
                html_response["img_before"] = f"data:image/png;base64,{img_current}"
                html_response["img_after"] = f"data:image/png;base64,{img_next}"
                step += 1
                steps.append(html_response)
                few_shots.append(one_shot)

        # Generate and write HTML file
        html_content = self.generate_html(steps)
        with open(os.path.join(self.folder, "trajectory.html"), "w", encoding='utf-8') as html_file:
            html_file.write(html_content)

        with open(os.path.join(self.folder, "few_shots.json"), "w", encoding='utf-8') as json_file:
            json.dump(few_shots, json_file, ensure_ascii=False, indent=4, cls=DateTimeEncoder)

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