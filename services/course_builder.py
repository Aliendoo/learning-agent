# services/course_builder.py
"""
Course builder service - organizes objectives and resources into a structured course
"""

import logging
from models import LearningState, PersonalizedCourse, CourseModule
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI

def build_personalized_course(state: LearningState) -> Dict[str, Any]:
    """
    Build a personalized course from learning objectives and their resources.
    """
    logging.info("Building personalized course from objectives and resources")
    
    # Get user preferences for context
    prefs = state.user_preferences
    topic = state.user_topic
    
    # Organize objectives into modules
    modules = _organize_into_modules(state.objective_results, prefs)
    
    # Generate course overview using LLM
    course_overview = _generate_course_overview(topic, modules, prefs)
    
    # Calculate totals
    total_resources = sum(len(module.resources) for module in modules)
    total_time = _calculate_total_time(modules)
    
    # Create final course
    course = PersonalizedCourse(
        title=course_overview["title"],
        description=course_overview["description"],
        total_estimated_time=total_time,
        modules=modules,
        total_resources=total_resources,
        difficulty_progression=course_overview["difficulty_progression"]
    )
    
    logging.info(f"Created course with {len(modules)} modules and {total_resources} resources")
    
    return {"final_course": course}

def _organize_into_modules(objective_results: List, prefs: Dict) -> List[CourseModule]:
    """Organize objectives and resources into logical course modules"""
    
    # Simple approach: group objectives into 3-4 modules based on progression
    num_objectives = len(objective_results)
    if num_objectives <= 3:
        objectives_per_module = 1
    elif num_objectives <= 6:
        objectives_per_module = 2
    else:
        objectives_per_module = 3
    
    modules = []
    current_module_objectives = []
    current_module_resources = []
    
    for i, obj_result in enumerate(objective_results):
        current_module_objectives.append(obj_result.objective)
        current_module_resources.extend(obj_result.resources)
        
        # Create module when we have enough objectives or reach the end
        if len(current_module_objectives) >= objectives_per_module or i == len(objective_results) - 1:
            module = _create_module(
                current_module_objectives, 
                current_module_resources, 
                len(modules) + 1,
                prefs
            )
            modules.append(module)
            
            # Reset for next module
            current_module_objectives = []
            current_module_resources = []
    
    return modules

def _create_module(objectives: List[str], resources: List, module_number: int, prefs: Dict) -> CourseModule:
    """Create a single course module"""
    
    # Determine module progression
    if module_number == 1:
        difficulty = "Beginner"
        module_title = f"Module {module_number}: Fundamentals"
        description_start = "Build a solid foundation"
    elif module_number <= 2:
        difficulty = "Intermediate" 
        module_title = f"Module {module_number}: Core Concepts"
        description_start = "Develop practical skills"
    else:
        difficulty = "Advanced"
        module_title = f"Module {module_number}: Advanced Applications"
        description_start = "Master advanced techniques"
    
    # Estimate time based on resources
    estimated_time = _estimate_module_time(resources)
    
    # Create description
    description = f"{description_start} by learning: {', '.join(objectives)}"
    
    return CourseModule(
        title=module_title,
        description=description,
        estimated_time=estimated_time,
        difficulty=difficulty,
        resources=resources,
        learning_objectives=objectives
    )

def _estimate_module_time(resources: List) -> str:
    """Estimate time for a module based on its resources"""
    if not resources:
        return "1 week"
    
    # Simple estimation based on number of resources
    if len(resources) <= 3:
        return "3-5 days"
    elif len(resources) <= 6:
        return "1 week"
    else:
        return "1-2 weeks"

def _calculate_total_time(modules: List[CourseModule]) -> str:
    """Calculate total course time"""
    total_weeks = len(modules)
    
    if total_weeks <= 2:
        return f"{total_weeks} weeks"
    elif total_weeks <= 4:
        return f"{total_weeks} weeks"
    else:
        return f"{total_weeks}+ weeks"

def _generate_course_overview(topic: str, modules: List[CourseModule], prefs: Dict) -> Dict[str, str]:
    """Generate course title, description, and progression using LLM"""
    
    current_level = prefs.get('current_level', 'beginner')
    goal_level = prefs.get('goal_level', 'intermediate')
    timeline = prefs.get('timeline', '1 month')
    
    # Create module summary for context
    module_summary = "\n".join([f"- {module.title}: {', '.join(module.learning_objectives)}" for module in modules])
    
    prompt = f"""
Create a course overview for a personalized learning course about "{topic}".

Student Profile:
- Current Level: {current_level}
- Goal Level: {goal_level}
- Timeline: {timeline}

Course Structure:
{module_summary}

Generate:
1. An engaging course title
2. A compelling course description (2-3 sentences)
3. A difficulty progression summary

Make it sound professional but approachable. Focus on practical outcomes.

Return as JSON:
{{
    "title": "Course title here",
    "description": "Course description here", 
    "difficulty_progression": "Progression description here"
}}
"""

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        response = llm.invoke(prompt)
        
        # Parse JSON response
        import json
        result = json.loads(response.content)
        return result
        
    except Exception as e:
        logging.warning(f"Failed to generate course overview with LLM: {e}")
        # Fallback to simple generation
        return {
            "title": f"Complete {topic.title()} Learning Path",
            "description": f"A comprehensive course to take you from {current_level} to {goal_level} in {topic} using high-quality educational resources.",
            "difficulty_progression": f"{current_level.title()} to {goal_level.title()}"
        }