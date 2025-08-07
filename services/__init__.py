"""
Services package for the Learning Agent

This package contains all the individual services that make up the multi-agent workflow:
- objective_generator: Generates learning objectives from user input
- resource_hunter_spawner: Creates parallel agents for resource discovery
- educational_resource_finder: Finds educational resources using Tavily search
- course_builder: Organizes resources into a structured course
"""

from .objective_generator import generate_learning_objectives
from .resource_hunter_spawner import spawn_resource_hunters
from .educational_resource_finder import find_objective_resources
from .course_builder import build_personalized_course

__all__ = [
    "generate_learning_objectives",
    "spawn_resource_hunters", 
    "find_objective_resources",
    "build_personalized_course"
]