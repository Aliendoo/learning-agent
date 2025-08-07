# main.py - Complete Learning Platform Application
import streamlit as st
import os
from dotenv import load_dotenv
from typing import Dict

# Load environment variables
load_dotenv()

# Import our modules
from models import LearningPreferences
from chatbot import ConversationalLearningChatbot
from course_generator import EnhancedCourseGenerator

def main():
    st.set_page_config(
        page_title="🎓 AI Learning Platform",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check API keys
    api_status = check_api_setup()
    
    st.title("🎓 AI-Powered Personalized Learning Platform")
    st.markdown("*Create a customized learning plan with real educational resources*")
    
    # Show API status
    if not api_status['openai']:
        st.error("⚠️ OpenAI API key is required to use this application")
        display_api_setup_instructions()
        return
    
    # Show API status in sidebar
    with st.sidebar:
        st.subheader("🔧 API Status")
        st.success("✅ OpenAI API" if api_status['openai'] else "❌ OpenAI API")
        st.success("✅ YouTube API" if api_status['youtube'] else "⚠️ YouTube API (Limited)")
        st.success("✅ Google Search API" if api_status['google_search'] else "❌ Google Search API")
        
        if not api_status['youtube']:
            st.info("💡 Add YouTube API key in .env for video resources")
        if not api_status['google_search']:
            st.info("💡 Add GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID in .env for article/course resources")
            st.success("✅ Web scraping fallback available for educational resources")
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 'form'
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'course_generated' not in st.session_state:
        st.session_state.course_generated = False
    
    # Progress indicator
    render_progress_indicator()
    
    st.markdown("---")
    
    # Navigation
    if st.session_state.step == 'form':
        render_initial_form()
    elif st.session_state.step == 'chat':
        render_chatbot()
    elif st.session_state.step == 'course':
        render_course_generation()

def check_api_setup() -> Dict[str, bool]:
    """Check which APIs are properly configured"""
    return {
        'openai': bool(os.getenv('OPENAI_API_KEY')),
        'youtube': bool(os.getenv('YOUTUBE_API_KEY')),
        'google_search': bool(os.getenv('GOOGLE_SEARCH_API_KEY') and os.getenv('GOOGLE_SEARCH_ENGINE_ID')),
        'udemy': bool(os.getenv('UDEMY_CLIENT_ID') and os.getenv('UDEMY_CLIENT_SECRET'))
    }

def render_progress_indicator():
    """Render progress indicator"""
    progress_steps = ['Form', 'Chat', 'Course']
    current_step_index = progress_steps.index(st.session_state.step.title())
    
    st.markdown("### 📊 Progress")
    cols = st.columns(len(progress_steps))
    for i, step in enumerate(progress_steps):
        with cols[i]:
            if i < current_step_index:
                st.success(f"✅ Step {i+1}: {step}")
            elif i == current_step_index:
                st.info(f"📍 Step {i+1}: {step}")
            else:
                st.text(f"⏳ Step {i+1}: {step}")

def render_initial_form():
    """Render the initial preference collection form"""
    st.header("📝 Step 1: Tell Us About Your Learning Goals")
    st.markdown("Let's start with some basic information about what you want to learn:")
    
    with st.form("initial_form"):
        # Create two columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input(
                "🎯 What do you want to learn?",
                placeholder="e.g., Python programming, Digital marketing, Photography",
                help="Be as specific as possible"
            )
            
            current_level = st.selectbox(
                "📊 Your current level:",
                ["", "Beginner", "Intermediate", "Advanced"],
                help="How would you rate your current knowledge?"
            )
            
            timeline = st.selectbox(
                "⏰ How long do you have?",
                ["", "1 week", "2 weeks", "1 month", "2 months", "3 months", "6+ months"],
                help="Your ideal timeline to reach your goal"
            )
        
        with col2:
            goal_level = st.selectbox(
                "🎯 Goal level:",
                ["", "Intermediate", "Advanced", "Expert"],
                help="What level do you want to reach?"
            )
            
            purpose = st.selectbox(
                "🎪 Purpose of learning:",
                ["", "Career development", "Personal interest", "Academic requirement", "Side project", "Other"],
                help="Why do you want to learn this?"
            )
            
            time_availability = st.selectbox(
                "⏱️ Time available per day:",
                ["", "30 minutes", "1 hour", "2 hours", "3+ hours"],
                help="How much time can you dedicate daily?"
            )
        
        # Learning preferences
        st.subheader("Learning Preferences (Optional)")
        
        col3, col4 = st.columns(2)
        
        with col3:
            learning_style = st.multiselect(
                "🧠 How you learn best:",
                ["Visual", "Auditory", "Kinesthetic (hands-on)", "Reading/Writing"],
                help="Select all that apply"
            )
        
        with col4:
            content_format = st.multiselect(
                "📚 Preferred content types:",
                ["Video", "Text/Articles", "Interactive exercises", "Practice projects", "Audio"],
                help="What formats do you prefer?"
            )
        
        submitted = st.form_submit_button("Continue to Chat Planning 💬", use_container_width=True)
        
        if submitted:
            # Validate required fields
            required_fields = {
                "Topic": topic,
                "Current Level": current_level,
                "Goal Level": goal_level,
                "Timeline": timeline,
                "Purpose": purpose,
                "Time Availability": time_availability
            }
            
            missing_fields = [name for name, value in required_fields.items() if not value]
            
            if missing_fields:
                st.error(f"Please fill in these required fields: {', '.join(missing_fields)}")
            else:
                # Store form data and initialize chatbot
                form_data = {
                    "topic": topic,
                    "current_level": current_level.lower(),
                    "goal_level": goal_level.lower(),
                    "timeline": timeline,
                    "purpose": purpose.lower(),
                    "time_availability": time_availability,
                    "learning_style": [style.lower().replace(" (hands-on)", "").replace("/writing", "") for style in learning_style],
                    "content_format": [fmt.lower().replace("/articles", "").replace(" exercises", "").replace(" projects", "") for fmt in content_format],
                    "engagement_style": "",  # Will be filled in chat
                }
                
                st.session_state.chatbot = ConversationalLearningChatbot(form_data)
                st.session_state.step = 'chat'
                
                # Create natural opening message
                opening_message = f"""Great! I can see you want to learn {topic}. That's exciting! 

Let me ask you a few more questions to make sure I create the perfect learning plan for you. 

To start with - would you prefer a more structured, step-by-step approach, or would you like something more fun and engaging with interactive elements? And feel free to let me know if you have any specific requirements or if there's anything from the form you'd like to adjust!"""
                
                st.session_state.chat_messages = [{
                    "role": "assistant",
                    "content": opening_message
                }]
                st.rerun()

