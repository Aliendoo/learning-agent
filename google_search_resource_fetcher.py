# google_search_resource_fetcher.py
"""
Modern Resource Fetcher that fully relies on Google Search API and YouTube API
Replaces all web scraping with API-based resource discovery
"""

import os
import time
from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import streamlit as st
from models import LearningResource
from quality_scorer import QualityScorer

# Load environment variables
load_dotenv()

class GoogleSearchResourceFetcher:
    """
    Modern resource fetcher that uses Google Search API and YouTube API
    Replaces all web scraping with reliable API-based resource discovery
    """
    
    def __init__(self):
        # Google Search API setup
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        # YouTube API setup
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        
        # Initialize services
        if self.google_api_key and self.search_engine_id:
            self.google_service = build("customsearch", "v1", developerKey=self.google_api_key)
        else:
            self.google_service = None
            st.warning("Google Search API credentials not found")
        
        if self.youtube_api_key:
            self.youtube_service = build('youtube', 'v3', developerKey=self.youtube_api_key)
        else:
            self.youtube_service = None
            st.warning("YouTube API credentials not found")
        
        # Quality scorer
        self.quality_scorer = QualityScorer()
    
    def fetch_all_resources(self, topic: str, preferences: Dict) -> Dict[str, List[LearningResource]]:
        """
        Fetch resources from all sources using Google Search API and YouTube API
        
        Args:
            topic: The learning topic
            preferences: User preferences for content type, difficulty, etc.
        
        Returns:
            Dictionary with resources organized by type
        """
        all_resources = {
            'videos': [],
            'articles': [],
            'courses': [],
            'documentation': []
        }
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1. YouTube Videos
            if 'video' in preferences.get('content_format', []):
                status_text.text("🔍 Searching YouTube for educational videos...")
                progress_bar.progress(0.25)
                
                videos = self._fetch_youtube_videos(topic, max_results=6)
                all_resources['videos'] = videos
            
            # 2. Articles via Google Search
            if 'text' in preferences.get('content_format', []):
                status_text.text("📄 Searching for educational articles...")
                progress_bar.progress(0.50)
                
                articles = self._fetch_articles(topic, max_results=6)
                all_resources['articles'] = articles
            
            # 3. Courses via Google Search
            if 'interactive' in preferences.get('content_format', []):
                status_text.text("🎓 Searching for online courses...")
                progress_bar.progress(0.75)
                
                courses = self._fetch_courses(topic, max_results=4)
                all_resources['courses'] = courses
            
            # 4. Documentation via Google Search
            status_text.text("📚 Searching for official documentation...")
            progress_bar.progress(1.0)
            
            documentation = self._fetch_documentation(topic, max_results=3)
            all_resources['documentation'] = documentation
            
            # Clean up progress indicators
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"Error fetching resources: {e}")
            progress_bar.empty()
            status_text.empty()
        
        return all_resources
    
    def _fetch_youtube_videos(self, topic: str, max_results: int = 6) -> List[LearningResource]:
        """Fetch educational videos from YouTube API"""
        if not self.youtube_service:
            return []
        
        try:
            search_query = f"{topic} tutorial learn course education"
            
            search_response = self.youtube_service.search().list(
                q=search_query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='relevance',
                videoDuration='medium',
                videoDefinition='high',
                safeSearch='strict'
            ).execute()
            
            videos = []
            for search_result in search_response.get('items', []):
                video_details = self._get_video_details(search_result['id']['videoId'])
                
                video = LearningResource(
                    type='video',
                    title=search_result['snippet']['title'],
                    url=f"https://www.youtube.com/watch?v={search_result['id']['videoId']}",
                    description=search_result['snippet']['description'][:200] + "...",
                    source=search_result['snippet']['channelTitle'],
                    estimated_time=video_details.get('duration', 'Unknown'),
                    difficulty='Mixed'
                )
                
                # Apply quality scoring
                self.quality_scorer.score_resource(video, topic)
                videos.append(video)
            
            return videos
            
        except HttpError as e:
            st.warning(f"YouTube API error: {e}")
            return []
    
    def _get_video_details(self, video_id: str) -> Dict:
        """Get detailed information about a video"""
        try:
            video_response = self.youtube_service.videos().list(
                part='contentDetails,statistics',
                id=video_id
            ).execute()
            
            if video_response['items']:
                item = video_response['items'][0]
                duration = item['contentDetails']['duration']
                duration_readable = self._parse_duration(duration)
                
                return {'duration': duration_readable}
        except:
            pass
        
        return {}
    
    def _parse_duration(self, duration: str) -> str:
        """Parse ISO 8601 duration to readable format"""
        import re
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration)
        
        if match:
            hours, minutes, seconds = match.groups()
            hours = int(hours) if hours else 0
            minutes = int(minutes) if minutes else 0
            seconds = int(seconds) if seconds else 0
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
        
        return "Unknown"
    
    def _fetch_articles(self, topic: str, max_results: int = 6) -> List[LearningResource]:
        """Fetch educational articles using Google Search API"""
        if not self.google_service:
            return []
        
        try:
            search_query = f'"{topic}" tutorial guide article learn education'
            
            result = self.google_service.cse().list(
                q=search_query,
                cx=self.search_engine_id,
                num=max_results
            ).execute()
            
            articles = []
            if 'items' in result:
                for item in result['items']:
                    # Filter for article-type content
                    if self._is_article_content(item):
                        article = LearningResource(
                            type='article',
                            title=item.get('title', ''),
                            url=item.get('link', ''),
                            description=item.get('snippet', '')[:200] + "...",
                            source=self._extract_source(item.get('link', '')),
                            estimated_time=self._estimate_reading_time(item),
                            difficulty=self._determine_difficulty(item, topic)
                        )
                        
                        # Apply quality scoring
                        self.quality_scorer.score_resource(article, topic)
                        articles.append(article)
            
            return articles
            
        except Exception as e:
            st.warning(f"Google Search for articles failed: {e}")
            return []
    
    def _fetch_courses(self, topic: str, max_results: int = 4) -> List[LearningResource]:
        """Fetch online courses using Google Search API"""
        if not self.google_service:
            return []
        
        try:
            search_query = f'"{topic}" course class lesson curriculum online learning'
            
            result = self.google_service.cse().list(
                q=search_query,
                cx=self.search_engine_id,
                num=max_results
            ).execute()
            
            courses = []
            if 'items' in result:
                for item in result['items']:
                    # Filter for course-type content
                    if self._is_course_content(item):
                        course = LearningResource(
                            type='course',
                            title=item.get('title', ''),
                            url=item.get('link', ''),
                            description=item.get('snippet', '')[:200] + "...",
                            source=self._extract_source(item.get('link', '')),
                            estimated_time='Self-paced',
                            difficulty=self._determine_difficulty(item, topic)
                        )
                        
                        # Apply quality scoring
                        self.quality_scorer.score_resource(course, topic)
                        courses.append(course)
            
            return courses
            
        except Exception as e:
            st.warning(f"Google Search for courses failed: {e}")
            return []
    
    def _fetch_documentation(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Fetch official documentation using Google Search API"""
        if not self.google_service:
            return []
        
        try:
            search_query = f'"{topic}" documentation official guide reference manual'
            
            result = self.google_service.cse().list(
                q=search_query,
                cx=self.search_engine_id,
                num=max_results
            ).execute()
            
            docs = []
            if 'items' in result:
                for item in result['items']:
                    # Filter for documentation-type content
                    if self._is_documentation_content(item):
                        doc = LearningResource(
                            type='documentation',
                            title=item.get('title', ''),
                            url=item.get('link', ''),
                            description=item.get('snippet', '')[:200] + "...",
                            source=self._extract_source(item.get('link', '')),
                            estimated_time='Reference',
                            difficulty='Mixed'
                        )
                        
                        # Apply quality scoring
                        self.quality_scorer.score_resource(doc, topic)
                        docs.append(doc)
            
            return docs
            
        except Exception as e:
            st.warning(f"Google Search for documentation failed: {e}")
            return []
    
    def _is_article_content(self, item: Dict) -> bool:
        """Determine if search result is article content"""
        url = item.get('link', '').lower()
        title = item.get('title', '').lower()
        
        # Exclude video platforms
        if any(platform in url for platform in ['youtube.com', 'youtu.be', 'vimeo.com']):
            return False
        
        # Exclude course platforms (they have their own category)
        if any(platform in url for platform in ['coursera.org', 'udemy.com', 'edx.org', 'khanacademy.org']):
            return False
        
        # Exclude documentation sites
        if any(doc in url for doc in ['docs.', 'documentation', 'api.']):
            return False
        
        # Exclude community/forum sites
        community_sites = [
            'reddit.com', 'stackoverflow.com', 'stackexchange.com', 'quora.com',
            'medium.com/community', 'dev.to', 'hashnode.com', 'hashnode.dev',
            'discord.com', 'slack.com', 'telegram.org', 'facebook.com', 'twitter.com',
            'x.com', 'linkedin.com', 'github.com/discussions', 'github.com/issues'
        ]
        
        if any(site in url for site in community_sites):
            return False
        
        return True
    
    def _is_course_content(self, item: Dict) -> bool:
        """Determine if search result is course content"""
        url = item.get('link', '').lower()
        title = item.get('title', '').lower()
        
        # Look for course platforms (trusted educational platforms only)
        course_platforms = [
            'coursera.org', 'udemy.com', 'edx.org', 'khanacademy.org', 
            'datacamp.com', 'freecodecamp.org', 'theodinproject.com',
            'pluralsight.com', 'skillshare.com', 'codecademy.com', 'teamtreehouse.com',
            'udacity.com', 'mit.edu', 'stanford.edu', 'harvard.edu'
        ]
        
        return any(platform in url for platform in course_platforms)
    
    def _is_documentation_content(self, item: Dict) -> bool:
        """Determine if search result is documentation content"""
        url = item.get('link', '').lower()
        title = item.get('title', '').lower()
        
        # Look for documentation indicators
        doc_indicators = ['docs.', 'documentation', 'api.', 'reference', 'manual', 'guide']
        
        # Exclude community/forum sites from documentation
        community_sites = [
            'reddit.com', 'stackoverflow.com', 'stackexchange.com', 'quora.com',
            'github.com/discussions', 'github.com/issues', 'dev.to', 'hashnode.com'
        ]
        
        if any(site in url for site in community_sites):
            return False
        
        return any(indicator in url or indicator in title for indicator in doc_indicators)
    
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
    
    def _estimate_reading_time(self, item: Dict) -> str:
        """Estimate reading time based on snippet length"""
        snippet = item.get('snippet', '')
        word_count = len(snippet.split())
        
        if word_count < 100:
            return '2-5 min read'
        elif word_count < 300:
            return '5-10 min read'
        elif word_count < 600:
            return '10-15 min read'
        else:
            return '15+ min read'
    
    def _determine_difficulty(self, item: Dict, topic: str) -> str:
        """Determine difficulty level based on title and description"""
        title = item.get('title', '').lower()
        snippet = item.get('snippet', '').lower()
        
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
    
    def filter_resources_by_preferences(self, resources: Dict[str, List[LearningResource]], 
                                      preferences: Dict) -> Dict[str, List[LearningResource]]:
        """
        Filter and rank resources based on user preferences
        Optimized for Google Search API results
        """
        filtered_resources = {}
        
        learning_style = preferences.get('learning_style', [])
        content_format = preferences.get('content_format', [])
        current_level = preferences.get('current_level', 'beginner')
        
        for resource_type, resource_list in resources.items():
            filtered_list = []
            
            for resource in resource_list:
                score = 0
                
                # Score based on content format preference
                if resource_type == 'videos' and 'video' in content_format:
                    score += 3
                elif resource_type == 'articles' and 'text' in content_format:
                    score += 3
                elif resource_type == 'courses' and 'interactive' in content_format:
                    score += 3
                elif resource_type == 'documentation' and 'text' in content_format:
                    score += 2
                
                # Score based on learning style
                if 'visual' in learning_style and resource_type in ['videos', 'courses']:
                    score += 2
                elif 'reading' in learning_style and resource_type in ['articles', 'documentation']:
                    score += 2
                
                # Score based on level appropriateness
                if current_level == 'beginner' and resource.difficulty == 'Beginner':
                    score += 2
                elif current_level == 'intermediate' and resource.difficulty == 'Intermediate':
                    score += 2
                elif current_level == 'advanced' and resource.difficulty == 'Advanced':
                    score += 2
                
                # Add quality score (from Google Search ranking + our scoring)
                final_score = score + (getattr(resource, 'quality_score', 0) * 0.3)
                resource.relevance_score = final_score
                filtered_list.append(resource)
            
            # Sort by final score
            filtered_list.sort(key=lambda x: x.relevance_score, reverse=True)
            filtered_resources[resource_type] = filtered_list[:6]  # Top 6 per category
        
        return filtered_resources 