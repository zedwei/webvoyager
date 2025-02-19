from playwright.async_api import async_playwright
import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from colorama import Fore
import asyncio

TEXT = "Mouse"

with open("./src/webtrajectory/click_listener.js") as f:
    click_listener_script = f.read()


class Client:
    async def init(self, task):
        print(f"{Fore.CYAN}Initializing client...")
        self.img_index = 0
        self.task = task
        self.start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.coord_trajectory = []

        browser = await async_playwright().start()
        self.browser = await browser.chromium.launch(
            channel="msedge", headless=False, args=["--window-position=0,0"]
        )
        self.context = await self.browser.new_context(
            #viewport={"width": 1024, "height": 768}
            viewport={"width": 1280, "height": 1080}
        )
        await self.context.expose_function("handle_click", self.handle_click)
        await self.context.add_init_script(click_listener_script)

        page = await self.context.new_page()
        await page.goto("https://www.opentable.com")
        print(f"{Fore.GREEN}Client initialized successfully")

    def _ensure_data_directory(self, is_annotated=False):
        """
        Create the data directory and return the file path for the screenshot.
        Args:
            is_annotated (bool): Whether this is for an annotated image
        Returns:
            tuple: (directory path, full file path)
        """
        dir = f"data/{self.start_time}"
        os.makedirs(dir, exist_ok=True)
        suffix = "annotated" if is_annotated else "raw"
        file_path = os.path.join(dir, f"screenshot_{self.img_index}_{suffix}.png")
        return dir, file_path

    def draw_cursor_annotation(self, draw, x, y, text):
        """
        Draw a simple arrow cursor annotation with text label on the image.
        
        Args:
            draw (ImageDraw): PIL ImageDraw object
            x (int): x coordinate of click
            y (int): y coordinate of click
            text (str): Text label to show next to cursor
        """
        # Simple arrow cursor - larger size
        cursor_points = [
            (x, y),           # Tip point
            (x - 10, y + 20), # Left point
            (x, y + 15),      # Inner point
            (x + 10, y + 20)  # Right point
        ]
        
        # Draw cursor with better visibility
        # Black outline
        draw.polygon(cursor_points + [cursor_points[0]], fill="white", outline="black", width=2)
        # Add second outline for emphasis
        draw.line(cursor_points + [cursor_points[0]], fill="black", width=3)
        
        # Add text label with better formatting
        try:
            # Larger font size for better visibility
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Position text to align with cursor better
        text_position = (x + 20, y)  # Align with cursor tip vertically
        
        # Draw text with thicker black outline for better visibility
        outline_offsets = [
            (2,2), (-2,-2), (2,-2), (-2,2),  # Outer corners
            (2,0), (-2,0), (0,2), (0,-2)     # Sides
        ]
        for offset in outline_offsets:
            draw.text((text_position[0]+offset[0], text_position[1]+offset[1]), 
                     text, fill="black", font=font)
        
        # Draw main text in bright red
        draw.text(text_position, text, fill="#FF0000", font=font)

    async def handle_click(self, event):
        print(f"{Fore.CYAN}Handling click event...")
        image_byte = await self.context.pages[-1].screenshot()
        url = self.context.pages[-1].url

        # Save raw screenshot
        dir, raw_path = self._ensure_data_directory(is_annotated=False)
        with open(raw_path, "wb") as file:
            file.write(image_byte)
        print(f"{Fore.GREEN}Raw screenshot saved: {raw_path}")

        # Create and save annotated version
        print(f"{Fore.CYAN}Creating annotated image...")
        img = Image.open(raw_path)
        draw = ImageDraw.Draw(img)
        
        # Draw cursor annotation
        self.draw_cursor_annotation(draw, event["x"], event["y"], TEXT)
        
        _, annotated_path = self._ensure_data_directory(is_annotated=True)
        img.save(annotated_path)
        print(f"{Fore.GREEN}Annotated image saved: {annotated_path}")

        # Update trajectory
        self.coord_trajectory.append({
            "task": self.task,
            "url": url,
            "raw": raw_path,
            "annotated": annotated_path,
            "mouse": event,
        })

        trajectory_path = os.path.join(dir, "trajectory.json")
        with open(trajectory_path, "w") as json_file:
            json.dump(self.coord_trajectory, json_file, indent=4)
        print(f"{Fore.GREEN}Trajectory saved: {trajectory_path}")
        self.img_index += 1

    @staticmethod
    async def start_recording(task=None):
        """
        Start recording user actions with the given task.
        
        Args:
            task (str, optional): The task to record. If None, will prompt user for input.
        """
        DEFAULT_TASK = "book a table at wild ginger seattle for 3 people on 2/10 9pm"
        
        if task is None:
            task = input(f"{Fore.YELLOW}Enter task [default {DEFAULT_TASK}]: ") or DEFAULT_TASK
            
        client = Client()
        await client.init(task)
        
        print(f"{Fore.GREEN}Recording started. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}Recording stopped.")

async def main():
    await Client.start_recording()

if __name__ == "__main__":
    asyncio.run(main())
