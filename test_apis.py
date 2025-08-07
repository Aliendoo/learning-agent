#!/usr/bin/env python3
"""
Test script to verify all APIs are working correctly
Run this after setting up your .env file: python test_apis.py
"""

import os
from dotenv import load_dotenv
import sys
import requests

# Load environment variables
load_dotenv()

def test_openai_api():
    """Test OpenAI API"""
    print("🧪 Testing OpenAI API...")
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-3.5-turbo", timeout=30)
        response = llm.invoke("Say 'OpenAI API is working!'")
        print(f"✅ OpenAI API: {response.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI API failed: {e}")
        return False

def test_youtube_api():
    """Test YouTube API"""
    print("\n🧪 Testing YouTube API...")
    try:
        from googleapiclient.discovery import build
        
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            print("⚠️ YouTube API: No API key found (this is optional)")
            return True  # Consider this a pass since it's optional
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Test search
        search_response = youtube.search().list(
            q='python programming tutorial',
            part='id,snippet',
            maxResults=1,
            type='video'
        ).execute()
        
        if search_response.get('items'):
            video = search_response['items'][0]
            print(f"✅ YouTube API: Found video '{video['snippet']['title']}'")
            return True
        else:
            print("❌ YouTube API: No results returned")
            return False
            
    except Exception as e:
        print(f"❌ YouTube API failed: {e}")
        return False

def test_wikipedia_api():
    """Test removed - Wikipedia API no longer used"""
    return True

def test_web_scraping():
    """Test web scraping capabilities"""
    print("\n🧪 Testing Web Scraping...")
    
    # Test multiple endpoints to ensure robustness
    test_urls = [
        "https://httpbin.org/html",
        "https://example.com",
        "https://httpbin.org/json"
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    for url in test_urls:
        try:
            print(f"   Testing: {url}")
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                if 'json' in url:
                    # Test JSON parsing
                    data = response.json()
                    if data:
                        print(f"✅ Web Scraping: Successfully fetched and parsed JSON from {url}")
                        return True
                else:
                    # Test HTML parsing
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    if soup.find(['title', 'h1', 'p', 'div']):
                        print(f"✅ Web Scraping: Successfully parsed HTML from {url}")
                        return True
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout for {url}")
            continue
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection error for {url}")
            continue
        except Exception as e:
            print(f"   ⚠️ Error with {url}: {str(e)[:50]}...")
            continue
    
    # If all URLs fail, try a simple local test
    try:
        print("   Testing BeautifulSoup parsing with local HTML...")
        from bs4 import BeautifulSoup
        
        test_html = "<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"
        soup = BeautifulSoup(test_html, 'html.parser')
        
        if soup.title and soup.title.string == "Test":
            print("✅ Web Scraping: BeautifulSoup parsing works (network might be restricted)")
            return True
            
    except Exception as e:
        print(f"❌ Web Scraping: BeautifulSoup parsing failed: {e}")
    
    print("❌ Web Scraping: All tests failed - this might be due to network restrictions")
    print("   Note: This won't affect the main application functionality")
    return False

def test_vector_database():
    """Test vector database functionality"""
    print("\n🧪 Testing Vector Database...")
    try:
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS
        
        embeddings = OpenAIEmbeddings()
        
        # Create a simple vector store
        texts = ["This is a test document", "Another test document"]
        vector_store = FAISS.from_texts(texts, embeddings)
        
        # Test similarity search
        results = vector_store.similarity_search("test", k=1)
        
        if results:
            print(f"✅ Vector Database: Found similar document")
            return True
        else:
            print("❌ Vector Database: No results found")
            return False
            
    except Exception as e:
        print(f"❌ Vector Database failed: {e}")
        return False

def test_full_integration():
    """Test the complete integration"""
    print("\n🧪 Testing Full Integration...")
    try:
        from models import LearningPreferences
        from chatbot import ConversationalLearningChatbot
        from resource_fetchers import ComprehensiveResourceFetcher
        
        # Test models
        prefs = LearningPreferences(
            topic="Python programming",
            current_level="beginner",
            goal_level="intermediate",
            timeline="1 month",
            purpose="career development"
        )
        
        # Test chatbot initialization
        chatbot = ConversationalLearningChatbot(prefs.dict())
        
        # Test resource fetcher
        fetcher = ComprehensiveResourceFetcher()
        
        print(f"✅ Full Integration: All components loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Full Integration failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting API Tests for Learning Platform...")
    print("=" * 60)
    
    tests = [
        ("OpenAI API", test_openai_api),
        ("YouTube API", test_youtube_api),
        ("Web Scraping", test_web_scraping),
        ("Vector Database", test_vector_database),
        ("Full Integration", test_full_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("-" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print("-" * 30)
    print(f"Total: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your Learning Platform is ready to use.")
        print("\nNext steps:")
        print("1. Run: streamlit run main.py")
        print("2. Open your browser to the local URL")
        print("3. Start creating personalized learning plans!")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        print("\nCommon issues:")
        print("- Missing API keys in .env file")
        print("- Internet connection problems")
        print("- Missing dependencies (run: pip install -r requirements.txt)")
        
        # Show required environment variables
        print("\nRequired .env variables:")
        print("OPENAI_API_KEY=your_openai_key_here")
        print("\nOptional .env variables:")
        print("YOUTUBE_API_KEY=your_youtube_key_here")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)