# Web Scraping Fallback System

## Overview

The Learning Agent now includes a robust web scraping fallback system that automatically activates when the Google Search API is unavailable, rate-limited, or not configured. This ensures users always get relevant educational resources, even without API access.

## How It Works

### 1. Smart Fallback Hierarchy
```
1. Google Search API (Primary) - Real-time, high-quality results
2. Web Scraping (Secondary) - When API is rate-limited or unavailable  
3. Mock/Static Resources (Tertiary) - Last resort
```

### 2. Educational Site Targeting

The web scraper targets high-quality educational platforms:

**For Articles:**
- **Medium** - Educational articles and tutorials
- **Dev.to** - Developer tutorials and guides
- **FreeCodeCamp** - Free educational content
- **CSS-Tricks** - Web development resources
- **Smashing Magazine** - Design and development articles

**For Courses:**
- Converts comprehensive articles into course-like resources
- Identifies content that covers complete topics
- Provides structured learning paths

### 3. Respectful Scraping

The scraper implements best practices:
- **Rate limiting**: Delays between requests (1-2 seconds)
- **User-Agent**: Proper identification as educational research bot
- **Error handling**: Graceful fallback when sites are unavailable
- **Content filtering**: Only extracts educational content

## Features

### ✅ Intelligent Content Detection
- Filters for educational content only
- Excludes discussion forums and non-educational sites
- Identifies comprehensive guides vs. simple articles

### ✅ Quality Assessment
- Scores content based on relevance and comprehensiveness
- Estimates reading time based on content length
- Determines difficulty level from content analysis

### ✅ Duplicate Removal
- Removes duplicate articles from multiple sources
- Prioritizes higher-quality content
- Returns unique, relevant resources

### ✅ Error Resilience
- Continues scraping if one site fails
- Provides clear feedback about scraping status
- Graceful degradation when sites are unavailable

## Usage

### Automatic Activation
The web scraping fallback activates automatically when:
- Google Search API is not configured
- API rate limits are reached
- API requests fail

### Manual Testing
You can test the web scraping functionality:

```bash
streamlit run test_web_scraping.py
```

This will let you test scraping for any topic and see the results.

## Configuration

### Required Dependencies
The following packages are already included in `requirements.txt`:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser

### Environment Variables
No additional environment variables are needed for web scraping. It works automatically when Google Search API is not available.

## Example Flow

1. **User searches for "photography"**
2. **System checks Google Search API availability**
3. **If API unavailable:**
   - Shows "Using web scraping fallback..."
   - Scrapes Medium, Dev.to, FreeCodeCamp
   - Filters and ranks results
   - Returns photography-specific educational resources
4. **User gets real photography content instead of generic fallback**

## Benefits

### 🔄 Reliability
- No dependency on external APIs
- Works even when APIs are down
- Multiple fallback sources

### 🎯 Quality
- Targets only educational sites
- Filters for relevant content
- Provides structured learning resources

### 🚀 Performance
- Fast response times
- Efficient content extraction
- Minimal resource usage

### 🛡️ Safety
- Respectful scraping practices
- Proper error handling
- No impact on target sites

## Future Enhancements

### Phase 1B Improvements
- Add more educational sites (Coursera, Udemy, etc.)
- Implement course catalog scraping
- Add content caching for better performance
- Enhanced quality scoring algorithms

### Advanced Features
- Content summarization
- Learning path generation
- Interactive content detection
- Multi-language support

## Troubleshooting

### Common Issues

**No results found:**
- Check internet connection
- Verify target sites are accessible
- Try different search terms

**Scraping errors:**
- Sites may have changed their structure
- Rate limiting may be in effect
- Network connectivity issues

**Performance issues:**
- Reduce max_results parameter
- Check system resources
- Verify network speed

## Support

The web scraping system is designed to be robust and self-healing. If you encounter issues:

1. Check the console output for error messages
2. Verify your internet connection
3. Try the test script to isolate issues
4. Check if target sites are accessible in your browser

The system will automatically fall back to alternative methods if scraping fails. 