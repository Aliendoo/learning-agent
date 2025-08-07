# 🎓 AI-Powered Personalized Learning Platform

A sophisticated multi-agent AI system that creates personalized learning courses with real educational resources. The platform uses LangGraph to orchestrate multiple AI agents that work together to generate customized learning paths based on user preferences, timeline, and learning goals.

## ✨ Features

### 🎯 **Personalized Course Generation**
- **Timeline-aware planning**: Courses are automatically sized to fit your available time (1 week to 6+ months)
- **Dynamic objectives**: Number of learning objectives adjusts based on your timeline and daily time availability
- **Multi-level progression**: From beginner to expert, with appropriate difficulty scaling
- **Learning style adaptation**: Supports visual, auditory, kinesthetic, and reading/writing preferences

### 🤖 **Multi-Agent AI Workflow**
- **Objective Generator**: Creates specific, measurable learning objectives using GPT-4
- **Resource Hunter**: Finds high-quality educational resources using Tavily search
- **Course Builder**: Organizes objectives and resources into structured modules
- **Timeline Validator**: Ensures courses fit within your specified timeline

### 📚 **Real Educational Resources**
- **Multiple content types**: Videos, articles, courses, documentation
- **Quality filtering**: Relevance scoring and educational domain filtering
- **Timeline-appropriate quantity**: Resource count adjusts based on your timeline
- **Source diversity**: Curated from educational platforms and trusted sources

### 🎨 **Modern Web Interface**
- **Streamlit-based UI**: Clean, responsive interface
- **Progress tracking**: Visual progress indicators
- **Real-time generation**: Live updates during course creation
- **Automatic JSON export**: Download your course data immediately after generation

## 🏗️ Architecture

### **Core Components**

```
Learning_Agent/
├── main.py                 # Main Streamlit application
├── models.py              # Data models and schemas
├── requirements.txt       # Python dependencies
├── core/                  # Core workflow orchestration
│   ├── __init__.py
│   └── learning_graph.py  # LangGraph workflow definition
└── services/              # Individual AI services
    ├── __init__.py
    ├── objective_generator.py      # Learning objective generation
    ├── educational_resource_finder.py  # Resource discovery
    ├── course_builder.py           # Course structure creation
    └── resource_hunter_spawner.py  # Multi-agent coordination
```

### **Multi-Agent Workflow**

1. **User Input** → Learning preferences, timeline, goals
2. **Objective Generation** → AI creates specific learning objectives
3. **Resource Discovery** → Multiple agents find educational resources
4. **Course Building** → Objectives and resources organized into modules
5. **Timeline Validation** → Ensures course fits user's timeline
6. **Course Delivery** → Structured course with downloadable JSON

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- OpenAI API key
- Tavily API key

### **Installation**

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
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

### **API Keys Setup**

- **OpenAI API**: Get your key from [platform.openai.com](https://platform.openai.com)
- **Tavily API**: Get your key from [tavily.com](https://tavily.com) (for web search)

## 📖 Usage

### **1. Learning Preferences Form**
Fill out the form with:
- **Topic**: What you want to learn
- **Current Level**: Beginner, Intermediate, or Advanced
- **Goal Level**: Intermediate, Advanced, or Expert
- **Timeline**: 1 week to 6+ months
- **Purpose**: Career development, personal interest, etc.
- **Time Availability**: 30 minutes to 3+ hours per day
- **Learning Preferences**: Visual, auditory, kinesthetic, reading/writing
- **Content Formats**: Video, text, interactive exercises, projects, audio

### **2. Course Generation**
The system will:
- Generate appropriate number of learning objectives
- Find high-quality educational resources
- Organize content into timeline-appropriate modules
- Validate that the course fits your timeline

### **3. Course Delivery**
You'll receive:
- **Structured course modules** with learning objectives
- **Curated educational resources** with relevance scores
- **Timeline-appropriate content** sized for your schedule
- **Downloadable JSON** with complete course data

## 🎯 Timeline-Aware Features

### **Dynamic Course Sizing**
| Timeline | Objectives | Modules | Resources/Objective |
|----------|------------|---------|-------------------|
| 1 week | 2-3 | 1 | 2 |
| 2 weeks | 3-4 | 2 | 3 |
| 1 month | 6-8 | 4 | 4 |
| 2 months | 8-10 | 6 | 5 |
| 3 months | 10-12 | 8 | 6 |
| 6+ months | 12+ | 12 | 8 |

### **Smart Time Calculation**
- **Daily time availability** affects objective count
- **Timeline constraints** determine module organization
- **Resource quantity** scales with available time
- **Validation** ensures courses fit within timeline

## 🔧 Technical Details

### **Dependencies**
- **Streamlit**: Web interface framework
- **LangGraph**: Multi-agent workflow orchestration
- **LangChain**: LLM integration and structured output
- **Tavily**: Web search for educational resources
- **Pydantic**: Data validation and serialization

### **AI Models Used**
- **GPT-4o-mini**: Learning objective generation and course overview
- **Tavily Search**: Educational resource discovery
- **Custom prompts**: Timeline-aware content generation

### **Data Flow**
1. **User Input** → LearningState model
2. **LangGraph Workflow** → Orchestrates multiple services
3. **Service Execution** → Parallel resource discovery
4. **Course Assembly** → Structured course with validation
5. **JSON Export** → Downloadable course data

## 🎨 Customization

### **Adding New Learning Styles**
Modify the learning preferences form in `main.py` to include additional learning style options.

### **Extending Resource Types**
Update the resource type detection in `services/educational_resource_finder.py` to support new content formats.

### **Custom Timeline Mappings**
Adjust the timeline-to-objectives mapping in `main.py` to fine-tune course sizing for your needs.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 language model
- **Tavily** for web search capabilities
- **LangChain** for LLM orchestration framework
- **Streamlit** for the web interface framework

---

**Built with ❤️ for personalized learning** 