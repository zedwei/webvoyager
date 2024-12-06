import base64
from io import BytesIO
from prompt_template import prompt
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from utils import *
from actions import *
from mark_page import annotate
from langgraph.graph import START, StateGraph
from langchain_core.runnables import RunnableLambda
from interfaces import AgentState, ActionResponse
from constants import OPENAI_MODEL


class Agent:
    def __init__(self):
        # llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=16384)
        llm = ChatOpenAI(model=OPENAI_MODEL, max_tokens=16384)
        llm = llm.with_structured_output(ActionResponse)

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

        # print(self.graph.get_graph().draw_ascii())

    async def call_agent(self, question: str, browser_context, page, max_steps: int = 150):
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

            img_data = base64.b64decode(event["agent"]["img"])
            img_buffer = BytesIO(img_data)
            img = Image.open(img_buffer)
            img.save(f"imgs/img_{img_count}.jpg")
            img_count += 1

            if action == "ANSWER":
                final_answer = action_input[0]
                # break

        await event_stream.aclose()
        return final_answer
