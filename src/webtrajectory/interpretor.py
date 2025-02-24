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
from pydantic import BaseModel, Field

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from extraction.extraction_prompt import ExtractionResponse

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

# Output Pydantic
class ReasoningResponse(BaseModel):
    thought: str = Field(
        description="A brief reasoning explaining why these actions are chosen."
    )
    top_actions: List[str] = Field(
        description="A concrete description of the top 3 possible actions to take. E.g. Update the party size selector on web page to 3."
    )

class OneShotResponse(BaseModel):
    thought: str = Field(
        description="A brief reasoning explaining why this action was chosen."
    )
    action: str = Field(
        description="A concrete description of the action that should be chosen. Please only include a single action. E.g. Update the party size selector on web page to 3."
    )
    actions_to_avoid: List[str] = Field(
        description="A list of actions that should not be chosen. They are the ones from the top possible actions that do NOT match the actual action. E.g. ['GoBack', 'Navigate']"
    )

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

oneshot_llm = ChatOpenAI(
    model="gpt-4o",
    max_tokens=16384
).with_structured_output(OneShotResponse).with_retry(
    stop_after_attempt=3
)

def generate_extraction_results_human_prompt(prompt_path, extraction_data):
    try:
        with open(prompt_path, "r") as file:
            prompt_template = file.read()
    except FileNotFoundError:
        print(f"Prompt template file not found at {prompt_path}.")
        return

    for key, value in extraction_data.model_dump().items():
        value = format_time_value(value)
        prompt_template = prompt_template.replace(f"{{{key}}}", str(value))
        
    return prompt_template

