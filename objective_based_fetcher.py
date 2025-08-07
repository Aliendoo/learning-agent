"""
Objective-based resource fetching system
Searches for resources that specifically match learning objectives
"""

from typing import List, Dict, Tuple
from models import LearningResource
from quality_scorer import QualityScorer
from hybrid_resource_fetcher import HybridResourceFetcher
import streamlit as st

class ObjectiveBasedFetcher:
    def __init__(self):
        self.hybrid_fetcher = HybridResourceFetcher()
        self.quality_scorer = QualityScorer()
    
    def fetch_resources_for_objectives(self, learning_objectives: List[str], topic_category: str = "") -> Dict[str, List[LearningResource]]:
        """Fetch resources specifically for each learning objective"""
        
        objective_resources = {}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, objective in enumerate(learning_objectives):
            status_text.text(f"🔍 Searching for resources about: {objective}")
            progress_bar.progress((i + 1) / len(learning_objectives))
            
            # Search for resources specific to this objective
            resources = self._search_for_objective(objective, topic_category)
            
            # Score and rank resources for this objective
            scored_resources = []
            for resource in resources:
                scored_resource = self.quality_scorer.score_resource(resource, topic_category)
                # Add objective relevance score
                scored_resource.relevance_score += self._calculate_objective_relevance(resource, objective)
                scored_resources.append(scored_resource)
            
            # Sort by relevance to this specific objective
            scored_resources.sort(key=lambda x: x.relevance_score, reverse=True)
            
            objective_resources[objective] = scored_resources[:3]  # Top 3 for each objective
        
        progress_bar.empty()
        status_text.empty()
        
        return objective_resources
    
    def _search_for_objective(self, objective: str, topic_category: str) -> List[LearningResource]:
        """Search for resources specific to a learning objective using hybrid fetcher"""
        all_resources = []
        
        # Create specific search queries for this objective
        search_queries = self._generate_search_queries(objective)
        
        # Use hybrid fetcher for each query
        for query in search_queries:
            try:
                # Use hybrid fetcher with preferences for all content types
                preferences = {
                    'content_format': ['video', 'text', 'interactive'],
                    'learning_style': ['visual', 'reading'],
                    'current_level': 'beginner'
                }
                
                resources = self.hybrid_fetcher.fetch_all_resources(query, preferences)
                
                # Add resources to our collection
                all_resources.extend(resources.get('videos', [])[:1])  # Limit to 1 video per query
                all_resources.extend(resources.get('articles', [])[:1])  # Limit to 1 article per query
                all_resources.extend(resources.get('courses', [])[:1])  # Limit to 1 course per query
                
            except Exception as e:
                st.warning(f"Error searching for objective '{objective}': {e}")
                continue
        
        return all_resources
    
    def _generate_search_queries(self, objective: str) -> List[str]:
        """Generate specific search queries for a learning objective"""
        # Extract key concepts from the objective
        objective_lower = objective.lower()
        
        # Create focused search queries
        queries = []
        
        # Direct objective search
        queries.append(objective)
        
        # Extract key terms and create specific queries
        if "variables" in objective_lower:
            queries.extend([
                f"{objective} tutorial",
                f"{objective} examples",
                f"{objective} for beginners"
            ])
        elif "functions" in objective_lower:
            queries.extend([
                f"{objective} tutorial",
                f"{objective} examples",
                f"how to {objective}"
            ])
        elif "oop" in objective_lower or "object" in objective_lower:
            queries.extend([
                f"{objective} tutorial",
                f"{objective} examples",
                f"{objective} concepts"
            ])
        elif "data types" in objective_lower:
            queries.extend([
                f"{objective} tutorial",
                f"{objective} examples",
                f"understanding {objective}"
            ])
        elif "basic concepts" in objective_lower or "fundamentals" in objective_lower:
            queries.extend([
                f"python basics tutorial",
                f"python fundamentals for beginners",
                f"introduction to python programming"
            ])
        elif "terminology" in objective_lower or "principles" in objective_lower:
            queries.extend([
                f"python programming concepts",
                f"python terminology guide",
                f"python programming principles"
            ])
        elif "applications" in objective_lower or "use cases" in objective_lower:
            queries.extend([
                f"python programming applications",
                f"python use cases examples",
                f"what can you do with python"
            ])
        elif "apply" in objective_lower or "practice" in objective_lower:
            queries.extend([
                f"python programming practice",
                f"python hands-on exercises",
                f"python practical examples"
            ])
        elif "projects" in objective_lower or "hands-on" in objective_lower:
            queries.extend([
                f"python programming projects",
                f"python hands-on projects",
                f"python project tutorials"
            ])
        elif "skills" in objective_lower or "development" in objective_lower:
            queries.extend([
                f"python programming skills",
                f"python development tutorial",
                f"python programming practice"
            ])
        elif "advanced" in objective_lower or "master" in objective_lower:
            queries.extend([
                f"advanced python programming",
                f"python advanced techniques",
                f"master python programming"
            ])
        elif "best practices" in objective_lower:
            queries.extend([
                f"python best practices",
                f"python programming best practices",
                f"python coding standards"
            ])
        elif "expert" in objective_lower or "professional" in objective_lower:
            queries.extend([
                f"expert python programming",
                f"professional python development",
                f"python expert level"
            ])
        else:
            # Generic approach for other objectives - extract topic and create specific queries
            topic = self._extract_topic_from_objective(objective)
            if topic:
                queries.extend([
                    f"{topic} tutorial",
                    f"{topic} programming guide",
                    f"learn {topic} programming",
                    f"{topic} examples"
                ])
            else:
                # Fallback to generic queries
                queries.extend([
                    f"{objective} tutorial",
                    f"{objective} guide",
                    f"learn {objective}",
                    f"{objective} examples"
                ])
        
        return queries[:4]  # Limit to 4 queries per objective
    
    def _calculate_objective_relevance(self, resource: LearningResource, objective: str) -> float:
        """Calculate how relevant a resource is to a specific objective"""
        relevance_score = 0.0
        
        # Check title relevance
        title_lower = resource.title.lower()
        objective_lower = objective.lower()
        
        # Extract key terms from objective
        objective_terms = self._extract_key_terms(objective)
        
        # Score based on title matches
        for term in objective_terms:
            if term in title_lower:
                relevance_score += 2.0
        
        # Score based on description matches
        if hasattr(resource, 'description') and resource.description:
            desc_lower = resource.description.lower()
            for term in objective_terms:
                if term in desc_lower:
                    relevance_score += 1.0
        
        # Bonus for exact phrase matches
        if objective_lower in title_lower:
            relevance_score += 3.0
        
        # Bonus for tutorial/guide content
        tutorial_words = ['tutorial', 'guide', 'learn', 'understand', 'explain']
        if any(word in title_lower for word in tutorial_words):
            relevance_score += 1.0
        
        return relevance_score
    
    def _extract_key_terms(self, objective: str) -> List[str]:
        """Extract key terms from a learning objective"""
        # Remove common words and extract meaningful terms
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall'}
        
        words = objective.lower().split()
        key_terms = [word for word in words if word not in common_words and len(word) > 2]
        
        # Add multi-word terms
        if "data types" in objective.lower():
            key_terms.append("data types")
        if "object oriented" in objective.lower():
            key_terms.append("object oriented")
        if "oop" in objective.lower():
            key_terms.append("oop")
        
        return key_terms
    
    def _extract_topic_from_objective(self, objective: str) -> str:
        """Extract the main topic from a learning objective"""
        objective_lower = objective.lower()
        
        # Common programming topics
        topics = [
            'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'swift',
            'html', 'css', 'sql', 'react', 'angular', 'vue', 'node', 'django', 'flask',
            'machine learning', 'data science', 'web development', 'mobile development',
            'database', 'api', 'testing', 'deployment', 'git', 'docker', 'kubernetes'
        ]
        
        for topic in topics:
            if topic in objective_lower:
                return topic
        
        # If no specific topic found, try to extract from common patterns
        if 'programming' in objective_lower:
            return 'programming'
        elif 'development' in objective_lower:
            return 'development'
        elif 'coding' in objective_lower:
            return 'coding'
        
        return None
    
    def assign_resources_to_modules(self, course: 'PersonalizedCourse', objective_resources: Dict[str, List[LearningResource]]) -> 'PersonalizedCourse':
        """Assign the most relevant resources to each module based on learning objectives"""
        
        for module in course.modules:
            module_resources = []
            
            # For each learning objective in this module
            for objective in module.learning_objectives:
                if objective in objective_resources and objective_resources[objective]:
                    # Get the best resource for this objective
                    best_resource = objective_resources[objective][0]
                    
                    # Add null check to prevent AttributeError
                    if best_resource is not None:
                        # Add objective information to the resource
                        best_resource.objective_match = objective
                        module_resources.append(best_resource)
            
            # Update module with matched resources
            module.resources = module_resources
        
        return course 