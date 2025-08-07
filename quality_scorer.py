"""
Universal quality scoring system for learning resources
"""

from typing import List, Dict
from models import LearningResource
import re
from datetime import datetime

class QualityScorer:
    def __init__(self):
        # Recognized organizations for health/wellness topics
        self.recognized_organizations = {
            'fitness': ['nike', 'adidas', 'under armour', 'crossfit', 'ace', 'nasm', 'acsm'],
            'yoga': ['yoga alliance', 'yoga journal', 'doyogawithme', 'yoga international'],
            'meditation': ['headspace', 'calm', 'insight timer', 'mindful.org'],
            'nutrition': ['who', 'usda', 'academy of nutrition', 'harvard health'],
            'mental_health': ['apa', 'nami', 'mayo clinic', 'who mental health']
        }
        
        # Source credibility scoring
        self.source_credibility_scores = {
            'official': 10,      # Government, academic institutions
            'recognized': 9,     # Recognized organizations
            'established': 8,    # Coursera, edX, Khan Academy
            'professional': 7,   # Industry associations
            'popular': 6,        # Medium, verified YouTube
            'community': 5       # Personal blogs, unverified
        }
    
    def score_resource(self, resource: LearningResource, topic_category: str = "") -> LearningResource:
        """Score a resource across all quality dimensions"""
        
        # Score each dimension
        credibility_score = self._score_credibility(resource, topic_category)
        engagement_score = self._score_engagement(resource)
        depth_score = self._score_depth(resource)
        recency_score = self._score_recency(resource)
        
        # Calculate weighted total score
        total_score = (credibility_score * 0.4) + (engagement_score * 0.25) + (depth_score * 0.2) + (recency_score * 0.15)
        
        # Add safety warnings for health/wellness topics
        safety_warnings = self._get_safety_warnings(resource, topic_category)
        
        # Update resource with scores
        resource.quality_score = round(total_score, 2)
        resource.credibility_score = round(credibility_score, 2)
        resource.engagement_score = round(engagement_score, 2)
        resource.depth_score = round(depth_score, 2)
        resource.recency_score = round(recency_score, 2)
        resource.safety_warnings = safety_warnings
        resource.topic_category = topic_category
        
        return resource
    
    def _score_credibility(self, resource: LearningResource, topic_category: str) -> float:
        """Score source credibility (40% weight)"""
        source_lower = resource.source.lower()
        url_lower = resource.url.lower()
        
        # Check for official sources
        if any(domain in url_lower for domain in ['.gov', '.edu', 'official', 'docs.']):
            resource.source_credibility = "official"
            return 10.0
        
        # Check for recognized organizations (especially for health/wellness)
        if topic_category == "health_wellness":
            for category, orgs in self.recognized_organizations.items():
                if any(org in source_lower or org in url_lower for org in orgs):
                    resource.source_credibility = "recognized"
                    return 9.0
        
        # Check for established platforms
        established_platforms = ['coursera', 'edx', 'khan academy', 'masterclass', 'skillshare', 'udemy']
        if any(platform in source_lower or platform in url_lower for platform in established_platforms):
            resource.source_credibility = "established"
            return 8.0
        
        # Check for professional organizations
        professional_keywords = ['association', 'institute', 'foundation', 'certified', 'accredited']
        if any(keyword in source_lower for keyword in professional_keywords):
            resource.source_credibility = "professional"
            return 7.0
        
        # Check for popular community platforms
        popular_platforms = ['medium', 'dev.to', 'youtube', 'reddit']
        if any(platform in source_lower or platform in url_lower for platform in popular_platforms):
            resource.source_credibility = "popular"
            return 6.0
        
        # Default to community
        resource.source_credibility = "community"
        return 5.0
    
    def _score_engagement(self, resource: LearningResource) -> float:
        """Score engagement metrics (25% weight)"""
        # This is a simplified scoring - in a real implementation, you'd fetch actual metrics
        title_lower = resource.title.lower()
        description_lower = resource.description.lower()
        
        # Score based on content type and indicators
        if resource.type == 'video':
            # Videos typically have good engagement
            if any(word in title_lower for word in ['tutorial', 'guide', 'how to', 'learn']):
                return 8.0
            return 7.0
        
        elif resource.type == 'course':
            # Courses have structured engagement
            if 'comprehensive' in description_lower or 'complete' in description_lower:
                return 9.0
            return 8.0
        
        elif resource.type == 'article':
            # Articles vary in engagement
            if any(word in title_lower for word in ['complete', 'comprehensive', 'ultimate']):
                return 8.0
            elif any(word in title_lower for word in ['tutorial', 'guide', 'how to']):
                return 7.0
            return 6.0
        
        return 5.0
    
    def _score_depth(self, resource: LearningResource) -> float:
        """Score content depth (20% weight)"""
        title_lower = resource.title.lower()
        description_lower = resource.description.lower()
        
        # Comprehensive content
        if any(word in title_lower or word in description_lower 
               for word in ['complete', 'comprehensive', 'full', 'ultimate', 'master']):
            return 10.0
        
        # Series or collection
        if any(word in title_lower for word in ['series', 'collection', 'part', 'episode']):
            return 8.0
        
        # Detailed tutorial
        if any(word in title_lower for word in ['tutorial', 'guide', 'how to', 'learn']):
            return 6.0
        
        # Quick guide or tip
        if any(word in title_lower for word in ['tip', 'quick', 'basics', 'intro']):
            return 4.0
        
        return 5.0
    
    def _score_recency(self, resource: LearningResource) -> float:
        """Score content recency (15% weight)"""
        # This is a simplified scoring - in a real implementation, you'd parse actual dates
        title_lower = resource.title.lower()
        description_lower = resource.description.lower()
        
        # Check for year indicators
        current_year = datetime.now().year
        
        # Look for year mentions
        year_pattern = r'\b(20[12]\d)\b'
        years = re.findall(year_pattern, title_lower + ' ' + description_lower)
        
        if years:
            year = int(years[0])
            if year == current_year:
                return 10.0
            elif year >= current_year - 2:
                return 8.0
            elif year >= current_year - 5:
                return 6.0
            else:
                return 4.0
        
        # If no year found, assume recent if it's from established platforms
        if resource.source_credibility in ['official', 'recognized', 'established']:
            return 7.0
        
        return 5.0
    
    def _get_safety_warnings(self, resource: LearningResource, topic_category: str) -> List[str]:
        """Get appropriate safety warnings based on topic category"""
        warnings = []
        
        if topic_category == "health_wellness":
            if any(word in resource.title.lower() for word in ['exercise', 'workout', 'fitness', 'yoga']):
                warnings.append("Consult your doctor before starting any new exercise program.")
            elif any(word in resource.title.lower() for word in ['meditation', 'mental health', 'therapy']):
                warnings.append("This is not a substitute for professional medical advice.")
            elif any(word in resource.title.lower() for word in ['nutrition', 'diet', 'supplements']):
                warnings.append("Consult a healthcare provider for personalized nutrition advice.")
        
        elif topic_category == "technical":
            if any(word in resource.title.lower() for word in ['database', 'server', 'production']):
                warnings.append("Backup your data before making system changes.")
            elif any(word in resource.title.lower() for word in ['security', 'authentication']):
                warnings.append("Test security implementations in a safe environment.")
        
        elif topic_category == "creative":
            if any(word in resource.title.lower() for word in ['painting', 'art', 'crafts']):
                warnings.append("Use appropriate materials and ensure proper ventilation.")
        
        return warnings 