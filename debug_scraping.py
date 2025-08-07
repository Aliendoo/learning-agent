#!/usr/bin/env python3
"""
Debug script for web scraping issues
"""

import requests
from bs4 import BeautifulSoup
import time

def test_medium_scraping():
    """Test Medium scraping"""
    print("=== Testing Medium ===")
    try:
        response = requests.get('https://medium.com/search?q=photography', timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
        
        # Check for different selectors
        articles = soup.find_all('article')
        print(f"Article elements: {len(articles)}")
        
        # Check for any links with /p/ pattern
        links = soup.find_all('a', href=True)
        medium_links = [link for link in links if '/p/' in link.get('href')]
        print(f"Medium article links: {len(medium_links)}")
        
        # Check for script tags (JavaScript)
        scripts = soup.find_all('script')
        print(f"Script tags: {len(scripts)}")
        
        if len(scripts) > 10:
            print("⚠️  This appears to be a JavaScript-heavy page")
        
    except Exception as e:
        print(f"Error: {e}")

def test_dev_to_scraping():
    """Test Dev.to scraping"""
    print("\n=== Testing Dev.to ===")
    try:
        response = requests.get('https://dev.to/search?q=photography', timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
        
        # Check for article elements
        articles = soup.find_all('div', class_='crayons-story')
        print(f"Crayons-story elements: {len(articles)}")
        
        if articles:
            article = articles[0]
            title_elem = article.find('a', class_='crayons-story__title')
            if title_elem:
                print(f"First article title: {title_elem.get_text(strip=True)[:50]}...")
                print(f"First article URL: {title_elem.get('href')}")
        
        # Check for script tags
        scripts = soup.find_all('script')
        print(f"Script tags: {len(scripts)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_freecodecamp_scraping():
    """Test FreeCodeCamp scraping"""
    print("\n=== Testing FreeCodeCamp ===")
    try:
        response = requests.get('https://www.freecodecamp.org/news/search/?query=photography', timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
        
        # Check for article elements
        articles = soup.find_all('article', class_='post-card')
        print(f"Post-card elements: {len(articles)}")
        
        # Check for any article-like elements
        all_articles = soup.find_all('article')
        print(f"All article elements: {len(all_articles)}")
        
        # Check for script tags
        scripts = soup.find_all('script')
        print(f"Script tags: {len(scripts)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_alternative_sites():
    """Test alternative educational sites that might work better"""
    print("\n=== Testing Alternative Sites ===")
    
    # Test sites that might have static content
    test_sites = [
        ('CSS-Tricks', 'https://css-tricks.com/?s=photography'),
        ('Smashing Magazine', 'https://www.smashingmagazine.com/search/?q=photography'),
        ('SitePoint', 'https://www.sitepoint.com/?s=photography')
    ]
    
    for site_name, url in test_sites:
        print(f"\n--- {site_name} ---")
        try:
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"Title: {soup.title.string if soup.title else 'No title'}")
            
            # Look for common article patterns
            articles = soup.find_all(['article', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['post', 'article', 'entry', 'card']))
            print(f"Potential article elements: {len(articles)}")
            
            # Look for links
            links = soup.find_all('a', href=True)
            print(f"Total links: {len(links)}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_medium_scraping()
    test_dev_to_scraping()
    test_freecodecamp_scraping()
    test_alternative_sites() 