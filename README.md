# 🎓 AI Learning Platform

An intelligent, personalized learning platform that creates customized educational courses with real resources from trusted educational sites.

## 🚀 Features

- **Personalized Learning Plans**: AI-generated courses tailored to your goals
- **Real Educational Resources**: Direct access to Khan Academy, YouTube, Wikipedia, Coursera, and more
- **Smart Resource Fetching**: Google Search API with fallback to educational sites
- **Interactive Chatbot**: Conversational interface to refine your learning plan
- **Quality Assessment**: Intelligent scoring and ranking of educational content

## 📁 Project Structure

### **Core Application**
- `main.py` - Main Streamlit application
- `chatbot.py` - Conversational AI chatbot
- `course_generator.py` - Course generation with real resources
- `models.py` - Data models and structures

### **Resource Fetching**
- `hybrid_resource_fetcher.py` - Google Search API + educational site fallback
- `simple_educational_searcher.py` - Direct access to educational sites
- `objective_based_fetcher.py` - Resource fetching based on learning objectives

### **AI & Analysis**
- `topic_detector.py` - Topic analysis and categorization
- `quality_scorer.py` - Content quality assessment

### **Configuration**
- `config.py` - API configuration management
- `requirements.txt` - Python dependencies

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aliendoo/learning-agent.git
   cd learning-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file with:
   ```bash
   # Required
   OPENAI_API_KEY=your_openai_key
   
   # Google Search API (Recommended)
   GOOGLE_SEARCH_API_KEY=your_google_search_key
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
   
   # YouTube API (Optional)
   YOUTUBE_API_KEY=your_youtube_key
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

## 🎯 How It Works

### **1. Learning Plan Creation**
- Fill out a form with your learning goals
- Specify your current level, timeline, and preferences
- AI analyzes your topic and creates a personalized plan

### **2. Interactive Refinement**
- Chat with the AI to refine your learning plan
- Ask questions, make adjustments, or add specific requirements
- Get real-time feedback and suggestions

### **3. Resource Discovery**
- **Primary**: Google Search API for real-time results
- **Fallback**: Direct access to educational sites (Khan Academy, YouTube, Wikipedia, etc.)
- **Smart Categorization**: Topic-specific site selection

### **4. Course Generation**
- AI creates structured learning modules
- Each module includes relevant resources
- Quality scoring ensures high-value content

## 🔧 API Setup

### **OpenAI API (Required)**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an account and get your API key
3. Add to `.env` file

### **Google Search API (Recommended)**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Custom Search API
3. Create API key and Search Engine ID
4. Add to `.env` file

### **YouTube API (Optional)**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable YouTube Data API v3
3. Create API key
4. Add to `.env` file

## 🎉 Example Usage

1. **Start the app**: `streamlit run main.py`
2. **Enter your topic**: "photography", "python programming", "digital marketing"
3. **Fill out preferences**: Current level, timeline, learning style
4. **Chat with AI**: Refine your learning plan
5. **Generate course**: Get a personalized course with real resources

## 🔄 Resource Fetching Strategy

### **Smart Fallback System**
```
1. Google Search API (Primary)
   ↓ (if unavailable)
2. Simple Educational Searcher (Fallback)
   ↓ (if unavailable)
3. Curated Resources (Final fallback)
```

### **Educational Sites Used**
- **Universal**: Khan Academy, YouTube, Wikipedia, Coursera, FreeCodeCamp, TED-Ed, edX
- **Programming**: Real Python, Dev.to, CSS-Tricks
- **Photography**: Digital Photography School, Photography Life
- **Design**: Smashing Magazine, Awwwards

## 📊 Features

### **✅ What Works**
- Personalized course generation
- Real educational resource discovery
- Interactive chatbot interface
- Quality content assessment
- Smart fallback mechanisms
- Topic-specific site targeting

### **🎯 Key Benefits**
- **No more irrelevant content**: Photography searches return photography resources
- **Reliable resource discovery**: Works even when APIs are unavailable
- **High-quality content**: Direct access to trusted educational sites
- **Personalized learning**: AI-tailored to your specific needs

## 🚀 Future Enhancements

### **Phase 1B**
- Enhanced topic categorization
- More educational sites
- Content caching for performance
- Advanced quality scoring

### **Phase 2**
- Learning progress tracking
- Interactive exercises
- Community features
- Mobile app

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your API keys are correctly set
3. Ensure all dependencies are installed
4. Check the documentation in `SIMPLE_SEARCHER_README.md`

---

**Built with ❤️ for personalized learning** 