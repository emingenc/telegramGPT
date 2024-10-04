from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
from conf import llm
from state import GraphState
from nodes import nodes, options_str
from enum import Enum
import logging


logger = logging.getLogger(__name__)

next_steps = {key: key for key in nodes.keys()}
next_step_enums = Enum("NextStep", next_steps)

# Define the QueryAssessment model
class QueryAssessment(BaseModel):
    next_step: next_step_enums = Field(description="The next step to take")
    confidence: float = Field(
        description="Confidence score for the chosen next step (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )

# Assessment function
def assess_query(state: GraphState) -> GraphState:
    question = state.question
    prompt_template = """
    Determine the most appropriate next step based on the user's question and chat history.

    Options:
    {options}

    Question:
    {question}
    choose best option for question.
    respond Only JSON format output.
    {{'next_step': selected_option, 'confidence': confidence}}
    {format_instructions}
    Only JSON:"""

    parser = JsonOutputParser(pydantic_object=QueryAssessment)
    assessment_prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["options", "question"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    assessment_chain = assessment_prompt | llm | parser

    try:
        assessment = assessment_chain.invoke(
            {"options": options_str, "question": question}
        )
        print(assessment)
        state.next_step = assessment.get("next_step", END)
        confidence = assessment.get("confidence", 0.0)
        logger.info(
            f"Determined next step: {state.next_step} with confidence: {confidence}"
        )

        return state

    except Exception as e:
        logger.error(f"Error in assessing query: {str(e)}")
        return state


def decide_next_step(state: GraphState) -> GraphState:
    next_step = state.next_step
    print(f"Next step: {next_step}")
    return next_step


# Create the graph
def create_graph(nodes: Dict[str, Dict[str, Any]]) -> StateGraph:
    workflow = StateGraph(GraphState)

    # Add assessment node
    workflow.add_node("assess", assess_query)

    # Add nodes
    for node_name, node_data in nodes.items():
        workflow.add_node(node_name, node_data["node"])

    # Add edges
    workflow.set_entry_point("assess")

    edges = {key: key for key in nodes.keys()} 

    workflow.add_conditional_edges(
        "assess",
        decide_next_step,
        edges,
    )
    for node_name, node_data in nodes.items():
        workflow.add_edge(node_name, END)

    return workflow


# Create and compile the graph
graph = create_graph(nodes)
app = graph.compile()