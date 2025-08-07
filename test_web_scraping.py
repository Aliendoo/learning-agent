# test_web_scraping.py
"""
Test script for web scraping functionality
"""

import streamlit as st
from educational_site_scraper import EducationalSiteScraper

def test_web_scraping():
    """Test the web scraping functionality"""
    st.title("🧪 Web Scraping Test")
    
    # Initialize scraper
    scraper = EducationalSiteScraper()
    
    # Test topic
    test_topic = st.text_input("Enter topic to test:", value="photography")
    
    if st.button("Test Web Scraping"):
        st.info(f"Testing web scraping for: {test_topic}")
        
        # Test article scraping
        st.subheader("📄 Testing Article Scraping")
        try:
            articles = scraper.scrape_educational_articles(test_topic, max_results=3)
            st.success(f"Found {len(articles)} articles")
            
            for i, article in enumerate(articles, 1):
                with st.expander(f"Article {i}: {article.title}"):
                    st.write(f"**Source:** {article.source}")
                    st.write(f"**URL:** {article.url}")
                    st.write(f"**Description:** {article.description}")
                    st.write(f"**Time:** {article.estimated_time}")
                    st.write(f"**Difficulty:** {article.difficulty}")
                    st.write(f"**Quality Score:** {getattr(article, 'quality_score', 'N/A')}")
        except Exception as e:
            st.error(f"Article scraping failed: {str(e)}")
        
        # Test course scraping
        st.subheader("🎓 Testing Course Scraping")
        try:
            courses = scraper.scrape_educational_courses(test_topic, max_results=3)
            st.success(f"Found {len(courses)} courses")
            
            for i, course in enumerate(courses, 1):
                with st.expander(f"Course {i}: {course.title}"):
                    st.write(f"**Source:** {course.source}")
                    st.write(f"**URL:** {course.url}")
                    st.write(f"**Description:** {course.description}")
                    st.write(f"**Time:** {course.estimated_time}")
                    st.write(f"**Difficulty:** {course.difficulty}")
        except Exception as e:
            st.error(f"Course scraping failed: {str(e)}")

if __name__ == "__main__":
    test_web_scraping() 