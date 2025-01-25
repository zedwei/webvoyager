from playwright.async_api import async_playwright
import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

TEXT = "Interacted component"

with open("./src/webtrajectory/click_listener.js") as f:
    click_listener_script = f.read()


class Client:
    async def init(self, task):
        self.img_index = 0
        self.task = task
        self.pending = False
        self.start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.coord_trajectory = []

        browser = await async_playwright().start()
        self.browser = await browser.chromium.launch(
            channel="msedge", headless=False, args=["--window-position=0,0"]
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1024, "height": 768}
        )
        await self.context.expose_function("handle_click", self.handle_click)
        await self.context.add_init_script(click_listener_script)

        page = await self.context.new_page()
        await page.goto("https://www.opentable.com")

    async def handle_click(self, event):
        image_byte = await self.context.pages[-1].screenshot()
        dir = f"data/{self.start_time}"
        os.makedirs(dir, exist_ok=True)
        suffix = "after" if self.pending else "before"
        file_path = os.path.join(dir, f"screenshot_{self.img_index}_{suffix}.png")
        with open(file_path, "wb") as file:
            file.write(image_byte)

        if not self.pending:
            # Draw rectangle and text to form the annotated before image
            img = Image.open(file_path)
            draw = ImageDraw.Draw(img)
            top_left = (event["x"] - 20, event["y"] - 20)
            bottom_right = (event["x"] + 20, event["y"] + 20)
            draw.rectangle([top_left, bottom_right], outline="red", width=3)
            text_position = (event["x"] - 20, event["y"] - 30)
            draw.text(text_position, TEXT, fill="red", font=ImageFont.load_default())
            anno_file_path = os.path.join(
                dir, f"screenshot_{self.img_index}_before_annotated.png"
            )
            img.save(anno_file_path)

            self.coord_trajectory.append(
                {
                    "task": self.task,
                    "before": file_path,
                    "mouse": event,
                    "before_annotated": anno_file_path,
                }
            )
            self.pending = True
        else:
            self.coord_trajectory[-1]["after"] = file_path
            self.pending = False
            with open(os.path.join(dir, "trajectory.json"), "w") as json_file:
                json.dump(self.coord_trajectory, json_file, indent=4)
            self.img_index += 1