def render_chatbot():
    """Render the chatbot interface"""
    st.header("💬 Step 2: Let's Refine Your Learning Plan")
    st.markdown("Now let's have a conversation to perfect your learning plan. Feel free to ask questions, make requests, or change anything!")
    
    # Show current preferences in sidebar
    with st.sidebar:
        st.subheader("📋 Current Preferences")
        if st.session_state.chatbot:
            prefs = st.session_state.chatbot.preferences.dict()
            for key, value in prefs.items():
                if value:  # Only show filled fields
                    formatted_key = key.replace('_', ' ').title()
                    if isinstance(value, list):
                        value_str = ', '.join([str(v).title() for v in value])
                    else:
                        value_str = str(value).title()
                    st.text(f"{formatted_key}: {value_str}")
        
        # Show progress
        if st.session_state.chatbot:
            missing = st.session_state.chatbot.preferences.get_missing_fields()
            complete_fields = 10 - len(missing)  # Total fields minus missing
            progress = complete_fields / 10
            st.progress(progress)
            st.caption(f"Progress: {complete_fields}/10 fields complete")
            
            if not missing:
                st.success("✅ All information collected!")
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your response here... (e.g., 'I prefer visual learning' or 'Can we change the timeline?')"):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Get bot response
        if st.session_state.chatbot:
            response = st.session_state.chatbot.chat_turn(prompt)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            
            # Check if conversation is complete
            if st.session_state.chatbot.conversation_complete:
                st.balloons()
        
        st.rerun()
    
    # Generate course button (only show when ready)
    if st.session_state.chatbot and (st.session_state.chatbot.preferences.is_complete() or st.session_state.chatbot.user_ready_to_generate):
        st.markdown("---")
        if st.button("🚀 Generate My Learning Course", use_container_width=True, type="primary"):
            st.session_state.step = 'course'
            st.rerun()
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Form", use_container_width=True):
            st.session_state.step = 'form'
            st.session_state.chatbot = None
            st.session_state.chat_messages = []
            st.rerun()

