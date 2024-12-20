from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain_core.prompts import PromptTemplate

OPENAI_EXTRACTION_MODEL = "gpt-4o"  # "gpt-4o-mini"
OPENAI_REASONING_MODEL = "gpt-4o"
OPENAI_EXECUTION_MODEL = "gpt-4o"

USER_QUERY = ""  # Make this empty so it'll ask user to input the query
# USER_QUERY = "book a table in wild ginger seattle for 3 people at 7:30pm on 12/24/2024"
# USER_QUERY = "book a table in el gaucho bellevue on 12/28"
# USER_QUERY = "book a table in wild ginger seattle for 2 people at 7pm on 12/11"
# USER_QUERY = "book a table in wild ginger seattle for 1 people at 7pm on 12/24"
# USER_QUERY = "book a table in wild ginger seattle"

GLOBAL_PROMPT_TEMPLATE = SystemMessagePromptTemplate(
    prompt=[
        PromptTemplate.from_file(
            f"./src/global_prompt.md",
            input_variables=[
                "date_today",
            ],
        ),
    ],
)
