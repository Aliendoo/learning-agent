# test_new_fetcher.py
import streamlit as st
from google_search_resource_fetcher import GoogleSearchResourceFetcher

def test_new_fetcher():
    """Test the new GoogleSearchResourceFetcher"""
    
    st.title("Test New Google Search Resource Fetcher")
    
    # Initialize the new fetcher
    fetcher = GoogleSearchResourceFetcher()
    
    # Test topic
    topic = st.text_input("Enter a topic to search:", value="python programming")
    
    if st.button("Test New Fetcher"):
        if topic:
            with st.spinner("Testing new resource fetcher..."):
                
                # Sample preferences
                preferences = {
                    'content_format': ['video', 'text', 'interactive'],
                    'learning_style': ['visual', 'reading'],
                    'current_level': 'beginner'
                }
                
                # Fetch resources
                resources = fetcher.fetch_all_resources(topic, preferences)
                
                # Display results
                st.subheader("📺 Videos")
                for i, video in enumerate(resources['videos'][:3], 1):
                    with st.expander(f"{i}. {video.title}"):
                        st.write(f"**Source:** {video.source}")
                        st.write(f"**URL:** {video.url}")
                        st.write(f"**Time:** {video.estimated_time}")
                        st.write(f"**Quality Score:** {getattr(video, 'quality_score', 'N/A')}")
                
                st.subheader("📄 Articles")
                for i, article in enumerate(resources['articles'][:3], 1):
                    with st.expander(f"{i}. {article.title}"):
                        st.write(f"**Source:** {article.source}")
                        st.write(f"**URL:** {article.url}")
                        st.write(f"**Time:** {article.estimated_time}")
                        st.write(f"**Difficulty:** {article.difficulty}")
                        st.write(f"**Quality Score:** {getattr(article, 'quality_score', 'N/A')}")
                
                st.subheader("🎓 Courses")
                for i, course in enumerate(resources['courses'][:2], 1):
                    with st.expander(f"{i}. {course.title}"):
                        st.write(f"**Source:** {course.source}")
                        st.write(f"**URL:** {course.url}")
                        st.write(f"**Difficulty:** {course.difficulty}")
                        st.write(f"**Quality Score:** {getattr(course, 'quality_score', 'N/A')}")
                
                st.subheader("📚 Documentation")
                for i, doc in enumerate(resources['documentation'][:2], 1):
                    with st.expander(f"{i}. {doc.title}"):
                        st.write(f"**Source:** {doc.source}")
                        st.write(f"**URL:** {doc.url}")
                        st.write(f"**Quality Score:** {getattr(doc, 'quality_score', 'N/A')}")

if __name__ == "__main__":
    st.set_page_config(page_title="Test New Fetcher", layout="wide")
    test_new_fetcher() 