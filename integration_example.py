# integration_example.py
"""
Example of how to integrate Google Search API into existing resource fetchers
This shows the minimal changes needed to replace web scraping with Google Search API
"""

import streamlit as st
from google_search_integration import (
    get_google_articles, 
    get_google_courses, 
    get_google_documentation,
    get_google_search_results
)

def example_integration():
    """Example of how to use Google Search API instead of web scraping"""
    
    st.title("Google Search API Integration Example")
    
    topic = st.text_input("Enter a topic to search:", value="python programming")
    
    if st.button("Search with Google API"):
        if topic:
            with st.spinner("Searching with Google Search API..."):
                
                # Example 1: Replace article scraping
                st.subheader("📄 Articles (replaces web scraping)")
                articles = get_google_articles(topic, max_results=4)
                for i, article in enumerate(articles, 1):
                    with st.expander(f"{i}. {article.title}"):
                        st.write(f"**Source:** {article.source}")
                        st.write(f"**URL:** {article.url}")
                        st.write(f"**Description:** {article.description}")
                        st.write(f"**Time:** {article.estimated_time}")
                        st.write(f"**Difficulty:** {article.difficulty}")
                
                # Example 2: Replace course scraping
                st.subheader("🎓 Courses (replaces course platform scraping)")
                courses = get_google_courses(topic, max_results=3)
                for i, course in enumerate(courses, 1):
                    with st.expander(f"{i}. {course.title}"):
                        st.write(f"**Source:** {course.source}")
                        st.write(f"**URL:** {course.url}")
                        st.write(f"**Description:** {course.description}")
                        st.write(f"**Time:** {course.estimated_time}")
                
                # Example 3: Replace documentation scraping
                st.subheader("📚 Documentation (replaces manual curated docs)")
                docs = get_google_documentation(topic, max_results=2)
                for i, doc in enumerate(docs, 1):
                    with st.expander(f"{i}. {doc.title}"):
                        st.write(f"**Source:** {doc.source}")
                        st.write(f"**URL:** {doc.url}")
                        st.write(f"**Description:** {doc.description}")

def show_integration_code():
    """Show the code changes needed for integration"""
    
    st.subheader("🔧 Code Integration Examples")
    
    st.markdown("""
    ### 1. Replace Article Scraping
    
    **Before (Web Scraping):**
    ```python
    # In EducationalArticleScraper
    articles = self.article_scraper.search_educational_articles(topic, max_results=6)
    ```
    
    **After (Google Search API):**
    ```python
    # Import the integration
    from google_search_integration import get_google_articles
    
    # Replace the scraping call
    articles = get_google_articles(topic, max_results=6)
    ```
    
    ### 2. Replace Course Scraping
    
    **Before (Web Scraping):**
    ```python
    # In CoursePlatformFetcher
    courses = self.course_fetcher.search_all_platforms(topic, max_results=4)
    ```
    
    **After (Google Search API):**
    ```python
    # Import the integration
    from google_search_integration import get_google_courses
    
    # Replace the scraping call
    courses = get_google_courses(topic, max_results=4)
    ```
    
    ### 3. Replace Documentation Scraping
    
    **Before (Manual Curated):**
    ```python
    # In OfficialDocumentationFetcher
    docs = self.documentation_fetcher.search_official_docs(topic, max_results=3)
    ```
    
    **After (Google Search API):**
    ```python
    # Import the integration
    from google_search_integration import get_google_documentation
    
    # Replace the manual curated call
    docs = get_google_documentation(topic, max_results=3)
    ```
    """)

if __name__ == "__main__":
    st.set_page_config(page_title="Google Search Integration Example", layout="wide")
    
    tab1, tab2 = st.tabs(["Live Example", "Integration Code"])
    
    with tab1:
        example_integration()
    
    with tab2:
        show_integration_code() 