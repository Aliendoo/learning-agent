# hybrid_resource_fetcher.py
"""
Hybrid Resource Fetcher - Phase 1A Testing
Uses Google Search API for articles only, keeps existing methods for everything else
Includes rate limiting and fallback mechanisms
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
from educational_site_scraper import EducationalSiteScraper

# Load environment variables
load_dotenv()

class HybridResourceFetcher:
    """
    Hybrid resource fetcher for safe testing
    - Articles: Google Search API (with fallback)
    - Videos: YouTube API (existing)
    - Courses: Existing scrapers (fallback)
    - Documentation: Existing scrapers (fallback)
    """
    
    def __init__(self):
        # Google Search API setup
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        # YouTube API setup (keep existing)
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        
        # Initialize services
        if self.google_api_key and self.search_engine_id:
            self.google_service = build("customsearch", "v1", developerKey=self.google_api_key)
            self.google_available = True
        else:
            self.google_service = None
            self.google_available = False
            st.warning("Google Search API credentials not found - using fallback methods")
        
        if self.youtube_api_key:
            self.youtube_service = build('youtube', 'v3', developerKey=self.youtube_api_key)
            self.youtube_available = True
        else:
            self.youtube_service = None
            self.youtube_available = False
            st.warning("YouTube API credentials not found")
        
        # Quality scorer
        self.quality_scorer = QualityScorer()
        
        # Web scraping fallback
        self.web_scraper = EducationalSiteScraper()
        
        # Rate limiting
        self.daily_query_count = 0
        self.max_daily_queries = 50  # Conservative limit to stay well under 100/day
        self.last_query_time = 0
        self.min_query_interval = 0.1  # 100ms between queries
    
    def fetch_all_resources(self, topic: str, preferences: Dict) -> Dict[str, List[LearningResource]]:
        """
        Fetch resources using hybrid approach
        Articles: Google Search API (with fallback)
        Everything else: Existing methods
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
            # 1. YouTube Videos (keep existing)
            if 'video' in preferences.get('content_format', []):
                status_text.text("🔍 Searching YouTube for educational videos...")
                progress_bar.progress(0.20)
                
                videos = self._fetch_youtube_videos(topic, max_results=3)  # Reduced for testing
                all_resources['videos'] = videos
            
            # 2. Articles via Google Search API (ALWAYS try, regardless of content format)
            status_text.text("📄 Searching for educational articles (Google Search API)...")
            progress_bar.progress(0.40)
            
            articles = self._fetch_articles_with_fallback(topic, max_results=3)  # Reduced for testing
            all_resources['articles'] = articles
            
            # 3. Courses via Google Search API (ALWAYS try, regardless of content format)
            status_text.text("🎓 Searching for online courses (Google Search API)...")
            progress_bar.progress(0.60)
            
            courses = self._fetch_courses_with_fallback(topic, max_results=3)  # Reduced for testing
            all_resources['courses'] = courses
            
            # 4. Documentation (removed - not needed)
            status_text.text("✅ Resource fetching complete")
            progress_bar.progress(1.0)
            
            all_resources['documentation'] = []
            
            # Show API usage summary
            if self.google_available:
                usage_info = self.get_api_usage_info()
                st.info(f"🔍 Google Search API: {usage_info['daily_queries']}/{usage_info['max_queries']} queries used today")
            else:
                st.info("🔍 Using web scraping fallback for educational resources")
            
            # Clean up progress indicators
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"Error fetching resources: {e}")
            progress_bar.empty()
            status_text.empty()
        
        return all_resources
    
    def _fetch_youtube_videos(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Fetch educational videos from YouTube API (existing logic)"""
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
        """Get detailed information about a video (existing logic)"""
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
        """Parse ISO 8601 duration to readable format (existing logic)"""
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
    
    def _fetch_articles_with_fallback(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """
        Fetch articles using Google Search API with fallback
        Includes rate limiting and error handling
        """
        # Check if Google Search API is available
        if not self.google_available:
            st.warning("⚠️ Google Search API not configured - using fallback methods")
            return self._fallback_articles(topic, max_results)
        
        # Check rate limits
        if not self._can_make_query():
            st.warning("⚠️ Rate limit reached - using fallback methods")
            return self._fallback_articles(topic, max_results)
        
        # Try Google Search API first
        try:
            articles = self._fetch_articles_google_search(topic, max_results)
            if articles:
                st.success(f"✅ Found {len(articles)} articles via Google Search API")
                return articles
            else:
                st.info("ℹ️ No articles found via Google Search API - using fallback")
                return self._fallback_articles(topic, max_results)
                
        except Exception as e:
            st.error(f"❌ Google Search API failed: {str(e)} - using fallback")
            return self._fallback_articles(topic, max_results)
    
    def _fetch_articles_google_search(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Fetch articles using Google Search API"""
        if not self.google_service:
            return []
        
        # Rate limiting
        self._update_query_count()
        
        try:
            # Create more targeted educational search queries
            search_queries = [
                f'"{topic}" tutorial guide learn education',
                f'"{topic}" how to beginner guide',
                f'"{topic}" tips techniques best practices'
            ]
            
            all_articles = []
            
            for query in search_queries[:2]:  # Use first 2 queries to stay within limits
                result = self.google_service.cse().list(
                    q=query,
                    cx=self.search_engine_id,
                    num=max_results
                ).execute()
                
                if 'items' in result:
                    for item in result['items']:
                        # Filter for article-type content (exclude community sites)
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
                            all_articles.append(article)
                
                # Small delay between queries
                time.sleep(0.1)
            
            # Remove duplicates and return top results
            unique_articles = []
            seen_urls = set()
            for article in all_articles:
                if article.url not in seen_urls:
                    unique_articles.append(article)
                    seen_urls.add(article.url)
            
            return unique_articles[:max_results]
            
        except Exception as e:
            st.error(f"Google Search for articles failed: {str(e)}")
            return []
    
    def _fallback_articles(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Fallback method for articles using web scraping"""
        st.info("🔍 Google Search API unavailable - using web scraping fallback...")
        
        try:
            articles = self.web_scraper.scrape_educational_articles(topic, max_results)
            if articles:
                st.success(f"✅ Found {len(articles)} articles via web scraping")
                return articles
            else:
                st.warning("⚠️ No articles found via web scraping")
                return []
        except Exception as e:
            st.error(f"❌ Web scraping failed: {str(e)}")
            return []
    
    def _fetch_courses_with_fallback(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """
        Fetch courses using Google Search API with fallback
        Includes rate limiting and error handling
        """
        # Check if Google Search API is available
        if not self.google_available:
            st.warning("⚠️ Google Search API not configured - using fallback methods")
            return self._fallback_courses(topic, max_results)
        
        # Check rate limits
        if not self._can_make_query():
            st.warning("⚠️ Rate limit reached - using fallback methods")
            return self._fallback_courses(topic, max_results)
        
        # Try Google Search API first
        try:
            courses = self._fetch_courses_google_search(topic, max_results)
            if courses:
                st.success(f"✅ Found {len(courses)} courses via Google Search API")
                return courses
            else:
                st.info("ℹ️ No courses found via Google Search API - using fallback")
                return self._fallback_courses(topic, max_results)
                
        except Exception as e:
            st.error(f"❌ Google Search API failed: {str(e)} - using fallback")
            return self._fallback_courses(topic, max_results)
    
    def _fetch_courses_google_search(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Fetch courses using Google Search API"""
        if not self.google_service:
            return []
        
        # Rate limiting
        self._update_query_count()
        
        try:
            # Create targeted course search queries
            search_queries = [
                f'"{topic}" course online learning',
                f'"{topic}" class tutorial curriculum'
            ]
            
            all_courses = []
            
            for query in search_queries:
                result = self.google_service.cse().list(
                    q=query,
                    cx=self.search_engine_id,
                    num=max_results
                ).execute()
                
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
                            all_courses.append(course)
                
                # Small delay between queries
                time.sleep(0.1)
            
            # Remove duplicates and return top results
            unique_courses = []
            seen_urls = set()
            for course in all_courses:
                if course.url not in seen_urls:
                    unique_courses.append(course)
                    seen_urls.add(course.url)
            
            return unique_courses[:max_results]
            
        except Exception as e:
            st.error(f"Google Search for courses failed: {str(e)}")
            return []
    
    def _fallback_courses(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Fallback method for courses using web scraping"""
        st.info("🔍 Google Search API unavailable - using web scraping fallback...")
        
        try:
            courses = self.web_scraper.scrape_educational_courses(topic, max_results)
            if courses:
                st.success(f"✅ Found {len(courses)} courses via web scraping")
                return courses
            else:
                st.warning("⚠️ No courses found via web scraping")
                return []
        except Exception as e:
            st.error(f"❌ Web scraping failed: {str(e)}")
            return []
    
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
    
    def _is_article_content(self, item: Dict) -> bool:
        """Determine if search result is article content (include more educational sites)"""
        url = item.get('link', '').lower()
        title = item.get('title', '').lower()
        
        # Exclude video platforms
        if any(platform in url for platform in ['youtube.com', 'youtu.be', 'vimeo.com']):
            return False
        
        # Exclude course platforms (they have their own category)
        if any(platform in url for platform in ['coursera.org', 'udemy.com', 'edx.org', 'khanacademy.org']):
            return False
        
        # Exclude pure documentation sites (but allow educational content)
        if any(doc in url for doc in ['api.', 'reference.']):
            return False
        
        # Include educational content from community sites (but exclude pure discussion)
        educational_community_sites = [
            'medium.com', 'dev.to', 'hashnode.com', 'hashnode.dev',
            'freecodecamp.org', 'css-tricks.com', 'smashingmagazine.com',
            'sitepoint.com', 'webdesignerdepot.com', 'alistapart.com'
        ]
        
        # Allow educational content from these sites
        if any(site in url for site in educational_community_sites):
            return True
        
        # Exclude pure discussion/forum sites
        discussion_sites = [
            'reddit.com', 'stackoverflow.com', 'stackexchange.com', 'quora.com',
            'discord.com', 'slack.com', 'telegram.org', 'facebook.com', 'twitter.com',
            'x.com', 'linkedin.com', 'github.com/discussions', 'github.com/issues'
        ]
        
        if any(site in url for site in discussion_sites):
            return False
        
        return True
    
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
    
    def _can_make_query(self) -> bool:
        """Check if we can make a query (rate limiting)"""
        current_time = time.time()
        
        # Reset daily count if it's a new day
        if current_time - self.last_query_time > 86400:  # 24 hours
            self.daily_query_count = 0
        
        return self.daily_query_count < self.max_daily_queries
    
    def _update_query_count(self):
        """Update query count for rate limiting"""
        current_time = time.time()
        
        # Rate limiting between queries
        if current_time - self.last_query_time < self.min_query_interval:
            time.sleep(self.min_query_interval - (current_time - self.last_query_time))
        
        self.daily_query_count += 1
        self.last_query_time = current_time
    
    def get_api_usage_info(self) -> Dict:
        """Get current API usage information"""
        return {
            'daily_queries_used': self.daily_query_count,
            'max_daily_queries': self.max_daily_queries,
            'queries_remaining': self.max_daily_queries - self.daily_query_count,
            'google_search_available': self.google_available,
            'youtube_available': self.youtube_available
        } 