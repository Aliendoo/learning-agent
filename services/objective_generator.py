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
    
    # Timeline-specific guidance
    timeline_guidance = {
        "1 week": "Focus on essential, foundational concepts only. Keep objectives concise and achievable within 7 days. Prioritize the most important basics.",
        "2 weeks": "Include core concepts with some practical application. Balance theory and practice. Focus on key fundamentals.",
        "1 month": "Comprehensive coverage of fundamentals with hands-on projects. Include both theory and practical skills.",
        "2 months": "Deep dive into concepts with multiple practical applications and projects. Cover intermediate topics.",
        "3 months": "Extensive coverage including advanced topics and real-world applications. Include both breadth and depth.",
        "6+ months": "Complete mastery path with comprehensive theory, advanced techniques, and extensive projects. Full curriculum coverage."
    }
    
    guidance = timeline_guidance.get(timeline, "Comprehensive learning objectives with practical applications.")
    
    prompt = f"""
You are an expert curriculum designer. Generate {state.num_objectives} specific, measurable learning objectives for someone who wants to learn "{state.user_topic}".

Context:
- Current Level: {current_level}
- Goal Level: {goal_level}
- Timeline: {timeline}
- Purpose: {purpose}
- Date: {state.current_date}

Timeline Constraint: {guidance}

Guidelines:
1. Create objectives that progress from basic to advanced concepts
2. Make each objective specific and actionable
3. Ensure objectives build upon each other logically
4. Consider the user's current level and goals
5. Include both theoretical understanding and practical application
6. Respect the timeline constraint - make objectives achievable within the given time

Example format:
- "Understand [concept] and its basic principles"
- "Apply [skill] to create [practical outcome]"
- "Master [advanced technique] for [specific use case]"

Generate exactly {state.num_objectives} learning objectives as a list, appropriate for the {timeline} timeline.
"""

    # Use LLM to generate objectives
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    structured_llm = llm.with_structured_output(ObjectiveList)
    
    result = structured_llm.invoke(prompt)
    
    logging.info(f"\nGenerated {len(result.objectives)} learning objectives for '{state.user_topic}' with {timeline} timeline:")
    for i, obj in enumerate(result.objectives, 1):
        logging.info(f"{i}. {obj}")
    
    return {"learning_objectives": result.objectives}