from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts.chat import MessagesPlaceholder
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate
from constants import PROMPT_FILENAME


def readPromptTemplate():
    with open(f"./src/prompts/{PROMPT_FILENAME}", "r") as file:
        file_content = file.read()
        return file_content


prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate(
            prompt=[
                PromptTemplate.from_template(readPromptTemplate()),
            ],
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
                PromptTemplate.from_template("{current_url}"),
                PromptTemplate.from_template("[User Input]"),
                PromptTemplate.from_template("{input}"),
            ],
        ),
        MessagesPlaceholder(
            optional=True,
            variable_name="scratchpad",
        ),
    ],
    input_variables=[
        "bbox_descriptions",
        "img",
        "input",
    ],
    partial_variables={"scratchpad": []},
)
