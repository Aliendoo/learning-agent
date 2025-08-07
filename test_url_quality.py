#!/usr/bin/env python3
"""
Comprehensive URL quality test script
Tests that all generated URLs are direct content URLs, not search URLs
"""

import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def is_search_url(url: str) -> bool:
    """Check if a URL is a search URL (should be avoided)"""
    search_patterns = [
        r'google\.com/search',
        r'google\.com/url',
        r'bing\.com/search',
        r'duckduckgo\.com',
        r'youtube\.com/results',
        r'medium\.com/search',
        r'stackoverflow\.com/search',
        r'reddit\.com/.*search',
        r'coursera\.org/search',
        r'edx\.org/search',
        r'udemy\.com/courses/search',
        r'freecodecamp\.org/news/search',
        r'github\.com/search',
        r'wikipedia\.org/wiki/Special:Search'
    ]
    
    for pattern in search_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False

def is_direct_content_url(url: str) -> bool:
    """Check if a URL is a direct content URL (preferred)"""
    direct_content_patterns = [
        r'youtube\.com/watch',
        r'freecodecamp\.org/news/',
        r'freecodecamp\.org/learn/',
        r'realpython\.com/',
        r'docs\.python\.org/',
        r'developer\.mozilla\.org/',
        r'javascript\.info/',
        r'eloquentjavascript\.net/',
        r'coursera\.org/learn/',
        r'coursera\.org/specializations/',
        r'edx\.org/course/',
        r'udemy\.com/course/',
        r'kaggle\.com/learn',
        r'course\.fast\.ai/',
        r'theodinproject\.com/',
        r'lab\.github\.com/',
        r'dev\.to/',
        r'github\.com/.*/.*'  # GitHub repos
    ]
    
    for pattern in direct_content_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False

def test_individual_fetchers():
    """Test each fetcher method individually"""
    print("🧪 Testing individual fetchers...")
    
    try:
        from resource_fetchers import YouTubeResourceFetcher, EducationalArticleScraper, CoursePlatformFetcher
        
        # Test YouTube fetcher
        print("\n📺 Testing YouTube fetcher...")
        youtube_fetcher = YouTubeResourceFetcher()
        videos = youtube_fetcher.search_educational_videos("Python tutorial", max_results=2)
        
        for i, video in enumerate(videos, 1):
            print(f"   Video {i}: {video.title}")
            print(f"      URL: {video.url}")
            if is_search_url(video.url):
                print(f"      ❌ SEARCH URL DETECTED!")
            elif is_direct_content_url(video.url):
                print(f"      ✅ Direct content URL")
            else:
                print(f"      ⚠️ Unknown URL type")
        
        # Test article scraper
        print("\n📄 Testing article scraper...")
        article_scraper = EducationalArticleScraper()
        articles = article_scraper.search_educational_articles("Python", max_results=3)
        
        for i, article in enumerate(articles, 1):
            print(f"   Article {i}: {article.title}")
            print(f"      URL: {article.url}")
            if is_search_url(article.url):
                print(f"      ❌ SEARCH URL DETECTED!")
            elif is_direct_content_url(article.url):
                print(f"      ✅ Direct content URL")
            else:
                print(f"      ⚠️ Unknown URL type")
        
        # Test course fetcher
        print("\n🎓 Testing course fetcher...")
        course_fetcher = CoursePlatformFetcher()
        courses = course_fetcher.search_all_platforms("Python", max_results=3)
        
        for i, course in enumerate(courses, 1):
            print(f"   Course {i}: {course.title}")
            print(f"      URL: {course.url}")
            if is_search_url(course.url):
                print(f"      ❌ SEARCH URL DETECTED!")
            elif is_direct_content_url(course.url):
                print(f"      ✅ Direct content URL")
            else:
                print(f"      ⚠️ Unknown URL type")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual fetcher test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_url_validation():
    """Test URL validation functions"""
    print("\n🔍 Testing URL validation functions...")
    
    # Test search URLs
    search_urls = [
        "https://www.google.com/search?q=python+tutorial",
        "https://medium.com/search?q=javascript",
        "https://stackoverflow.com/search?q=python",
        "https://www.coursera.org/search?query=python",
        "https://www.youtube.com/results?search_query=python"
    ]
    
    for url in search_urls:
        if is_search_url(url):
            print(f"   ✅ Correctly identified search URL: {url}")
        else:
            print(f"   ❌ Failed to identify search URL: {url}")
    
    # Test direct content URLs
    direct_urls = [
        "https://www.youtube.com/watch?v=abc123",
        "https://www.freecodecamp.org/news/python-tutorial/",
        "https://realpython.com/python-basics/",
        "https://docs.python.org/3/tutorial/",
        "https://www.coursera.org/learn/python"
    ]
    
    for url in direct_urls:
        if is_direct_content_url(url):
            print(f"   ✅ Correctly identified direct content URL: {url}")
        else:
            print(f"   ❌ Failed to identify direct content URL: {url}")
    
    return True

