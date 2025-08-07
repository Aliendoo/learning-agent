# services/resource_hunter_spawner.py
"""
Resource hunter spawner - creates parallel agents for each learning objective
"""

import logging
from models import LearningState
from typing import List
from langgraph.types import Send

def spawn_resource_hunters(state: LearningState) -> List[Send]:
    """
    Spawn parallel resource hunter agents for each learning objective.
    Each agent will search for educational resources for their specific objective.
    """
    logging.info(f"Spawning {len(state.learning_objectives)} parallel resource hunter agents")
    
    return [
        Send("find_objective_resources", {
            "objective": objective,
            "user_topic": state.user_topic,
            "user_preferences": state.user_preferences,
            "current_date": state.current_date
        }) 
        for objective in state.learning_objectives
    ]