# services/objective_generator.py
"""
Learning objective generator service
"""

import logging
from models import LearningState
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class ObjectiveList(BaseModel):
    objectives: List[str]

def generate_learning_objectives(state: LearningState) -> Dict[str, Any]:
    """
    Generate learning objectives based on user's topic and preferences using an LLM.
    """
    
    # Extract preferences for context
    prefs = state.user_preferences
    current_level = prefs.get('current_level', 'beginner')
    goal_level = prefs.get('goal_level', 'intermediate') 
    timeline = prefs.get('timeline', '1 month')
    purpose = prefs.get('purpose', 'general learning')
    
    prompt = f"""
You are an expert curriculum designer. Generate {state.num_objectives} specific, measurable learning objectives for someone who wants to learn "{state.user_topic}".

Context:
- Current Level: {current_level}
- Goal Level: {goal_level}
- Timeline: {timeline}
- Purpose: {purpose}
- Date: {state.current_date}

Guidelines:
1. Create objectives that progress from basic to advanced concepts
2. Make each objective specific and actionable
3. Ensure objectives build upon each other logically
4. Consider the user's current level and goals
5. Include both theoretical understanding and practical application

Example format:
- "Understand [concept] and its basic principles"
- "Apply [skill] to create [practical outcome]"
- "Master [advanced technique] for [specific use case]"

Generate exactly {state.num_objectives} learning objectives as a list.
"""

    # Use LLM to generate objectives
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    structured_llm = llm.with_structured_output(ObjectiveList)
    
    result = structured_llm.invoke(prompt)
    
    logging.info(f"\nGenerated {len(result.objectives)} learning objectives for '{state.user_topic}':")
    for i, obj in enumerate(result.objectives, 1):
        logging.info(f"{i}. {obj}")
    
    return {"learning_objectives": result.objectives}