def test_course_generation_urls():
    """Test complete course generation for URL quality"""
    print("\n🎓 Testing complete course generation URLs...")
    
    try:
        from course_generator import EnhancedCourseGenerator
        
        # Create test preferences
        preferences = {
            'topic': 'Python programming',
            'current_level': 'beginner',
            'goal_level': 'intermediate',
            'timeline': '2 months',
            'purpose': 'career development',
            'time_availability': '1 hour',
            'learning_style': ['visual', 'kinesthetic'],
            'content_format': ['video', 'interactive'],
            'engagement_style': 'fun and engaging'
        }
        
        # Generate course
        generator = EnhancedCourseGenerator()
        result = generator.generate_course_with_real_resources(preferences)
        
        if not result or 'course' not in result:
            print("   ❌ Course generation failed")
            return False
        
        course = result['course']
        all_resources = result.get('all_resources', {})
        
        print(f"   Course: {course.title}")
        print(f"   Modules: {len(course.modules)}")
        
        # Check all resources for URL quality
        total_resources = 0
        search_urls_found = 0
        direct_urls_found = 0
        unknown_urls = 0
        
        for module in course.modules:
            print(f"\n   Module: {module.title}")
            for resource in module.resources:
                total_resources += 1
                print(f"      Resource: {resource.title}")
                print(f"         URL: {resource.url}")
                
                if is_search_url(resource.url):
                    print(f"         ❌ SEARCH URL DETECTED!")
                    search_urls_found += 1
                elif is_direct_content_url(resource.url):
                    print(f"         ✅ Direct content URL")
                    direct_urls_found += 1
                else:
                    print(f"         ⚠️ Unknown URL type")
                    unknown_urls += 1
        
        # Summary
        print(f"\n📊 URL Quality Summary:")
        print(f"   Total resources: {total_resources}")
        print(f"   Direct content URLs: {direct_urls_found}")
        print(f"   Search URLs: {search_urls_found}")
        print(f"   Unknown URLs: {unknown_urls}")
        
        if search_urls_found > 0:
            print(f"   ❌ {search_urls_found} search URLs found - needs fixing!")
            return False
        else:
            print(f"   ✅ All URLs are direct content URLs!")
            return True
        
    except Exception as e:
        print(f"❌ Course generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_url_report():
    """Generate a comprehensive URL quality report"""
    print("\n📋 Generating URL quality report...")
    
    try:
        from resource_fetchers import YouTubeResourceFetcher, EducationalArticleScraper, CoursePlatformFetcher
        
        report = {
            'youtube': {'total': 0, 'direct': 0, 'search': 0, 'unknown': 0},
            'articles': {'total': 0, 'direct': 0, 'search': 0, 'unknown': 0},
            'courses': {'total': 0, 'direct': 0, 'search': 0, 'unknown': 0}
        }
        
        # Test topics
        test_topics = ['python', 'javascript', 'web development', 'machine learning']
        
        youtube_fetcher = YouTubeResourceFetcher()
        article_scraper = EducationalArticleScraper()
        course_fetcher = CoursePlatformFetcher()
        
        for topic in test_topics:
            print(f"\n   Testing topic: {topic}")
            
            # YouTube
            videos = youtube_fetcher.search_educational_videos(f"{topic} tutorial", max_results=2)
            for video in videos:
                report['youtube']['total'] += 1
                if is_search_url(video.url):
                    report['youtube']['search'] += 1
                elif is_direct_content_url(video.url):
                    report['youtube']['direct'] += 1
                else:
                    report['youtube']['unknown'] += 1
            
            # Articles
            articles = article_scraper.search_educational_articles(topic, max_results=3)
            for article in articles:
                report['articles']['total'] += 1
                if is_search_url(article.url):
                    report['articles']['search'] += 1
                elif is_direct_content_url(article.url):
                    report['articles']['direct'] += 1
                else:
                    report['articles']['unknown'] += 1
            
            # Courses
            courses = course_fetcher.search_all_platforms(topic, max_results=2)
            for course in courses:
                report['courses']['total'] += 1
                if is_search_url(course.url):
                    report['courses']['search'] += 1
                elif is_direct_content_url(course.url):
                    report['courses']['direct'] += 1
                else:
                    report['courses']['unknown'] += 1
        
        # Print report
        print(f"\n📊 URL Quality Report:")
        print(f"   YouTube Videos:")
        print(f"      Total: {report['youtube']['total']}")
        print(f"      Direct: {report['youtube']['direct']}")
        print(f"      Search: {report['youtube']['search']}")
        print(f"      Unknown: {report['youtube']['unknown']}")
        
        print(f"   Articles:")
        print(f"      Total: {report['articles']['total']}")
        print(f"      Direct: {report['articles']['direct']}")
        print(f"      Search: {report['articles']['search']}")
        print(f"      Unknown: {report['articles']['unknown']}")
        
        print(f"   Courses:")
        print(f"      Total: {report['courses']['total']}")
        print(f"      Direct: {report['courses']['direct']}")
        print(f"      Search: {report['courses']['search']}")
        print(f"      Unknown: {report['courses']['unknown']}")
        
        # Overall assessment
        total_search = report['youtube']['search'] + report['articles']['search'] + report['courses']['search']
        total_direct = report['youtube']['direct'] + report['articles']['direct'] + report['courses']['direct']
        
        if total_search == 0:
            print(f"\n   ✅ EXCELLENT: No search URLs found!")
        else:
            print(f"\n   ⚠️ WARNING: {total_search} search URLs found")
        
        print(f"   📈 Direct content URLs: {total_direct}")
        
        return total_search == 0
        
    except Exception as e:
        print(f"❌ URL report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive URL quality tests"""
    print("🧪 Starting comprehensive URL quality tests...\n")
    
    all_tests_passed = True
    
    # Test 1: URL validation functions
    if not test_url_validation():
        all_tests_passed = False
    
    # Test 2: Individual fetchers
    if not test_individual_fetchers():
        all_tests_passed = False
    
    # Test 3: Complete course generation
    if not test_course_generation_urls():
        all_tests_passed = False
    
    # Test 4: Generate comprehensive report
    if not generate_url_report():
        all_tests_passed = False
    
    # Final summary
    print(f"\n🎯 Final Results:")
    if all_tests_passed:
        print(f"   ✅ All URL quality tests passed!")
        print(f"   🎉 No search URLs detected in any resources!")
    else:
        print(f"   ❌ Some URL quality tests failed!")
        print(f"   🔧 Search URLs detected - fixes needed!")
    
    return all_tests_passed

if __name__ == "__main__":
    main() 