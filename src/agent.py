import base64
from io import BytesIO
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from utils import *
from actions import *
from mark_page import annotate
from langgraph.graph import START, StateGraph
from langchain_core.runnables import RunnableLambda
from interfaces import AgentState, ActionResponse
import constants
from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts.chat import MessagesPlaceholder
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_core.prompts import PromptTemplate, StringPromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate


def readPromptTemplate():
    with open(f"./src/prompts/{constants.PROMPT_FILENAME}", "r") as file:
        file_content = file.read()
        return file_content


class Agent:
    def __init__(self):
        # llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=16384)
        llm = ChatOpenAI(model=constants.OPENAI_MODEL, max_tokens=16384)
        llm = llm.with_structured_output(ActionResponse)

        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate(
                    prompt=[
                        PromptTemplate.from_template(readPromptTemplate()),
                    ],
                ),
                MessagesPlaceholder(
                    optional=True,
                    variable_name="scratchpad",
                ),
                SystemMessagePromptTemplate(
                    prompt=[
                        PromptTemplate.from_template(
                            "Then the user will provide: Observation: {{A labeled screenshot Given by User}}")
                    ]
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

        self.agent = annotate | RunnablePassthrough.assign(
            # prediction=format_descriptions | prompt | llm | PydanticOutputParser(pydantic_object=ActionResponse) | parse
            prediction=format_descriptions
            | prompt
            | llm
            | parse
        )

        graph_builder = StateGraph(AgentState)

        graph_builder.add_node("agent", self.agent)
        graph_builder.add_edge(START, "agent")

        graph_builder.add_node("update_scratchpad", update_scratchpad)
        graph_builder.add_edge("update_scratchpad", "agent")

        tools = {
            "Click": click,
            "Type": type_text,
            "ScrollUp": scroll,
            "ScrollDown": scroll,
            "Wait": wait,
            "GoBack": go_back,
            "Search": to_search,
            "SignIn": human_signin,
            "Clarify": ask,
            "Navigate": navigate,
            "Select": select,
        }

        for node_name, tool in tools.items():
            graph_builder.add_node(
                node_name,
                # The lambda ensures the function's string output is mapped to the "observation"
                # key in the AgentState
                RunnableLambda(tool)
                | (lambda observation: {"observation": observation}),
            )
            # Always return to the agent (by means of the update-scratchpad node)
            graph_builder.add_edge(node_name, "update_scratchpad")

        graph_builder.add_conditional_edges("agent", select_tool)

        self.graph = graph_builder.compile()

    async def call_agent(
        self, question: str, browser_context, page, max_steps: int = 150
    ):
        event_stream = self.graph.astream(
            {
                # "page": page,
                "browser": browser_context,
                "input": question,
                "scratchpad": [],
            },
            {
                "recursion_limit": max_steps,
            },
        )
        final_answer = None

        img_count = 0
        steps = []
        async for event in event_stream:
            # We'll display an event stream here
            if "agent" not in event:
                continue
            pred = event["agent"].get("prediction") or {}
            action = pred.get("action")
            action_input = pred.get("args")
            steps.append(f"{len(steps) + 1}. {action}: {action_input}")

            # img_data = base64.b64decode(event["agent"]["img"])
            # img_buffer = BytesIO(img_data)
            # img = Image.open(img_buffer)
            # img.save(f"imgs/img_{img_count}.jpg")
            # img_count += 1

            if action == "ANSWER":
                final_answer = action_input[0]
                # break

        await event_stream.aclose()
        return final_answer
