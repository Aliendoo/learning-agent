# services/educational_resource_finder.py
"""
Educational resource finder using Tavily search
"""

import logging
from models import LearningResource, ObjectiveResult
from typing import Dict, Any, List
from tavily import TavilyClient
import re

def find_objective_resources(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find educational resources for a specific learning objective using Tavily search.
    This function represents a single agent that searches for resources for one objective.
    """
    objective = data["objective"]
    user_topic = data["user_topic"]
    user_preferences = data["user_preferences"]
    current_date = data["current_date"]
    
    logging.info(f"Searching for resources for objective: {objective}")
    
    # Initialize Tavily client
    tavily_client = TavilyClient()
    
    # Create educational search queries for this objective
    search_queries = _generate_educational_queries(objective, user_topic)
    
    all_resources = []
    
    for query in search_queries:
        try:
            # Search with Tavily
            results = tavily_client.search(
                query=query,
                max_results=3,  # Get 3 results per query
                include_domains=_get_educational_domains(),
                exclude_domains=_get_excluded_domains()
            )
            
            # Convert search results to LearningResource objects
            for result in results.get("results", []):
                resource = _convert_to_learning_resource(result, objective)
                if resource and _is_educational_content(resource):
                    all_resources.append(resource)
                    
        except Exception as e:
            logging.warning(f"Search failed for query '{query}': {e}")
            continue
    
    # Remove duplicates and select best resources
    unique_resources = _remove_duplicates(all_resources)
    best_resources = _select_best_resources(unique_resources, max_resources=4)
    
    # Create ObjectiveResult
    objective_result = ObjectiveResult(
        objective=objective,
        resources=best_resources
    )
    
    logging.info(f"Found {len(best_resources)} resources for objective: {objective}")
    
    return {"objective_results": [objective_result]}

def _generate_educational_queries(objective: str, topic: str) -> List[str]:
    """Generate search queries optimized for educational content"""
    queries = []
    
    # Direct objective search with educational keywords
    queries.append(f"{objective} tutorial learn course")
    queries.append(f"{topic} {objective} guide education")
    
    # Extract key terms for more targeted searches
    key_terms = _extract_key_terms(objective)
    if key_terms:
        queries.append(f"{topic} {' '.join(key_terms[:2])} tutorial")
    
    return queries[:3]  # Limit to 3 queries per objective

def _extract_key_terms(objective: str) -> List[str]:
    """Extract meaningful terms from learning objective"""
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = re.findall(r'\b\w+\b', objective.lower())
    return [word for word in words if word not in stop_words and len(word) > 2]

def _convert_to_learning_resource(search_result: Dict, objective: str) -> LearningResource:
    """Convert Tavily search result to LearningResource"""
    try:
        # Determine resource type based on URL and content
        url = search_result.get("url", "")
        title = search_result.get("title", "")
        
        resource_type = _determine_resource_type(url, title)
        difficulty = _determine_difficulty(title, search_result.get("content", ""))
        estimated_time = _estimate_time(resource_type, search_result.get("content", ""))
        
        return LearningResource(
            type=resource_type,
            title=title,
            url=url,
            description=search_result.get("content", "")[:200] + "...",
            source=_extract_source(url),
            estimated_time=estimated_time,
            difficulty=difficulty,
            objective_match=objective,
            relevance_score=_calculate_relevance(search_result, objective)
        )
    except Exception as e:
        logging.warning(f"Failed to convert search result: {e}")
        return None

def _determine_resource_type(url: str, title: str) -> str:
    """Determine the type of educational resource"""
    url_lower = url.lower()
    title_lower = title.lower()
    
    if any(domain in url_lower for domain in ['youtube.com', 'youtu.be', 'vimeo.com']):
        return 'video'
    elif any(domain in url_lower for domain in ['coursera.org', 'udemy.com', 'edx.org', 'khanacademy.org']):
        return 'course'
    elif any(term in url_lower for term in ['docs.', 'documentation', 'reference']):
        return 'documentation'
    else:
        return 'article'

def _determine_difficulty(title: str, content: str) -> str:
    """Determine difficulty level from title and content"""
    text = f"{title} {content}".lower()
    
    if any(word in text for word in ['beginner', 'intro', 'basic', 'getting started']):
        return 'Beginner'
    elif any(word in text for word in ['advanced', 'expert', 'deep dive', 'master']):
        return 'Advanced'
    elif any(word in text for word in ['intermediate', 'practical']):
        return 'Intermediate'
    else:
        return 'Mixed'

def _estimate_time(resource_type: str, content: str) -> str:
    """Estimate time based on resource type and content"""
    if resource_type == 'video':
        return '10-30 min'
    elif resource_type == 'course':
        return '2-8 hours'
    elif resource_type == 'article':
        word_count = len(content.split())
        if word_count < 500:
            return '5-10 min read'
        elif word_count < 1500:
            return '10-20 min read'
        else:
            return '20+ min read'
    else:
        return 'Variable'

def _extract_source(url: str) -> str:
    """Extract source name from URL"""
    try:
        domain = url.split('//')[1].split('/')[0]
        domain = domain.replace('www.', '')
        return domain.split('.')[0].title()
    except:
        return 'Unknown'

def _calculate_relevance(search_result: Dict, objective: str) -> float:
    """Calculate relevance score based on title and content match"""
    title = search_result.get("title", "").lower()
    content = search_result.get("content", "").lower()
    objective_lower = objective.lower()
    
    score = 0.0
    
    # Title relevance (higher weight)
    objective_words = objective_lower.split()
    for word in objective_words:
        if word in title:
            score += 2.0
        if word in content:
            score += 1.0
    
    # Bonus for educational keywords
    educational_terms = ['tutorial', 'guide', 'learn', 'course', 'lesson']
    for term in educational_terms:
        if term in title:
            score += 1.0
    
    return min(score, 10.0)  # Cap at 10

def _is_educational_content(resource: LearningResource) -> bool:
    """Filter for educational content quality"""
    url_lower = resource.url.lower()
    title_lower = resource.title.lower()
    
    # Exclude non-educational sites
    excluded_indicators = ['forum', 'discussion', 'chat', 'social']
    if any(indicator in url_lower for indicator in excluded_indicators):
        return False
    
    # Require minimum relevance score
    return resource.relevance_score >= 2.0

def _remove_duplicates(resources: List[LearningResource]) -> List[LearningResource]:
    """Remove duplicate resources based on URL"""
    seen_urls = set()
    unique_resources = []
    
    for resource in resources:
        if resource.url not in seen_urls:
            unique_resources.append(resource)
            seen_urls.add(resource.url)
    
    return unique_resources

def _select_best_resources(resources: List[LearningResource], max_resources: int = 4) -> List[LearningResource]:
    """Select the best resources based on relevance score and diversity"""
    # Sort by relevance score
    sorted_resources = sorted(resources, key=lambda x: x.relevance_score, reverse=True)
    
    # Ensure diversity of resource types
    selected = []
    type_counts = {'video': 0, 'article': 0, 'course': 0, 'documentation': 0}
    max_per_type = 2
    
    for resource in sorted_resources:
        if len(selected) >= max_resources:
            break
        
        if type_counts[resource.type] < max_per_type:
            selected.append(resource)
            type_counts[resource.type] += 1
    
    # Fill remaining slots with best remaining resources
    remaining = max_resources - len(selected)
    for resource in sorted_resources:
        if remaining <= 0:
            break
        if resource not in selected:
            selected.append(resource)
            remaining -= 1
    
    return selected

def _get_educational_domains() -> List[str]:
    """Get list of preferred educational domains"""
    return [
        "youtube.com", "coursera.org", "edx.org", "udemy.com", "khanacademy.org",
        "freecodecamp.org", "codecademy.com", "pluralsight.com", "skillshare.com",
        "medium.com", "towards-data-science.com", "dev.to", "realpython.com",
        "w3schools.com", "mdn.mozilla.org", "docs.python.org"
    ]

def _get_excluded_domains() -> List[str]:
    """Get list of domains to exclude from search"""
    return [
        "reddit.com", "stackoverflow.com", "quora.com", "facebook.com", 
        "twitter.com", "linkedin.com", "pinterest.com"
    ]