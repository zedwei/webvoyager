from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts.chat import MessagesPlaceholder
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate


def readPromptTemplate():
    with open('./src/prompt_restaurant_booking.md', 'r') as file:
        file_content = file.read()
        return file_content


prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate(
            prompt=[
                # PromptTemplate.from_template("Imagine you are a robot browsing the web, just like humans. Now you need to complete a task. In each iteration, you will receive an Observation that includes a screenshot of a webpage and some texts. This screenshot will\nfeature Numerical Labels placed in the TOP LEFT corner of each Web Element. Carefully analyze the visual\ninformation to identify the Numerical Label corresponding to the Web Element that requires interaction, then follow\nthe guidelines and choose one of the following actions:\n\n1. Click a Web Element.\n2. Delete existing content in a textbox and then type content.\n3. Scroll up or down.\n4. Wait \n5. Go back\n7. Return to google to start over.\n8. Respond with the final answer\n\nCorrespondingly, Action should STRICTLY follow the format:\n\n- Click [Numerical_Label] \n- Type [Numerical_Label]; [Content] \n- Scroll [Numerical_Label or WINDOW]; [up or down] \n- Wait \n- GoBack\n- Google\n- ANSWER; [content]\n\nKey Guidelines You MUST follow:\n\n* Action guidelines *\n1) Execute only one action per iteration.\n2) When clicking or typing, ensure to select the correct bounding box.\n3) Numeric labels lie in the top-left corner of their corresponding bounding boxes and are colored the same.\n\n* Web Browsing Guidelines *\n1) Don't interact with useless web elements like Login, Sign-in, donation that appear in Webpages\n2) Select strategically to minimize time wasted.\n\nYour reply should strictly follow the format:\n\nThought: {{Your brief thoughts (briefly summarize the info that will help ANSWER)}}\nAction: {{One Action format you choose}}\nThen the User will provide:\nObservation: {{A labeled screenshot Given by User}}\n"),
                PromptTemplate.from_template(readPromptTemplate()),
            ],
        ),
        MessagesPlaceholder(
            optional=True,
            variable_name="scratchpad",
        ),
        HumanMessagePromptTemplate(
            prompt=[
                ImagePromptTemplate(
                    template={"url": "data:image/png;base64,{img}"},
                    input_variables=[
                        "img",
                    ],
                ),
                PromptTemplate.from_template("{bbox_descriptions}"),
                PromptTemplate.from_template("{input}"),
            ],
        ),
    ],
    input_variables=[
        "bbox_descriptions",
        "img",
        "input",
    ],
    partial_variables={"scratchpad": []},
)
