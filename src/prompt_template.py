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

