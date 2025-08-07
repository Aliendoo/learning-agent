# core/learning_graph.py
"""
Learning workflow graph using LangGraph
"""

from models import LearningState
from services.objective_generator import generate_learning_objectives
from services.resource_hunter_spawner import spawn_resource_hunters
from services.educational_resource_finder import find_objective_resources
from services.course_builder import build_personalized_course
from langgraph.graph import START, END, StateGraph

def build_learning_graph() -> StateGraph:
    """
    Build the learning workflow graph that orchestrates the multi-agent course generation.
    
    Flow:
    START → generate_objectives → spawn_hunters → find_resources → build_course → END
    """
    
    builder = StateGraph(LearningState)
    
    # Add nodes
    builder.add_node("generate_objectives", generate_learning_objectives)
    builder.add_node("find_objective_resources", find_objective_resources)
    builder.add_node("build_course", build_personalized_course)
    
    # Add edges
    builder.add_edge(START, "generate_objectives")
    builder.add_conditional_edges("generate_objectives", spawn_resource_hunters, ["find_objective_resources"])
    builder.add_edge("find_objective_resources", "build_course")
    builder.add_edge("build_course", END)
    
    # Compile the graph
    graph = builder.compile()
    return graph