from utils import *
from actions import *
from langgraph.graph import START, END, StateGraph
from langchain_core.runnables import RunnableLambda
from interfaces import AgentState
from datetime import datetime
from utils import *

from extraction.extraction_agent import extraction_agent
from reasoning.reasoning_agent import reasoning_agent
from execution.execution_agent import execution_agent


class Agent:

    def __init__(self):
        # Define state extraction LLM call
        self.extraction_agent = extraction_agent()
        self.reasoning_agent = reasoning_agent()
        self.execution_agent = execution_agent()

        graph_builder = StateGraph(AgentState)

        graph_builder.add_node("extraction_agent", self.extraction_agent) # Observe the environment, e.g., query parsing
        graph_builder.add_node("reasoning_agent", self.reasoning_agent) # Reason to generate the action thought
        graph_builder.add_node("execution_agent", self.execution_agent) # Select an action to execute
        graph_builder.add_node("update_scratchpad", update_scratchpad)

        graph_builder.add_edge(START, "extraction_agent")
        graph_builder.add_edge("extraction_agent", "reasoning_agent")
        graph_builder.add_edge("reasoning_agent", "execution_agent")

        graph_builder.add_conditional_edges("execution_agent", select_tool) # Take action, decided at the runtime

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

        """
        The pipeline output of the extraction_agent is the following dictionary:
        {
        "observation": tool execution result
        }
        """
        for node_name, tool in tools.items():
            graph_builder.add_node(
                node_name,
                RunnableLambda(tool)
                | (lambda observation: {"observation": observation}),
            )
            # Question: How/where is "observation" used?
            graph_builder.add_edge(node_name, "update_scratchpad")

        graph_builder.add_edge("update_scratchpad", "extraction_agent")

        self.graph = graph_builder.compile()

    async def call_agent(self, question: str, client, max_steps: int = 150):
        event_stream = self.graph.astream(
            {
                "browser": client,
                "input": question,
                "scratchpad": [],
                "date_today": datetime.today().strftime("%Y-%m-%d"),
            },
            {
                "recursion_limit": max_steps,
            },
        )
        final_answer = None

        async for event in event_stream:
            # We'll display an event stream here
            if "agent" not in event:
                continue
            pred = event["agent"].get("prediction") or {}
            action = pred.get("action")
            action_input = pred.get("args")

            if action == "ANSWER":
                final_answer = action_input[0]
                # break

        await event_stream.aclose()
        return final_answer
