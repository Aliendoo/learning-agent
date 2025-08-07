# educational_site_scraper.py
"""
Educational Site Scraper - Web scraping fallback for when Google Search API is unavailable
Targets high-quality educational platforms for articles and courses
"""

import requests
import time
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import streamlit as st
from models import LearningResource
from quality_scorer import QualityScorer

class EducationalSiteScraper:
    """Scraper for educational websites as fallback when Google Search API is unavailable"""
    
    def __init__(self):
        self.quality_scorer = QualityScorer()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LearningAgent/1.0 (Educational Research Bot)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Rate limiting delays (seconds between requests)
        self.request_delays = {
            'medium.com': 2.0,
            'dev.to': 1.5,
            'freecodecamp.org': 1.0,
            'css-tricks.com': 2.0,
            'smashingmagazine.com': 2.0,
            'sitepoint.com': 1.5,
            'default': 1.0
        }
        
        # Educational site configurations
        self.site_configs = {
            'medium': {
                'search_url': 'https://medium.com/search',
                'base_url': 'https://medium.com',
                'article_selector': 'article',
                'title_selector': 'h1, h2, h3',
                'link_selector': 'a[href*="/p/"]',
                'description_selector': 'p',
                'delay': 2.0
            },
            'dev_to': {
                'search_url': 'https://dev.to/search',
                'base_url': 'https://dev.to',
                'article_selector': '.crayons-story',
                'title_selector': '.crayons-story__title',
                'link_selector': 'a.crayons-story__title',
                'description_selector': '.crayons-story__snippet',
                'delay': 1.5
            },
            'freecodecamp': {
                'search_url': 'https://www.freecodecamp.org/news/search',
                'base_url': 'https://www.freecodecamp.org',
                'article_selector': '.post-card',
                'title_selector': '.post-card-title',
                'link_selector': 'a.post-card-image-link',
                'description_selector': '.post-card-excerpt',
                'delay': 1.0
            }
        }
    
    def scrape_educational_articles(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Scrape educational articles from multiple sites"""
        all_articles = []
        
        # Sites to scrape (in order of preference)
        sites = ['freecodecamp', 'dev_to', 'medium']
        
        for site in sites:
            try:
                st.info(f"🔍 Scraping {site.replace('_', ' ').title()} for {topic}...")
                articles = getattr(self, f'scrape_{site}')(topic, max_results)
                all_articles.extend(articles)
                
                # Respect rate limits
                delay = self.site_configs.get(site, {}).get('delay', self.request_delays['default'])
                time.sleep(delay)
                
            except Exception as e:
                st.warning(f"⚠️ Failed to scrape {site}: {str(e)}")
                continue
        
        # Score, rank, and return top results
        scored_articles = []
        for article in all_articles:
            scored_article = self.quality_scorer.score_resource(article, topic)
            scored_articles.append(scored_article)
        
        # Sort by quality score and remove duplicates
        scored_articles.sort(key=lambda x: x.quality_score, reverse=True)
        unique_articles = self._remove_duplicates(scored_articles)
        
        return unique_articles[:max_results]
    
    def scrape_medium(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Scrape educational articles from Medium"""
        articles = []
        
        try:
            # Medium search URL
            search_url = f"https://medium.com/search?q={topic.replace(' ', '%20')}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if this is a JavaScript-heavy page
            scripts = soup.find_all('script')
            if len(scripts) > 20:
                st.warning("⚠️ Medium uses JavaScript to load content - skipping")
                return articles
            
            # Try alternative selectors for Medium
            selectors = [
                'article',
                'div[data-testid*="story"]',
                'div[class*="story"]',
                'div[class*="post"]'
            ]
            
            for selector in selectors:
                article_elements = soup.select(selector)
                if article_elements:
                    break
            
            for article_elem in article_elements[:max_results * 2]:
                try:
                    # Extract title and link
                    title_elem = article_elem.find(['h1', 'h2', 'h3', 'a'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue
                    
                    # Find link
                    link_elem = article_elem.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    url = link_elem.get('href')
                    if not url.startswith('http'):
                        url = urljoin('https://medium.com', url)
                    
                    # Extract description
                    desc_elem = article_elem.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Create LearningResource
                    article = LearningResource(
                        type='article',
                        title=title,
                        url=url,
                        description=description[:200] + "..." if len(description) > 200 else description,
                        source='Medium',
                        estimated_time=self._estimate_reading_time_from_text(description),
                        difficulty=self._determine_difficulty_from_text(title, description)
                    )
                    
                    articles.append(article)
                    
                    if len(articles) >= max_results:
                        break
                        
                except Exception as e:
                    continue
            
        except Exception as e:
            st.warning(f"Medium scraping failed: {str(e)}")
        
        return articles
    
    def scrape_dev_to(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Scrape educational articles from Dev.to"""
        articles = []
        
        try:
            # Dev.to search URL
            search_url = f"https://dev.to/search?q={topic.replace(' ', '%20')}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article elements
            article_elements = soup.find_all('div', class_='crayons-story', limit=max_results * 2)
            
            for article_elem in article_elements:
                try:
                    # Extract title and link
                    title_elem = article_elem.find('a', class_='crayons-story__title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href')
                    if not url.startswith('http'):
                        url = urljoin('https://dev.to', url)
                    
                    # Extract description
                    desc_elem = article_elem.find('div', class_='crayons-story__snippet')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Create LearningResource
                    article = LearningResource(
                        type='article',
                        title=title,
                        url=url,
                        description=description[:200] + "..." if len(description) > 200 else description,
                        source='Dev.to',
                        estimated_time=self._estimate_reading_time_from_text(description),
                        difficulty=self._determine_difficulty_from_text(title, description)
                    )
                    
                    articles.append(article)
                    
                    if len(articles) >= max_results:
                        break
                        
                except Exception as e:
                    continue
            
        except Exception as e:
            st.warning(f"Dev.to scraping failed: {str(e)}")
        
        return articles
    
    def scrape_freecodecamp(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Scrape educational articles from FreeCodeCamp"""
        articles = []
        
        try:
            # FreeCodeCamp search URL
            search_url = f"https://www.freecodecamp.org/news/search/?query={topic.replace(' ', '%20')}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article elements
            article_elements = soup.find_all('article', class_='post-card', limit=max_results * 2)
            
            for article_elem in article_elements:
                try:
                    # Extract title and link
                    title_elem = article_elem.find('h2', class_='post-card-title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Find link
                    link_elem = article_elem.find('a', class_='post-card-image-link')
                    if not link_elem:
                        continue
                    
                    url = link_elem.get('href')
                    if not url.startswith('http'):
                        url = urljoin('https://www.freecodecamp.org', url)
                    
                    # Extract description
                    desc_elem = article_elem.find('section', class_='post-card-excerpt')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Create LearningResource
                    article = LearningResource(
                        type='article',
                        title=title,
                        url=url,
                        description=description[:200] + "..." if len(description) > 200 else description,
                        source='FreeCodeCamp',
                        estimated_time=self._estimate_reading_time_from_text(description),
                        difficulty=self._determine_difficulty_from_text(title, description)
                    )
                    
                    articles.append(article)
                    
                    if len(articles) >= max_results:
                        break
                        
                except Exception as e:
                    continue
            
        except Exception as e:
            st.warning(f"FreeCodeCamp scraping failed: {str(e)}")
        
        return articles
    
    def scrape_educational_courses(self, topic: str, max_results: int = 3) -> List[LearningResource]:
        """Scrape educational courses from course platforms"""
        all_courses = []
        
        # For now, focus on course platforms that have searchable content
        # In a full implementation, this would scrape course catalogs
        
        try:
            # Try to find course-related content from educational sites
            st.info(f"🔍 Searching for course content about {topic}...")
            
            # For Phase 1A, return a limited set of course resources
            # In Phase 1B, this would implement full course scraping
            
            # Create some course-like resources from educational articles
            articles = self.scrape_educational_articles(topic, max_results)
            
            for article in articles:
                # Convert some articles to course-like resources if they seem comprehensive
                if self._is_comprehensive_content(article.title, article.description):
                    course = LearningResource(
                        type='course',
                        title=f"Complete Guide: {article.title}",
                        url=article.url,
                        description=article.description,
                        source=article.source,
                        estimated_time='Self-paced',
                        difficulty=article.difficulty
                    )
                    all_courses.append(course)
            
        except Exception as e:
            st.warning(f"Course scraping failed: {str(e)}")
        
        return all_courses[:max_results]
    
    def _is_comprehensive_content(self, title: str, description: str) -> bool:
        """Determine if content seems comprehensive enough to be course-like"""
        comprehensive_keywords = [
            'complete', 'comprehensive', 'guide', 'tutorial', 'course', 'learn',
            'master', 'fundamentals', 'basics', 'advanced', 'full', 'ultimate'
        ]
        
        text = f"{title} {description}".lower()
        return any(keyword in text for keyword in comprehensive_keywords)
    
    def _estimate_reading_time_from_text(self, text: str) -> str:
        """Estimate reading time based on text length"""
        word_count = len(text.split())
        
        if word_count < 100:
            return '2-5 min read'
        elif word_count < 300:
            return '5-10 min read'
        elif word_count < 600:
            return '10-15 min read'
        else:
            return '15+ min read'
    
    def _determine_difficulty_from_text(self, title: str, description: str) -> str:
        """Determine difficulty level based on text content"""
        text = f"{title} {description}".lower()
        
        # Check for beginner indicators
        if any(word in text for word in ['beginner', 'intro', 'basic', 'getting started', 'first time']):
            return 'Beginner'
        
        # Check for advanced indicators
        if any(word in text for word in ['advanced', 'expert', 'deep dive', 'masterclass']):
            return 'Advanced'
        
        # Check for intermediate indicators
        if any(word in text for word in ['intermediate', 'practical', 'hands-on', 'project']):
            return 'Intermediate'
        
        return 'Mixed'
    
    def _remove_duplicates(self, articles: List[LearningResource]) -> List[LearningResource]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article.url not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(article.url)
        
        return unique_articles 