# google_search_integration.py
"""
Standalone Google Search API integration for Learning Agent
This module can be easily integrated into existing resource fetchers
"""

import os
import time
from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from models import LearningResource
from quality_scorer import QualityScorer

# Load environment variables
load_dotenv()

class GoogleSearchIntegration:
    """
    Google Search API integration that can replace web scraping methods
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.quality_scorer = QualityScorer()
        
        if not self.api_key or not self.search_engine_id:
            print("Warning: Google Search API credentials not found. Using fallback methods.")
            self.available = False
        else:
            self.available = True
            self.service = build("customsearch", "v1", developerKey=self.api_key)
    
    def search_educational_resources(self, topic: str, max_results: int = 10, 
                                   resource_type: str = 'all') -> List[LearningResource]:
        """
        Search for educational resources using Google Custom Search API
        Replaces web scraping methods with more reliable API-based search
        """
        if not self.available:
            return []
        
        try:
            # Prepare search query
            search_query = self._prepare_search_query(topic, resource_type)
            
            # Execute search
            search_results = []
            remaining_results = max_results
            
            # Google Custom Search API returns max 10 results per request
            for start_index in range(1, max_results + 1, 10):
                if remaining_results <= 0:
                    break
                
                current_max = min(10, remaining_results)
                
                try:
                    # Use general search (site restrictions are too limiting)
                    result = self.service.cse().list(
                        q=search_query,
                        cx=self.search_engine_id,
                        start=start_index,
                        num=current_max
                    ).execute()
                    
                    if 'items' in result:
                        search_results.extend(result['items'])
                        remaining_results -= len(result['items'])
                    
                    # Be respectful to API limits
                    time.sleep(0.1)
                    
                except HttpError as e:
                    print(f"Google Search API error: {e}")
                    break
            
            # Convert to LearningResource objects
            resources = self._convert_to_learning_resources(search_results, topic)
            
            # Apply quality scoring
            for resource in resources:
                self.quality_scorer.score_resource(resource, topic)
            
            return resources[:max_results]
            
        except Exception as e:
            print(f"Error searching Google: {e}")
            return []
    
    def _prepare_search_query(self, topic: str, resource_type: str) -> str:
        """Prepare search query with educational context"""
        base_query = f'"{topic}" tutorial learn course education'
        
        if resource_type == 'video':
            base_query += ' video tutorial youtube'
        elif resource_type == 'article':
            base_query += ' article guide documentation'
        elif resource_type == 'course':
            base_query += ' course class lesson curriculum'
        
        return base_query
    
    def _convert_to_learning_resources(self, search_results: List[Dict], 
                                     original_query: str) -> List[LearningResource]:
        """Convert Google search results to LearningResource objects"""
        resources = []
        
        for result in search_results:
            # Determine resource type based on URL and title
            resource_type = self._determine_resource_type(result)
            
            # Extract estimated time
            estimated_time = self._estimate_reading_time(result)
            
            # Extract difficulty level
            difficulty = self._determine_difficulty(result, original_query)
            
            # Create LearningResource
            resource = LearningResource(
                type=resource_type,
                title=result.get('title', ''),
                url=result.get('link', ''),
                description=result.get('snippet', '')[:200] + "...",
                source=self._extract_source(result.get('link', '')),
                estimated_time=estimated_time,
                difficulty=difficulty
            )
            
            resources.append(resource)
        
        return resources
    
    def _determine_resource_type(self, result: Dict) -> str:
        """Determine the type of resource based on URL and title"""
        url = result.get('link', '').lower()
        title = result.get('title', '').lower()
        
        # Check for video platforms
        if any(platform in url for platform in ['youtube.com', 'youtu.be', 'vimeo.com']):
            return 'video'
        
        # Check for course platforms
        if any(platform in url for platform in ['coursera.org', 'udemy.com', 'edx.org', 'khanacademy.org']):
            return 'course'
        
        # Check for documentation
        if any(doc in url for doc in ['docs.', 'documentation', 'api.']):
            return 'documentation'
        
        # Default to article
        return 'article'
    
    def _estimate_reading_time(self, result: Dict) -> str:
        """Estimate reading time based on snippet length"""
        snippet = result.get('snippet', '')
        word_count = len(snippet.split())
        
        if word_count < 100:
            return '2-5 min read'
        elif word_count < 300:
            return '5-10 min read'
        elif word_count < 600:
            return '10-15 min read'
        else:
            return '15+ min read'
    
    def _determine_difficulty(self, result: Dict, original_query: str) -> str:
        """Determine difficulty level based on title and description"""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        # Check for beginner indicators
        if any(word in title or word in snippet 
               for word in ['beginner', 'intro', 'basic', 'getting started', 'first time']):
            return 'Beginner'
        
        # Check for advanced indicators
        if any(word in title or word in snippet 
               for word in ['advanced', 'expert', 'deep dive', 'masterclass']):
            return 'Advanced'
        
        # Check for intermediate indicators
        if any(word in title or word in snippet 
               for word in ['intermediate', 'practical', 'hands-on', 'project']):
            return 'Intermediate'
        
        return 'Mixed'
    
    def _extract_source(self, url: str) -> str:
        """Extract source name from URL"""
        if not url:
            return 'Unknown'
        
        # Remove protocol and www
        domain = url.replace('https://', '').replace('http://', '').replace('www.', '')
        
        # Extract domain name
        domain_parts = domain.split('/')[0].split('.')
        
        if len(domain_parts) >= 2:
            return domain_parts[-2].title()
        
        return domain.split('/')[0].title()

# Convenience functions for easy integration
def get_google_search_results(topic: str, max_results: int = 8) -> List[LearningResource]:
    """
    Convenience function to get Google Search results
    Use this to replace web scraping methods
    """
    integration = GoogleSearchIntegration()
    return integration.search_educational_resources(topic, max_results)

def get_google_articles(topic: str, max_results: int = 6) -> List[LearningResource]:
    """
    Get articles specifically from Google Search
    Replaces: EducationalArticleScraper.search_educational_articles()
    """
    integration = GoogleSearchIntegration()
    return integration.search_educational_resources(topic, max_results, 'article')

def get_google_courses(topic: str, max_results: int = 4) -> List[LearningResource]:
    """
    Get courses specifically from Google Search
    Replaces: CoursePlatformFetcher.search_all_platforms()
    """
    integration = GoogleSearchIntegration()
    return integration.search_educational_resources(topic, max_results, 'course')

def get_google_documentation(topic: str, max_results: int = 3) -> List[LearningResource]:
    """
    Get documentation specifically from Google Search
    Replaces: OfficialDocumentationFetcher.search_official_docs()
    """
    integration = GoogleSearchIntegration()
    return integration.search_educational_resources(f'{topic} documentation official guide', max_results, 'documentation') 