def render_course_generation():
    """Render the course generation with real resources"""
    st.header("📚 Step 3: Your Personalized Course")
    
    if not st.session_state.chatbot:
        st.error("No chatbot session found. Please start over.")
        if st.button("🔄 Start Over"):
            st.session_state.step = 'form'
            st.rerun()
        return
    
    prefs = st.session_state.chatbot.preferences.dict()
    
    # Show user preferences summary
    with st.expander("📋 Your Learning Profile", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **Topic:** {prefs['topic']}
            **Current Level:** {prefs['current_level'].title()}
            **Goal Level:** {prefs['goal_level'].title()}
            **Timeline:** {prefs['timeline']}
            """)
        with col2:
            st.markdown(f"""
            **Purpose:** {prefs['purpose'].title()}
            **Time Available:** {prefs['time_availability']}
            **Learning Style:** {', '.join([s.title() for s in prefs['learning_style']])}
            **Engagement:** {prefs['engagement_style'].title()}
            """)
        
        if prefs.get('special_requirements'):
            st.markdown(f"**Special Requirements:** {prefs['special_requirements']}")
    
    # Generate course automatically
    if not st.session_state.course_generated:
        st.info("🔍 Searching real educational platforms (YouTube, educational websites) for the best resources!")
        
        with st.spinner("🔍 Searching educational platforms for the best resources..."):
            try:
                course_generator = EnhancedCourseGenerator()
                result = course_generator.generate_course_with_real_resources(prefs)
                
                st.session_state.course_generated = True
                st.session_state.generated_course = result['course']
                st.session_state.all_resources = result['all_resources']
                st.session_state.topic_analysis = result.get('topic_analysis', None)
                
                st.success("🎉 Course generated successfully with real resources!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating course: {e}")
                st.info("Please try again or check your internet connection.")
    
    # Display generated course
    if st.session_state.course_generated:
        course = st.session_state.generated_course
        all_resources = st.session_state.all_resources
        topic_analysis = st.session_state.get('topic_analysis', None)
        
        # Course overview
        st.subheader("🎓 Course Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Duration", course.total_estimated_time)
        with col2:
            st.metric("Total Resources", course.total_resources)
        with col3:
            st.metric("Modules", len(course.modules))
        
        st.info(f"**{course.title}**\n\n{course.description}")
        
        # Display topic analysis if available
        if topic_analysis:
            st.subheader("🧠 AI Analysis")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**Category:** {topic_analysis.broad_category.title()}")
                st.markdown(f"**Subcategory:** {topic_analysis.subcategory.title()}")
            
            with col2:
                st.markdown(f"**Learning Styles:** {', '.join(topic_analysis.suggested_learning_styles)}")
                st.markdown(f"**Content Formats:** {', '.join(topic_analysis.suggested_content_formats)}")
            
            with col3:
                st.markdown(f"**Engagement:** {topic_analysis.suggested_engagement_level.title()}")
                if topic_analysis.safety_requirements:
                    st.markdown("**Safety:** ⚠️ See warnings below")
        
        # Display modules with real resources
        st.subheader("📖 Learning Modules")
        
        for i, module in enumerate(course.modules, 1):
            with st.expander(f"Module {i}: {module.title}", expanded=i==1):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {module.description}")
                    st.markdown("**Learning Objectives:**")
                    for obj in module.learning_objectives:
                        st.markdown(f"• {obj}")
                
                with col2:
                    st.markdown(f"**Time:** {module.estimated_time}")
                    st.markdown(f"**Level:** {module.difficulty}")
                    st.markdown(f"**Resources:** {len(module.resources)}")
                
                # Real resources
                if module.resources:
                    st.markdown("**📚 Resources:**")
                    for resource in module.resources:
                        icon = {"video": "📺", "article": "📄", "course": "🎓"}.get(resource.type, "📚")
                        
                        # Create clickable link
                        st.markdown(f"{icon} **[{resource.title}]({resource.url})**")
                        
                        # Display objective match if available
                        if hasattr(resource, 'objective_match') and resource.objective_match:
                            st.markdown(f"🎯 **Matches:** {resource.objective_match}")
                        
                        # Display quality and source information
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"   └ *Source: {resource.source}* | *Time: {resource.estimated_time}*")
                            if resource.description:
                                st.markdown(f"   └ {resource.description[:150]}...")
                        
                        with col2:
                            # Quality score indicator
                            if hasattr(resource, 'quality_score') and resource.quality_score > 0:
                                quality_color = "🟢" if resource.quality_score >= 7.5 else "🟡" if resource.quality_score >= 6.0 else "🔴"
                                st.markdown(f"{quality_color} **{resource.quality_score}/10**")
                        
                        # Display safety warnings
                        if hasattr(resource, 'safety_warnings') and resource.safety_warnings:
                            for warning in resource.safety_warnings:
                                st.warning(f"⚠️ {warning}")
                        
                        st.markdown("")
                else:
                    st.info("No specific resources found for this module.")
        
        # Resource summary
        st.subheader("📊 Resource Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎥 Videos", len(all_resources.get('videos', [])))
        with col2:
            st.metric("📄 Articles", len(all_resources.get('articles', [])))
        with col3:
            st.metric("🎓 Courses", len(all_resources.get('courses', [])))
        with col4:
            st.metric("📚 Documentation", len(all_resources.get('documentation', [])))
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📅 Schedule Learning", use_container_width=True):
                st.info("Calendar integration coming in Phase 3!")
        
        with col2:
            if st.button("💾 Export Course", use_container_width=True):
                # Create downloadable course data
                course_json = {
                    "course": course.dict(),
                    "preferences": prefs,
                    "generated_at": str(st.session_state.get('generation_time', 'Unknown'))
                }
                st.download_button(
                    label="📄 Download as JSON",
                    data=str(course_json),
                    file_name=f"{prefs['topic'].replace(' ', '_')}_course.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("🔄 Start Over", use_container_width=True):
                # Reset everything
                for key in ['step', 'chatbot', 'chat_messages', 'course_generated', 'generated_course', 'all_resources']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

def display_api_setup_instructions():
    """Display instructions for setting up APIs"""
    st.sidebar.markdown("## 🔧 API Setup Required")
    
    with st.sidebar.expander("📋 Setup Instructions"):
        st.markdown("""
        **Add to your .env file:**
        
        ```bash
        # Required
        OPENAI_API_KEY=your_openai_key
        
        # Google Search API (Recommended)
        GOOGLE_SEARCH_API_KEY=your_google_search_key
        GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
        
        # YouTube Data API (Optional)
        YOUTUBE_API_KEY=your_youtube_key
        
        # Udemy API (Optional)
        UDEMY_CLIENT_ID=your_udemy_id
        UDEMY_CLIENT_SECRET=your_udemy_secret
        ```
        
        **Get API Keys:**
        1. **OpenAI**: platform.openai.com
        2. **Google Search**: Google Cloud Console → Custom Search API
        3. **YouTube**: Google Cloud Console
        4. **Udemy**: Udemy Affiliate Program
        
        **Note**: If Google Search API is not configured, the system will automatically use web scraping fallback to find educational resources from trusted sites like Medium, Dev.to, and FreeCodeCamp.
        """)

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        st.error("🚨 Please set your OPENAI_API_KEY in the .env file")
        st.stop()
    
    main()