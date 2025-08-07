# test_hybrid_fetcher.py
import streamlit as st
from hybrid_resource_fetcher import HybridResourceFetcher

def test_hybrid_fetcher():
    """Test the hybrid resource fetcher (Phase 1A)"""
    
    st.title("🧪 Test Hybrid Resource Fetcher - Phase 1A")
    st.markdown("**Testing Google Search API for articles only, with rate limiting**")
    
    # Initialize the hybrid fetcher
    fetcher = HybridResourceFetcher()
    
    # Show API status
    usage_info = fetcher.get_api_usage_info()
    
    st.sidebar.subheader("🔧 API Status")
    st.sidebar.success("✅ Google Search API" if usage_info['google_search_available'] else "❌ Google Search API")
    st.sidebar.success("✅ YouTube API" if usage_info['youtube_available'] else "❌ YouTube API")
    
    st.sidebar.subheader("📊 Rate Limiting")
    st.sidebar.metric("Queries Used", usage_info['daily_queries_used'])
    st.sidebar.metric("Queries Remaining", usage_info['queries_remaining'])
    st.sidebar.metric("Daily Limit", usage_info['max_daily_queries'])
    
    # Test topic
    topic = st.text_input("Enter a topic to search:", value="python basics")
    
    if st.button("Test Hybrid Fetcher"):
        if topic:
            with st.spinner("Testing hybrid resource fetcher..."):
                
                # Sample preferences
                preferences = {
                    'content_format': ['video', 'text', 'interactive'],  # Test videos, articles, and courses
                    'learning_style': ['visual', 'reading'],
                    'current_level': 'beginner'
                }
                
                # Fetch resources
                resources = fetcher.fetch_all_resources(topic, preferences)
                
                # Display results
                st.subheader("📺 Videos (YouTube API - Existing)")
                if resources['videos']:
                    for i, video in enumerate(resources['videos'], 1):
                        with st.expander(f"{i}. {video.title}"):
                            st.write(f"**Source:** {video.source}")
                            st.write(f"**URL:** {video.url}")
                            st.write(f"**Time:** {video.estimated_time}")
                            st.write(f"**Quality Score:** {getattr(video, 'quality_score', 'N/A')}")
                else:
                    st.info("No videos found")
                
                st.subheader("📄 Articles (Google Search API - NEW)")
                if resources['articles']:
                    for i, article in enumerate(resources['articles'], 1):
                        with st.expander(f"{i}. {article.title}"):
                            st.write(f"**Source:** {article.source}")
                            st.write(f"**URL:** {article.url}")
                            st.write(f"**Time:** {article.estimated_time}")
                            st.write(f"**Difficulty:** {article.difficulty}")
                            st.write(f"**Quality Score:** {getattr(article, 'quality_score', 'N/A')}")
                else:
                    st.info("No articles found")
                
                st.subheader("🎓 Courses (Google Search API - NEW)")
                if resources['courses']:
                    for i, course in enumerate(resources['courses'], 1):
                        with st.expander(f"{i}. {course.title}"):
                            st.write(f"**Source:** {course.source}")
                            st.write(f"**URL:** {course.url}")
                            st.write(f"**Difficulty:** {course.difficulty}")
                            st.write(f"**Quality Score:** {getattr(course, 'quality_score', 'N/A')}")
                else:
                    st.info("No courses found")
                
                st.subheader("📚 Documentation (Removed)")
                st.info("Documentation fetching removed as requested")
                
                # Show updated usage info
                st.subheader("📊 Updated API Usage")
                updated_usage = fetcher.get_api_usage_info()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Queries Used", updated_usage['daily_queries_used'])
                with col2:
                    st.metric("Queries Remaining", updated_usage['queries_remaining'])
                with col3:
                    st.metric("Daily Limit", updated_usage['max_daily_queries'])

def show_phase_info():
    """Show information about the current phase"""
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Phase 1A Testing")
    st.sidebar.markdown("""
    **Current Phase:**
    - ✅ Articles: Google Search API
    - ✅ Videos: YouTube API (existing)
    - ✅ Courses: Google Search API
    - ❌ Documentation: Removed
    
    **Safety Features:**
    - Rate limiting (50 queries/day)
    - Error handling
    - Fallback mechanisms
    - Community site filtering
    - Trusted course platforms only
    """)

if __name__ == "__main__":
    st.set_page_config(page_title="Test Hybrid Fetcher", layout="wide")
    
    show_phase_info()
    test_hybrid_fetcher() 