# resource_fetchers.py
import os
import requests
import time
import re
from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
import streamlit as st
from models import LearningResource
from quality_scorer import QualityScorer

class YouTubeResourceFetcher:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if self.api_key:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        else:
            self.youtube = None
    
    def search_educational_videos(self, query: str, max_results: int = 5) -> List[LearningResource]:
        """Search for educational videos on YouTube"""
        if not self.youtube:
            return []
        
        try:
            search_query = f"{query} tutorial learn course education"
            
            search_response = self.youtube.search().list(
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
                video_details = self.get_video_details(search_result['id']['videoId'])
                
                videos.append(LearningResource(
                    type='video',
                    title=search_result['snippet']['title'],
                    url=f"https://www.youtube.com/watch?v={search_result['id']['videoId']}",
                    description=search_result['snippet']['description'][:200] + "...",
                    source=search_result['snippet']['channelTitle'],
                    estimated_time=video_details.get('duration', 'Unknown'),
                    difficulty='Mixed'
                ))
            
            return videos
            
        except HttpError as e:
            st.warning(f"YouTube API error: {e}")
            return []
    
    def get_video_details(self, video_id: str) -> Dict:
        """Get detailed information about a video"""
        try:
            video_response = self.youtube.videos().list(
                part='contentDetails,statistics',
                id=video_id
            ).execute()
            
            if video_response['items']:
                item = video_response['items'][0]
                duration = item['contentDetails']['duration']
                duration_readable = self.parse_duration(duration)
                
                return {'duration': duration_readable}
        except:
            pass
        
        return {}
    
    def parse_duration(self, duration: str) -> str:
        """Parse ISO 8601 duration to readable format"""
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

class EducationalArticleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        self.educational_sites = [
            'medium.com', 'towardsdatascience.com', 'freecodecamp.org',
            'codecademy.com', 'khanacademy.org', 'dev.to', 'hashnode.com'
        ]
    
    def search_educational_articles(self, topic: str, max_results: int = 5) -> List[LearningResource]:
        """Search for educational articles across multiple platforms"""
        articles = []
        
        # Try different search strategies
        search_methods = [
            self.search_dev_to,
            self.search_github_repos,
            self.create_curated_resources
        ]
        
        for search_method in search_methods:
            try:
                results = search_method(topic, max_results // len(search_methods) + 1)
                articles.extend(results)
                time.sleep(1)  # Be respectful to servers
                if len(articles) >= max_results:
                    break
            except Exception as e:
                st.warning(f"Search method {search_method.__name__} failed: {str(e)[:100]}...")
                continue
        
        unique_articles = self.remove_duplicates(articles)
        return unique_articles[:max_results]
    
    def search_dev_to(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Search Dev.to for articles (they have an API)"""
        articles = []
        
        try:
            # Dev.to has a public API
            api_url = "https://dev.to/api/articles"
            params = {
                'tag': topic.lower().replace(' ', ''),
                'per_page': max_results,
                'top': 7  # Top articles from past week
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for article in data:
                    articles.append(LearningResource(
                        type='article',
                        title=article.get('title', ''),
                        url=article.get('url', ''),
                        description=article.get('description', '')[:200] + "...",
                        source='Dev.to',
                        estimated_time='5-10 min read',
                        difficulty='Mixed'
                    ))
                    
        except Exception as e:
            pass  # Fail silently and try other methods
        
        return articles
    
    def search_github_repos(self, topic: str, max_results: int = 2) -> List[LearningResource]:
        """Search GitHub for educational repositories"""
        articles = []
        
        try:
            # GitHub search API (no auth needed for basic search)
            api_url = "https://api.github.com/search/repositories"
            params = {
                'q': f'{topic} tutorial awesome list',
                'sort': 'stars',
                'order': 'desc',
                'per_page': max_results
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for repo in data.get('items', []):
                    if 'awesome' in repo.get('name', '').lower() or 'tutorial' in repo.get('name', '').lower():
                        articles.append(LearningResource(
                            type='article',
                            title=f"GitHub: {repo.get('name', '')}",
                            url=repo.get('html_url', ''),
                            description=repo.get('description', '')[:200] + "...",
                            source='GitHub',
                            estimated_time='Variable',
                            difficulty='Mixed'
                        ))
                        
        except Exception as e:
            pass  # Fail silently
        
        return articles
    
    def create_curated_resources(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Create curated educational resources when scraping fails"""
        
        # Curated educational resources for common topics
        curated_resources = {
            'python': [
                {
                    'title': 'Python.org Official Tutorial',
                    'url': 'https://docs.python.org/3/tutorial/',
                    'description': 'The official Python tutorial covering all basics',
                    'source': 'Python.org'
                },
                {
                    'title': 'Real Python - Python Tutorials',
                    'url': 'https://realpython.com/',
                    'description': 'High-quality Python tutorials for all levels',
                    'source': 'Real Python'
                },
                {
                    'title': 'Python Guide for Beginners',
                    'url': 'https://wiki.python.org/moin/BeginnersGuide',
                    'description': 'Comprehensive guide for Python beginners',
                    'source': 'Python Wiki'
                }
            ],
            'javascript': [
                {
                    'title': 'MDN JavaScript Guide',
                    'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide',
                    'description': 'Comprehensive JavaScript guide by Mozilla',
                    'source': 'MDN Web Docs'
                },
                {
                    'title': 'JavaScript.info Tutorial',
                    'url': 'https://javascript.info/',
                    'description': 'Modern JavaScript tutorial with examples',
                    'source': 'JavaScript.info'
                }
            ],
            'machine learning': [
                {
                    'title': 'Machine Learning Course - Andrew Ng',
                    'url': 'https://www.coursera.org/learn/machine-learning',
                    'description': 'Famous machine learning course by Andrew Ng',
                    'source': 'Coursera'
                },
                {
                    'title': 'Scikit-learn User Guide',
                    'url': 'https://scikit-learn.org/stable/user_guide.html',
                    'description': 'Official scikit-learn documentation and tutorials',
                    'source': 'Scikit-learn'
                }
            ],
            'web development': [
                {
                    'title': 'FreeCodeCamp Web Development',
                    'url': 'https://www.freecodecamp.org/learn/responsive-web-design/',
                    'description': 'Complete web development curriculum',
                    'source': 'FreeCodeCamp'
                },
                {
                    'title': 'The Odin Project',
                    'url': 'https://www.theodinproject.com/',
                    'description': 'Full-stack web development curriculum',
                    'source': 'The Odin Project'
                }
            ],
            'data science': [
                {
                    'title': 'Kaggle Learn',
                    'url': 'https://www.kaggle.com/learn',
                    'description': 'Free micro-courses in data science',
                    'source': 'Kaggle'
                },
                {
                    'title': 'Fast.ai Practical Deep Learning',
                    'url': 'https://course.fast.ai/',
                    'description': 'Practical deep learning for coders',
                    'source': 'Fast.ai'
                }
            ]
        }
        
        articles = []
        topic_lower = topic.lower()
        
        # Find matching curated resources
        for key, resources in curated_resources.items():
            if key in topic_lower or any(word in topic_lower for word in key.split()):
                for resource in resources[:max_results]:
                    articles.append(LearningResource(
                        type='article',
                        title=resource['title'],
                        url=resource['url'],
                        description=resource['description'],
                        source=resource['source'],
                        estimated_time='10-30 min read',
                        difficulty='Mixed'
                    ))
        
        # If no specific curated resources, create generic ones
        if not articles:
            generic_resources = [
                LearningResource(
                    type='article',
                    title=f'{topic.title()} - Getting Started Guide',
                    url=f'https://www.google.com/search?q={topic.replace(" ", "+")}+tutorial+guide',
                    description=f'Search results for {topic} tutorials and guides',
                    source='Google Search',
                    estimated_time='Variable',
                    difficulty='Mixed'
                ),
                LearningResource(
                    type='article',
                    title=f'{topic.title()} Documentation',
                    url=f'https://www.google.com/search?q={topic.replace(" ", "+")}+official+documentation',
                    description=f'Official documentation and resources for {topic}',
                    source='Official Docs',
                    estimated_time='Variable',
                    difficulty='Reference'
                )
            ]
            articles.extend(generic_resources[:max_results])
        
        return articles
    
    def remove_duplicates(self, articles: List[LearningResource]) -> List[LearningResource]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article.url and article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        return unique_articles

class OfficialDocumentationFetcher:
    """Fetcher for official documentation and high-quality educational resources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_official_docs(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Search for official documentation and high-quality resources"""
        
        # Official documentation sources
        official_sources = {
            'python': [
                {
                    'title': 'Python Official Documentation',
                    'url': 'https://docs.python.org/3/',
                    'description': 'Complete Python documentation with tutorials and references',
                    'source': 'Python.org'
                },
                {
                    'title': 'Python Tutorial - Official',
                    'url': 'https://docs.python.org/3/tutorial/',
                    'description': 'Step-by-step Python tutorial from the creators',
                    'source': 'Python.org'
                }
            ],
            'javascript': [
                {
                    'title': 'MDN Web Docs - JavaScript',
                    'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript',
                    'description': 'Comprehensive JavaScript documentation by Mozilla',
                    'source': 'MDN Web Docs'
                },
                {
                    'title': 'JavaScript.info - Modern Tutorial',
                    'url': 'https://javascript.info/',
                    'description': 'Modern JavaScript tutorial with detailed explanations',
                    'source': 'JavaScript.info'
                }
            ],
            'react': [
                {
                    'title': 'React Official Documentation',
                    'url': 'https://react.dev/',
                    'description': 'Official React documentation with tutorials',
                    'source': 'React.dev'
                },
                {
                    'title': 'React Tutorial - Official',
                    'url': 'https://react.dev/learn',
                    'description': 'Learn React from the official tutorial',
                    'source': 'React.dev'
                }
            ],
            'node': [
                {
                    'title': 'Node.js Official Documentation',
                    'url': 'https://nodejs.org/en/docs/',
                    'description': 'Complete Node.js documentation and guides',
                    'source': 'Node.js'
                }
            ],
            'git': [
                {
                    'title': 'Git Official Documentation',
                    'url': 'https://git-scm.com/doc',
                    'description': 'Official Git documentation and tutorials',
                    'source': 'Git-SCM'
                },
                {
                    'title': 'Pro Git Book',
                    'url': 'https://git-scm.com/book',
                    'description': 'Complete Git book available for free',
                    'source': 'Git-SCM'
                }
            ]
        }
        
        resources = []
        topic_lower = topic.lower()
        
        # Find matching official documentation
        for key, docs in official_sources.items():
            if key in topic_lower or any(word in topic_lower for word in key.split()):
                for doc in docs[:max_results]:
                    resources.append(LearningResource(
                        type='documentation',
                        title=doc['title'],
                        url=doc['url'],
                        description=doc['description'],
                        source=doc['source'],
                        estimated_time='30-60 min read',
                        difficulty='Reference'
                    ))
        
        return resources[:max_results]

class CoursePlatformFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_all_platforms(self, topic: str, max_results: int = 6) -> List[LearningResource]:
        """Search all course platforms"""
        all_courses = []
        
        # High-quality educational platforms with direct course links
        course_platforms = {
            'python': [
                {
                    'title': 'Python for Everybody Specialization',
                    'url': 'https://www.coursera.org/specializations/python',
                    'source': 'Coursera',
                    'description': 'University of Michigan Python course series'
                },
                {
                    'title': 'Complete Python Bootcamp',
                    'url': 'https://www.udemy.com/course/complete-python-bootcamp/',
                    'source': 'Udemy',
                    'description': 'Comprehensive Python course from zero to hero'
                },
                {
                    'title': 'Python Programming Course',
                    'url': 'https://www.freecodecamp.org/learn/scientific-computing-with-python/',
                    'source': 'FreeCodeCamp',
                    'description': 'Free Python programming certification'
                }
            ],
            'machine learning': [
                {
                    'title': 'Machine Learning Course - Andrew Ng',
                    'url': 'https://www.coursera.org/learn/machine-learning',
                    'source': 'Coursera',
                    'description': 'The famous machine learning course by Andrew Ng'
                },
                {
                    'title': 'Fast.ai Practical Deep Learning',
                    'url': 'https://course.fast.ai/',
                    'source': 'Fast.ai',
                    'description': 'Practical deep learning for coders'
                }
            ],
            'web development': [
                {
                    'title': 'The Complete Web Developer Course',
                    'url': 'https://www.udemy.com/course/the-complete-web-development-bootcamp/',
                    'source': 'Udemy',
                    'description': 'Full-stack web development bootcamp'
                },
                {
                    'title': 'Responsive Web Design',
                    'url': 'https://www.freecodecamp.org/learn/responsive-web-design/',
                    'source': 'FreeCodeCamp',
                    'description': 'Free responsive web design certification'
                },
                {
                    'title': 'The Odin Project',
                    'url': 'https://www.theodinproject.com/',
                    'source': 'The Odin Project',
                    'description': 'Free full-stack curriculum'
                }
            ],
            'javascript': [
                {
                    'title': 'JavaScript Algorithms and Data Structures',
                    'url': 'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/',
                    'source': 'FreeCodeCamp',
                    'description': 'Free JavaScript certification course'
                },
                {
                    'title': 'The Complete JavaScript Course',
                    'url': 'https://www.udemy.com/course/the-complete-javascript-course/',
                    'source': 'Udemy',
                    'description': 'Modern JavaScript from beginner to advanced'
                }
            ]
        }
        
        topic_lower = topic.lower()
        
        # Find matching courses
        for key, courses in course_platforms.items():
            if key in topic_lower or any(word in topic_lower for word in key.split()):
                for course in courses[:max_results]:
                    all_courses.append(LearningResource(
                        type='course',
                        title=course['title'],
                        url=course['url'],
                        description=course['description'],
                        source=course['source'],
                        estimated_time='4-12 weeks',
                        difficulty='Mixed'
                    ))
        
        # If no specific courses found, create general course searches
        if not all_courses:
            general_courses = [
                LearningResource(
                    type='course',
                    title=f"Coursera: {topic.title()} Courses",
                    url=f"https://www.coursera.org/search?query={topic.replace(' ', '%20')}",
                    description=f"University-level courses on {topic}",
                    source='Coursera',
                    estimated_time='4-8 weeks',
                    difficulty='Mixed'
                ),
                LearningResource(
                    type='course',
                    title=f"Udemy: {topic.title()} Courses",
                    url=f"https://www.udemy.com/courses/search/?q={topic.replace(' ', '+')}",
                    description=f"Practical courses on {topic}",
                    source='Udemy',
                    estimated_time='2-10 hours',
                    difficulty='Mixed'
                ),
                LearningResource(
                    type='course',
                    title=f"edX: {topic.title()} Courses",
                    url=f"https://www.edx.org/search?q={topic.replace(' ', '+')}",
                    description=f"University courses on {topic}",
                    source='edX',
                    estimated_time='6-12 weeks',
                    difficulty='Mixed'
                )
            ]
            all_courses.extend(general_courses)
        
        return all_courses[:max_results]

class ComprehensiveResourceFetcher:
    def __init__(self):
        self.youtube_fetcher = YouTubeResourceFetcher()
        self.article_scraper = EducationalArticleScraper()
        self.documentation_fetcher = OfficialDocumentationFetcher()
        self.course_fetcher = CoursePlatformFetcher()
        
    def fetch_all_resources(self, topic: str, preferences: Dict) -> Dict[str, List[LearningResource]]:
        """Fetch resources from all sources based on user preferences"""
        
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
                
                all_resources['videos'] = self.youtube_fetcher.search_educational_videos(
                    topic, max_results=6
                )
            
            # 2. Educational Articles & Dev.to
            status_text.text("📄 Searching for educational articles...")
            progress_bar.progress(0.50)
            
            all_resources['articles'] = self.article_scraper.search_educational_articles(
                topic, max_results=6
            )
            
            # 3. Official Documentation
            status_text.text("📚 Searching for official documentation...")
            progress_bar.progress(0.75)
            
            all_resources['documentation'] = self.documentation_fetcher.search_official_docs(
                topic, max_results=3
            )
            
            # 4. Course Platforms
            status_text.text("🎓 Searching course platforms...")
            progress_bar.progress(1.0)
            
            all_resources['courses'] = self.course_fetcher.search_all_platforms(
                topic, max_results=4
            )
            
            # Clean up progress indicators
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"Error fetching resources: {e}")
            progress_bar.empty()
            status_text.empty()
        
        return all_resources
    
    def filter_resources_by_preferences(self, resources: Dict[str, List[LearningResource]], 
                                      preferences: Dict) -> Dict[str, List[LearningResource]]:
        """Filter and rank resources based on user preferences"""
        
        filtered_resources = {}
        
        learning_style = preferences.get('learning_style', [])
        content_format = preferences.get('content_format', [])
        engagement_style = preferences.get('engagement_style', '')
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
                title_lower = resource.title.lower()
                description_lower = resource.description.lower()
                
                if current_level == 'beginner':
                    if any(word in title_lower or word in description_lower 
                           for word in ['beginner', 'intro', 'basic', 'getting started']):
                        score += 2
                elif current_level == 'intermediate':
                    if any(word in title_lower or word in description_lower 
                           for word in ['intermediate', 'practical', 'hands-on']):
                        score += 2
                elif current_level == 'advanced':
                    if any(word in title_lower or word in description_lower 
                           for word in ['advanced', 'expert', 'deep dive']):
                        score += 2
                
                resource.relevance_score = score
                filtered_list.append(resource)
            
            # Sort by relevance score
            filtered_list.sort(key=lambda x: x.relevance_score, reverse=True)
            filtered_resources[resource_type] = filtered_list[:6]  # Top 6 per category
        
        return filtered_resources

class YouTubeResourceFetcher:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if self.api_key:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        else:
            self.youtube = None
    
    def search_educational_videos(self, query: str, max_results: int = 5) -> List[LearningResource]:
        """Search for educational videos on YouTube"""
        if not self.youtube:
            return []
        
        try:
            search_query = f"{query} tutorial learn course education"
            
            search_response = self.youtube.search().list(
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
                video_details = self.get_video_details(search_result['id']['videoId'])
                
                videos.append(LearningResource(
                    type='video',
                    title=search_result['snippet']['title'],
                    url=f"https://www.youtube.com/watch?v={search_result['id']['videoId']}",
                    description=search_result['snippet']['description'][:200] + "...",
                    source=search_result['snippet']['channelTitle'],
                    estimated_time=video_details.get('duration', 'Unknown'),
                    difficulty='Mixed'
                ))
            
            return videos
            
        except HttpError as e:
            st.warning(f"YouTube API error: {e}")
            return []
    
    def get_video_details(self, video_id: str) -> Dict:
        """Get detailed information about a video"""
        try:
            video_response = self.youtube.videos().list(
                part='contentDetails,statistics',
                id=video_id
            ).execute()
            
            if video_response['items']:
                item = video_response['items'][0]
                duration = item['contentDetails']['duration']
                duration_readable = self.parse_duration(duration)
                
                return {'duration': duration_readable}
        except:
            pass
        
        return {}
    
    def parse_duration(self, duration: str) -> str:
        """Parse ISO 8601 duration to readable format"""
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

class EducationalArticleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        self.educational_sites = [
            'medium.com', 'towardsdatascience.com', 'freecodecamp.org',
            'codecademy.com', 'khanacademy.org', 'dev.to', 'hashnode.com'
        ]
    
    def search_educational_articles(self, topic: str, max_results: int = 5) -> List[LearningResource]:
        """Search for educational articles across multiple platforms"""
        articles = []
        
        # Try different search strategies
        search_methods = [
            self.search_dev_to,
            self.search_github_repos,
            self.create_curated_resources
        ]
        
        for search_method in search_methods:
            try:
                results = search_method(topic, max_results // len(search_methods) + 1)
                articles.extend(results)
                time.sleep(1)  # Be respectful to servers
                if len(articles) >= max_results:
                    break
            except Exception as e:
                st.warning(f"Search method {search_method.__name__} failed: {str(e)[:100]}...")
                continue
        
        unique_articles = self.remove_duplicates(articles)
        return unique_articles[:max_results]
    
    def search_dev_to(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Search Dev.to for articles (they have an API)"""
        articles = []
        
        try:
            # Dev.to has a public API
            api_url = "https://dev.to/api/articles"
            params = {
                'tag': topic.lower().replace(' ', ''),
                'per_page': max_results,
                'top': 7  # Top articles from past week
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for article in data:
                    articles.append(LearningResource(
                        type='article',
                        title=article.get('title', ''),
                        url=article.get('url', ''),
                        description=article.get('description', '')[:200] + "...",
                        source='Dev.to',
                        estimated_time='5-10 min read',
                        difficulty='Mixed'
                    ))
                    
        except Exception as e:
            pass  # Fail silently and try other methods
        
        return articles
    
    def search_github_repos(self, topic: str, max_results: int = 2) -> List[LearningResource]:
        """Search GitHub for educational repositories"""
        articles = []
        
        try:
            # GitHub search API (no auth needed for basic search)
            api_url = "https://api.github.com/search/repositories"
            params = {
                'q': f'{topic} tutorial awesome list',
                'sort': 'stars',
                'order': 'desc',
                'per_page': max_results
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for repo in data.get('items', []):
                    if 'awesome' in repo.get('name', '').lower() or 'tutorial' in repo.get('name', '').lower():
                        articles.append(LearningResource(
                            type='article',
                            title=f"GitHub: {repo.get('name', '')}",
                            url=repo.get('html_url', ''),
                            description=repo.get('description', '')[:200] + "...",
                            source='GitHub',
                            estimated_time='Variable',
                            difficulty='Mixed'
                        ))
                        
        except Exception as e:
            pass  # Fail silently
        
        return articles
    
    def create_curated_resources(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Create curated educational resources when scraping fails"""
        
        # Curated educational resources for common topics
        curated_resources = {
            'python': [
                {
                    'title': 'Python.org Official Tutorial',
                    'url': 'https://docs.python.org/3/tutorial/',
                    'description': 'The official Python tutorial covering all basics',
                    'source': 'Python.org'
                },
                {
                    'title': 'Real Python - Python Tutorials',
                    'url': 'https://realpython.com/',
                    'description': 'High-quality Python tutorials for all levels',
                    'source': 'Real Python'
                },
                {
                    'title': 'Python Guide for Beginners',
                    'url': 'https://wiki.python.org/moin/BeginnersGuide',
                    'description': 'Comprehensive guide for Python beginners',
                    'source': 'Python Wiki'
                }
            ],
            'javascript': [
                {
                    'title': 'MDN JavaScript Guide',
                    'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide',
                    'description': 'Comprehensive JavaScript guide by Mozilla',
                    'source': 'MDN Web Docs'
                },
                {
                    'title': 'JavaScript.info Tutorial',
                    'url': 'https://javascript.info/',
                    'description': 'Modern JavaScript tutorial with examples',
                    'source': 'JavaScript.info'
                }
            ],
            'machine learning': [
                {
                    'title': 'Machine Learning Course - Andrew Ng',
                    'url': 'https://www.coursera.org/learn/machine-learning',
                    'description': 'Famous machine learning course by Andrew Ng',
                    'source': 'Coursera'
                },
                {
                    'title': 'Scikit-learn User Guide',
                    'url': 'https://scikit-learn.org/stable/user_guide.html',
                    'description': 'Official scikit-learn documentation and tutorials',
                    'source': 'Scikit-learn'
                }
            ]
        }
        
        articles = []
        topic_lower = topic.lower()
        
        # Find matching curated resources
        for key, resources in curated_resources.items():
            if key in topic_lower or any(word in topic_lower for word in key.split()):
                for resource in resources[:max_results]:
                    articles.append(LearningResource(
                        type='article',
                        title=resource['title'],
                        url=resource['url'],
                        description=resource['description'],
                        source=resource['source'],
                        estimated_time='10-30 min read',
                        difficulty='Mixed'
                    ))
        
        # If no specific curated resources, create generic ones
        if not articles:
            generic_resources = [
                LearningResource(
                    type='article',
                    title=f'{topic.title()} - Getting Started Guide',
                    url=f'https://www.google.com/search?q={topic.replace(" ", "+")}+tutorial+guide',
                    description=f'Search results for {topic} tutorials and guides',
                    source='Google Search',
                    estimated_time='Variable',
                    difficulty='Mixed'
                ),
                LearningResource(
                    type='article',
                    title=f'{topic.title()} Documentation',
                    url=f'https://www.google.com/search?q={topic.replace(" ", "+")}+official+documentation',
                    description=f'Official documentation and resources for {topic}',
                    source='Official Docs',
                    estimated_time='Variable',
                    difficulty='Reference'
                )
            ]
            articles.extend(generic_resources[:max_results])
        
        return articles
    
    def search_freecodecamp_articles(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Search FreeCodeCamp for articles - simplified version"""
        articles = []
        
        # Since web scraping might be blocked, create direct links
        freecodecamp_resources = [
            LearningResource(
                type='article',
                title=f'FreeCodeCamp: {topic.title()} Tutorial',
                url=f'https://www.freecodecamp.org/news/search/?query={topic.replace(" ", "%20")}',
                description=f'Search FreeCodeCamp articles about {topic}',
                source='FreeCodeCamp',
                estimated_time='10-20 min read',
                difficulty='Beginner to Intermediate'
            )
        ]
        
        return freecodecamp_resources[:max_results]
    
    def search_general_articles(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Create general article resources when web scraping is limited"""
        articles = []
        
        # Create helpful search links for major educational platforms
        educational_searches = [
            {
                'title': f'Medium Articles: {topic.title()}',
                'url': f'https://medium.com/search?q={topic.replace(" ", "%20")}',
                'source': 'Medium',
                'description': f'Medium articles and tutorials about {topic}'
            },
            {
                'title': f'Stack Overflow: {topic.title()}',
                'url': f'https://stackoverflow.com/search?q={topic.replace(" ", "+")}',
                'source': 'Stack Overflow',
                'description': f'Questions and answers about {topic}'
            },
            {
                'title': f'Reddit r/LearnProgramming: {topic.title()}',
                'url': f'https://www.reddit.com/r/learnprogramming/search/?q={topic.replace(" ", "%20")}',
                'source': 'Reddit',
                'description': f'Community discussions and resources about {topic}'
            }
        ]
        
        for resource in educational_searches[:max_results]:
            articles.append(LearningResource(
                type='article',
                title=resource['title'],
                url=resource['url'],
                description=resource['description'],
                source=resource['source'],
                estimated_time='5-15 min read',
                difficulty='Mixed'
            ))
        
        return articles
    
    def remove_duplicates(self, articles: List[LearningResource]) -> List[LearningResource]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article.url and article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        return unique_articles

class CoursePlatformFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_all_platforms(self, topic: str, max_results: int = 6) -> List[LearningResource]:
        """Search all course platforms"""
        all_courses = []
        
        # For now, we'll create some mock courses since course platform scraping is complex
        # In production, you'd implement actual scraping or use APIs where available
        mock_courses = [
            LearningResource(
                type='course',
                title=f"Complete {topic} Course",
                url=f"https://www.coursera.org/search?query={topic.replace(' ', '%20')}",
                description=f"Comprehensive course covering all aspects of {topic}",
                source='Coursera',
                estimated_time='4-6 weeks',
                difficulty='Intermediate'
            ),
            LearningResource(
                type='course',
                title=f"{topic} Fundamentals",
                url=f"https://www.edx.org/search?q={topic.replace(' ', '+')}",
                description=f"Learn the fundamentals of {topic} from industry experts",
                source='edX',
                estimated_time='3-5 weeks',
                difficulty='Beginner'
            ),
            LearningResource(
                type='course',
                title=f"Advanced {topic} Techniques",
                url=f"https://www.udemy.com/courses/search/?q={topic.replace(' ', '+')}",
                description=f"Master advanced {topic} concepts and techniques",
                source='Udemy',
                estimated_time='2-4 weeks',
                difficulty='Advanced'
            )
        ]
        
        return mock_courses[:max_results]

class ComprehensiveResourceFetcher:
    def __init__(self):
        self.youtube_fetcher = YouTubeResourceFetcher()
        self.article_scraper = EducationalArticleScraper()
        self.course_fetcher = CoursePlatformFetcher()
        self.quality_scorer = QualityScorer()
        
    def fetch_all_resources(self, topic: str, preferences: Dict) -> Dict[str, List[LearningResource]]:
        """Fetch resources from all sources based on user preferences"""
        
        all_resources = {
            'videos': [],
            'articles': [],
            'courses': []
        }
        
        # Get topic category for quality scoring
        topic_category = preferences.get('topic_category', '')
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1. YouTube Videos
            if 'video' in preferences.get('content_format', []):
                status_text.text("🔍 Searching YouTube for educational videos...")
                progress_bar.progress(0.25)
                
                videos = self.youtube_fetcher.search_educational_videos(
                    topic, max_results=5
                )
                
                # Apply quality scoring to videos
                for video in videos:
                    self.quality_scorer.score_resource(video, topic_category)
                
                all_resources['videos'] = videos
            
            # 2. Educational Articles
            status_text.text("📄 Searching for educational articles...")
            progress_bar.progress(0.50)
            
            articles = self.article_scraper.search_educational_articles(
                topic, max_results=5
            )
            
            # Apply quality scoring to articles
            for article in articles:
                self.quality_scorer.score_resource(article, topic_category)
            
            all_resources['articles'] = articles
            
            # 3. Course Platforms
            status_text.text("🎓 Searching course platforms...")
            progress_bar.progress(1.0)
            
            courses = self.course_fetcher.search_all_platforms(
                topic, max_results=4
            )
            
            # Apply quality scoring to courses
            for course in courses:
                self.quality_scorer.score_resource(course, topic_category)
            
            all_resources['courses'] = courses
            
            # Clean up progress indicators
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"Error fetching resources: {e}")
            progress_bar.empty()
            status_text.empty()
        
        return all_resources
    
    def filter_resources_by_preferences(self, resources: Dict[str, List[LearningResource]], 
                                      preferences: Dict) -> Dict[str, List[LearningResource]]:
        """Filter and rank resources based on user preferences"""
        
        filtered_resources = {}
        
        learning_style = preferences.get('learning_style', [])
        content_format = preferences.get('content_format', [])
        engagement_style = preferences.get('engagement_style', '')
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
                
                # Score based on learning style
                if 'visual' in learning_style and resource_type in ['videos', 'courses']:
                    score += 2
                elif 'reading' in learning_style and resource_type in ['articles']:
                    score += 2
                
                # Score based on level appropriateness
                title_lower = resource.title.lower()
                description_lower = resource.description.lower()
                
                if current_level == 'beginner':
                    if any(word in title_lower or word in description_lower 
                           for word in ['beginner', 'intro', 'basic', 'getting started']):
                        score += 2
                elif current_level == 'intermediate':
                    if any(word in title_lower or word in description_lower 
                           for word in ['intermediate', 'practical', 'hands-on']):
                        score += 2
                elif current_level == 'advanced':
                    if any(word in title_lower or word in description_lower 
                           for word in ['advanced', 'expert', 'deep dive']):
                        score += 2
                
                # Add quality score to relevance score
                final_score = score + (resource.quality_score * 0.3)  # Quality contributes 30% to final ranking
                resource.relevance_score = final_score
                filtered_list.append(resource)
            
            # Sort by final score (relevance + quality)
            filtered_list.sort(key=lambda x: x.relevance_score, reverse=True)
            filtered_resources[resource_type] = filtered_list[:5]
        
        return filtered_resources