class Interpreter:

    def __init__(self, folder):
        self.folder = folder
        self.extraction_results = []  # List to store extraction results
        
        # Load trajectory data
        trajectory_path = os.path.join(folder, "trajectory.json")
        try:
            with open(trajectory_path, 'r') as f:
                self.trajectory = json.load(f)
        except FileNotFoundError:
            print(f"Trajectory file not found at {trajectory_path}")
            self.trajectory = []

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

        # Prompt to generate the extraction results of user request and web page
        self.extraction_prompt_path = "./src/extraction/extraction_prompt.md"
        
        # Prompts to generate the reasoning of the top possible actions
        self.reasoning_prompt_human_path = "./src/reasoning/reasoning_prompt_human.md"
        self.reasoning_prompt_system_path = "./src/reasoning/reasoning_prompt_system.md"
        self.reasoning_prompt_ot_booking_path = "./src/reasoning/opentable/booking_prompt.md"
        self.reasoning_prompt_ot_detailed_path = "./src/reasoning/opentable/detailed_prompt.md"
        self.reasoning_prompt_ot_homepage_path = "./src/reasoning/opentable/homepage_prompt.md"
        self.reasoning_prompt_ot_search_path = "./src/reasoning/opentable/search_prompt.md"

        # Prompts to generate the one-shot example of the current step
        self.oneshot_prompt_human_path = "./src/webtrajectory/oneshot_prompt_human.md"
        self.oneshot_prompt_system_path = "./src/webtrajectory/oneshot_prompt_system.md"
        self.oneshot_prompt_ot_booking_path = "./src/webtrajectory/opentable/booking_prompt.md"
        self.oneshot_prompt_ot_detailed_path = "./src/webtrajectory/opentable/detailed_prompt.md"
        self.oneshot_prompt_ot_homepage_path = "./src/webtrajectory/opentable/homepage_prompt.md"
        self.oneshot_prompt_ot_search_path = "./src/webtrajectory/opentable/search_prompt.md"
        

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

    def normalize_string(self, s: str) -> str:
        if not isinstance(s, str):
            return s
        # Remove special characters and extra spaces, convert to lowercase
        # First get alphanumeric and spaces
        normalized = ''.join(c.lower() for c in s if c.isalnum() or c.isspace())
        # Then reduce multiple spaces to single space and strip
        return ' '.join(normalized.split())
        
    def retrieve_reasoning_system_prompt(self, page_category: str):
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

    def retrieve_oneshot_system_prompt(self, page_category: str):
        if page_category and "home".casefold() in page_category.casefold():
            return PromptTemplate.from_file(self.oneshot_prompt_ot_homepage_path)
        elif page_category and "search".casefold() in page_category.casefold():
            return PromptTemplate.from_file(self.oneshot_prompt_ot_search_path)
        elif page_category and "detail".casefold() in page_category.casefold():
            return PromptTemplate.from_file(self.oneshot_prompt_ot_detailed_path)
        elif page_category and "booking".casefold() in page_category.casefold():
            return PromptTemplate.from_file(self.oneshot_prompt_ot_booking_path)
        else:
            return PromptTemplate.from_file(self.oneshot_prompt_system_path)
    
    def extract(self):
        """Extract information from screenshots and user requests for all steps.
        First checks if extraction results already exist in extraction.json.
        If they do, loads them instead of running extraction again.
        Otherwise runs extraction and saves results to extraction.json.
        """
        # Check for existing extraction.json
        extraction_path = os.path.join(self.folder, "extraction.json")
        if os.path.exists(extraction_path):
            print(f"{Fore.GREEN}Loading existing extraction results from {extraction_path}")
            try:
                with open(extraction_path, 'r') as f:
                    saved_results = json.load(f)
                # Convert saved results back to ExtractionResponse objects
                self.extraction_results = [ExtractionResponse(**result) for result in saved_results]
                return
            except Exception as e:
                print(f"{Fore.RED}Error loading extraction.json: {e}. Will re-run extraction.")
        
        self.extraction_results = []  # Reset results list
        
        for step, step_data in enumerate(self.trajectory):
            # Load images
            img_before_path = step_data["annotated"]
            try:
                with open(img_before_path, "rb") as f:
                    img_before = base64.b64encode(f.read()).decode()
            except FileNotFoundError:
                print(f"Image file not found at {img_before_path}")
                continue

            # Get task and URL
            task = step_data["task"]
            url = step_data["url"]

            # Create extraction template
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
            self.extraction_results.append(extraction_response)

            print(f"{Fore.WHITE}================= Extracted info for step: {step} =================")
            print(f"{Fore.GREEN}user_task: {Fore.YELLOW}{task}")
            for key, value in extraction_response.model_dump().items():
                print(f"{Fore.GREEN}{key}: {Fore.YELLOW}{format_time_value(value)}")
            print("")
            
        # Save results to extraction.json
        try:
            results_to_save = [result.model_dump() for result in self.extraction_results]
            with open(extraction_path, 'w') as f:
                json.dump(results_to_save, f, cls=DateTimeEncoder, indent=4)
            print(f"{Fore.GREEN}Saved extraction results to {extraction_path}")
        except Exception as e:
            print(f"{Fore.RED}Error saving extraction.json: {e}")
            
    def interpret_step(self, img_before, img_after, task, url, step):
        """Interpret a single step using extraction results and generate next action.
        Checks for near-duplicates and includes next step's extraction results in one-shot generation.
        
        Args:
            img_before: Base64 encoded image of current state
            img_after: Base64 encoded image of next state
            task: User task
            url: Current URL
            step: Current step number
            
        Returns:
            dict or None: Interpretation response if successful, None if step should be skipped
        """
        # Step 1: Get extraction results
        if step >= len(self.extraction_results) or step + 1 >= len(self.extraction_results):
            print(f"{Fore.RED}Error: Step {step} or {step + 1} not found in extraction results")
            return None
            
        current_extraction_response = self.extraction_results[step]
        next_extraction_response = self.extraction_results[step + 1]
        
        # Check if near-duplicate
        if self.is_neardupe(current_extraction_response, next_extraction_response):
            print(f"{Fore.YELLOW}Step {step} and {step + 1} are near-duplicates, skipping...")
            return None
        
        # Step 2: Reasoning about possible actions
        reasoning_system_prompt = self.retrieve_reasoning_system_prompt(current_extraction_response.webpage_category)
        reasoning_human_prompt = generate_extraction_results_human_prompt(self.reasoning_prompt_human_path, current_extraction_response)
        
        reasoning_template = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate(
                    prompt=reasoning_system_prompt
                ),
                HumanMessagePromptTemplate(
                    prompt=[
                        PromptTemplate.from_template("[Web Page]\n"),
                        ImagePromptTemplate(
                            template={"url": "data:image/png;base64,{img_before}"},
                            input_variables=["img_before"]
                        ),
                        PromptTemplate.from_template("\n\nCurrent URL: {url}\n")
                    ]
                ),
                HumanMessagePromptTemplate(
                    prompt=[
                        PromptTemplate.from_template(reasoning_human_prompt)
                    ]
                )
            ]
        )

        # Format the messages with our data
        reasoning_messages = reasoning_template.format_messages(
            img_before=img_before,
            url=url
        )

        # Run reasoning
        reasoning_response = reasoning_llm.invoke(reasoning_messages)

        # Step 3: Generate the one-shot example of the current step
        oneshot_system_prompt = self.retrieve_oneshot_system_prompt(current_extraction_response.webpage_category)
        
        # Generate prompts for both current and next states
        oneshot_human_prompt_current = generate_extraction_results_human_prompt(self.oneshot_prompt_human_path, current_extraction_response)
        oneshot_human_prompt_next = generate_extraction_results_human_prompt(self.oneshot_prompt_human_path, next_extraction_response)
        
        oneshot_template = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate(
                    prompt=oneshot_system_prompt
                ),
                HumanMessagePromptTemplate(
                    prompt=[
                        PromptTemplate.from_template("[Web Page before the action]\n"),
                        ImagePromptTemplate(
                            template={"url": "data:image/png;base64,{img_before}"},
                            input_variables=["img_before"]
                        ),
                        PromptTemplate.from_template("\n\nURL of the web page before the action: {url}\n"),
                        PromptTemplate.from_template("\n[Description of the user request and web page before the action]\n"),
                        PromptTemplate.from_template(oneshot_human_prompt_current),
                        PromptTemplate.from_template("\n[Web Page after the action]\n"),
                        ImagePromptTemplate(
                            template={"url": "data:image/png;base64,{img_after}"},
                            input_variables=["img_after"]
                        ),
                        PromptTemplate.from_template("\n[Description of the user request and web page after the action]\n"),
                        PromptTemplate.from_template(oneshot_human_prompt_next),
                        PromptTemplate.from_template("\n[Top possible actions]: {top_actions}\n")
                    ]
                )
            ]
        )

        # Format the messages with our data
        oneshot_messages = oneshot_template.format_messages(
            img_before=img_before,
            url=url,
            img_after=img_after,
            top_actions=reasoning_response.top_actions
        )

        # Run reasoning
        oneshot_response = oneshot_llm.invoke(oneshot_messages)
        
        # Generate the interpretor's response
        interpretation_response = {}
        for key, value in current_extraction_response.model_dump().items():
            interpretation_response[key] = format_time_value(value)
        for key, value in reasoning_response.model_dump().items():
            interpretation_response[key] = format_time_value(value)
        for key, value in oneshot_response.model_dump().items():
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
        self.extract()
        
        trajectory_txt_path = os.path.join(self.folder, "trajectory.txt")
        if os.path.exists(trajectory_txt_path):
            os.remove(trajectory_txt_path)

        steps = []
        step = 0
        few_shots = []

        for i in range(len(self.trajectory) - 1):
            current = self.trajectory[i]
            next_step = self.trajectory[i + 1]

            current_img_path = current["annotated"]
            next_img_path = next_step["annotated"]

            if platform.system() != "Windows":
                current_img_path = current_img_path.replace("\\", "/")
                next_img_path = next_img_path.replace("\\", "/")
            
            img_current = self.load_based64_image(current_img_path)
            img_next = self.load_based64_image(next_img_path)
            task = current["task"]
            url = current["url"]
            
            response = self.interpret_step(img_current, img_next, task, url, step)
            
            if response is not None:
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
            else:
                step += 1

        # Generate and write HTML file
        html_content = self.generate_html(steps)
        with open(os.path.join(self.folder, "trajectory.html"), "w", encoding='utf-8') as html_file:
            html_file.write(html_content)

        with open(os.path.join(self.folder, "few_shots.json"), "w", encoding='utf-8') as json_file:
            json.dump(few_shots, json_file, ensure_ascii=False, indent=4, cls=DateTimeEncoder)

    def is_neardupe(self, response1: ExtractionResponse, response2: ExtractionResponse) -> bool:
        """Check if two ExtractionResponse objects are near-duplicates.
        Focuses on request_*, status_*, and webpage_category fields.
        
        Args:
            response1: First ExtractionResponse object
            response2: Second ExtractionResponse object
            
        Returns:
            bool: True if the responses are near-duplicates
        """
        # Check webpage_category first - if different, they're not duplicates
        if response1.webpage_category != response2.webpage_category:
            return False
            
        # Check request fields
        request_fields = [
            ('request_name', response1.request_name, response2.request_name),
            ('request_category', response1.request_category, response2.request_category),
            ('request_date', response1.request_date, response2.request_date),
            ('request_time', response1.request_time, response2.request_time),
            ('request_count', response1.request_count, response2.request_count)
        ]
        
        # Check status fields
        status_fields = [
            ('status_name', response1.status_name, response2.status_name),
            ('status_date', response1.status_date, response2.status_date),
            ('status_time', response1.status_time, response2.status_time),
            ('status_count', response1.status_count, response2.status_count)
        ]
        
        # Count how many fields match
        request_matches = 0
        for field, val1, val2 in request_fields:
            if val1 is None and val2 is None:
                request_matches += 1
            elif val1 is not None and val2 is not None:
                val1_norm = self.normalize_string(val1)
                val2_norm = self.normalize_string(val2)
                if val1_norm == val2_norm:
                    request_matches += 1
                    
        status_matches = 0
        for field, val1, val2 in status_fields:
            if val1 is None and val2 is None:
                status_matches += 1
            elif val1 is not None and val2 is not None:
                val1_norm = self.normalize_string(val1)
                val2_norm = self.normalize_string(val2)
                if val1_norm == val2_norm:
                    status_matches += 1
        
        # Count how many fields have values in both responses
        request_comparisons = sum(1 for field, val1, val2 in request_fields 
                                if val1 is not None and val2 is not None)
        status_comparisons = sum(1 for field, val1, val2 in status_fields 
                               if val1 is not None and val2 is not None)
        
        # If we can't compare any fields, they're not duplicates
        if request_comparisons == 0 and status_comparisons == 0:
            return False
            
        # Calculate match ratio for each category
        request_ratio = request_matches / request_comparisons if request_comparisons > 0 else 0
        status_ratio = status_matches / status_comparisons if status_comparisons > 0 else 0
        
        # Consider them near-duplicates if:
        # 1. At least one category has fields to compare
        # 2. For categories with fields to compare, at least 80% match
        threshold = 1.0
        has_request_fields = request_comparisons > 0
        has_status_fields = status_comparisons > 0
        
        if has_request_fields and has_status_fields:
            # If both have fields, both should meet threshold
            return request_ratio >= threshold and status_ratio >= threshold
        elif has_request_fields:
            # If only request fields exist, check those
            return request_ratio >= threshold
        elif has_status_fields:
            # If only status fields exist, check those
            return status_ratio >= threshold
        
        return False

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
        # interpreter.extract()

if __name__ == "__main__":
    main()