# main.py - Updated for multi-agent learning workflow
import streamlit as st
import os
from dotenv import load_dotenv
from datetime import date
from typing import Dict

# Load environment variables
load_dotenv()

# Import our new workflow components
from models import LearningPreferences, LearningState
from core.learning_graph import build_learning_graph

def calculate_objectives_from_timeline(timeline: str, time_availability: str) -> int:
    """
    Calculate appropriate number of objectives based on timeline and daily time availability
    """
    timeline_weeks = {
        "1 week": 1,
        "2 weeks": 2, 
        "1 month": 4,
        "2 months": 8,
        "3 months": 12,
        "6+ months": 24
    }
    
    daily_hours = {
        "30 minutes": 0.5,
        "1 hour": 1,
        "2 hours": 2,
        "3+ hours": 3
    }
    
    weeks = timeline_weeks.get(timeline, 4)
    hours_per_day = daily_hours.get(time_availability, 1)
    total_hours = weeks * 7 * hours_per_day
    
    # Estimate objectives based on available time
    # Assume 2-3 hours per objective on average
    objectives = max(2, min(12, int(total_hours / 2.5)))
    
    return objectives

def validate_course_timeline(course, user_timeline: str) -> bool:
    """Validate that the generated course fits within the user's timeline"""
    timeline_weeks = {
        "1 week": 1, "2 weeks": 2, "1 month": 4,
        "2 months": 8, "3 months": 12, "6+ months": 24
    }
    
    target_weeks = timeline_weeks.get(user_timeline, 4)
    estimated_weeks = len(course.modules)  # Simple estimation
    
    return estimated_weeks <= target_weeks

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
    st.markdown("*Create a customized learning plan with real educational resources using multi-agent AI*")
    
    # Check API keys
    if not api_status['openai'] or not api_status['tavily']:
        st.error("⚠️ Required API keys are missing. Please check your .env file.")
        display_api_setup_instructions()
        return
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 'form'
    if 'course_generated' not in st.session_state:
        st.session_state.course_generated = False
    if 'generated_course' not in st.session_state:
        st.session_state.generated_course = None
    
    # Progress indicator
    render_progress_indicator()
    
    st.markdown("---")
    
    # Navigation
    if st.session_state.step == 'form':
        render_learning_form()
    elif st.session_state.step == 'generation':
        render_course_generation()

def check_api_setup() -> Dict[str, bool]:
    """Check which APIs are properly configured"""
    return {
        'openai': bool(os.getenv('OPENAI_API_KEY')),
        'tavily': bool(os.getenv('TAVILY_API_KEY'))
    }

def render_progress_indicator():
    """Render progress indicator"""
    progress_steps = ['Form', 'Generation']
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

def render_learning_form():
    """Render the learning preferences form"""
    st.header("📝 What do you want to learn?")
    st.markdown("Tell us about your learning goals and we'll create a personalized course with real educational resources:")
    
    with st.form("learning_form"):
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
        
        engagement_style = st.selectbox(
            "🎮 Learning style preference:",
            ["", "Fun and engaging", "Structured and systematic", "Mixed approach"],
            help="How do you prefer to learn?"
        )
        
        special_requirements = st.text_area(
            "📝 Any special requirements?",
            placeholder="e.g., Focus on practical projects, certification preparation, specific tools...",
            help="Optional: Any specific needs or constraints"
        )
        
        submitted = st.form_submit_button("🚀 Generate My Learning Course", use_container_width=True, type="primary")
        
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
                # Store preferences and move to generation
                preferences = {
                    "topic": topic,
                    "current_level": current_level.lower(),
                    "goal_level": goal_level.lower(),
                    "timeline": timeline,
                    "purpose": purpose.lower(),
                    "time_availability": time_availability,
                    "learning_style": [style.lower().replace(" (hands-on)", "").replace("/writing", "") for style in learning_style],
                    "content_format": [fmt.lower().replace("/articles", "").replace(" exercises", "").replace(" projects", "") for fmt in content_format],
                    "engagement_style": engagement_style.lower() if engagement_style else "mixed",
                    "special_requirements": special_requirements
                }
                
                st.session_state.learning_preferences = preferences
                st.session_state.step = 'generation'
                st.rerun()

def render_course_generation():
    """Render the course generation with multi-agent workflow"""
    st.header("🤖 Generating Your Personalized Course")
    
    prefs = st.session_state.learning_preferences
    
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
    
    # Generate course automatically using multi-agent workflow
    if not st.session_state.course_generated:
        st.info("🤖 Starting multi-agent course generation workflow...")
        
        # Create status containers for real-time updates
        status_container = st.container()
        progress_bar = st.progress(0)
        
        with st.spinner("🔍 AI agents are working on your course..."):
            try:
                # Build the learning workflow graph
                graph = build_learning_graph()
                
                # Prepare state for the workflow
                current_date = date.today().strftime("%Y-%m-%d")
                
                # Calculate number of objectives based on timeline and time availability
                num_objectives = calculate_objectives_from_timeline(prefs['timeline'], prefs['time_availability'])
                
                learning_state = LearningState(
                    user_topic=prefs['topic'],
                    user_preferences=prefs,
                    current_date=current_date,
                    num_objectives=num_objectives
                )
                
                # Update progress
                with status_container:
                    st.info("🎯 Generating learning objectives...")
                progress_bar.progress(0.2)
                
                # Execute the multi-agent workflow
                result = graph.invoke(learning_state.dict())
                
                # Update progress
                with status_container:
                    st.info("🔍 Finding educational resources...")
                progress_bar.progress(0.6)
                
                # Update progress
                with status_container:
                    st.info("📚 Building your personalized course...")
                progress_bar.progress(0.9)
                
                # Store results
                st.session_state.generated_course = result['final_course']
                st.session_state.learning_objectives = result['learning_objectives']
                st.session_state.objective_results = result['objective_results']
                st.session_state.course_generated = True
                
                # Create downloadable course data for automatic download
                import json
                course_data = {
                    "course": result['final_course'].dict(),
                    "objectives": result['learning_objectives'],
                    "preferences": prefs,
                    "generated_at": date.today().strftime("%Y-%m-%d")
                }
                st.session_state.course_json = json.dumps(course_data, indent=2)
                st.session_state.course_filename = f"{prefs['topic'].replace(' ', '_')}_course.json"
                
                # Validate timeline fit
                if not validate_course_timeline(result['final_course'], prefs['timeline']):
                    st.warning(f"⚠️ Note: The generated course has {len(result['final_course'].modules)} modules, which may exceed your {prefs['timeline']} timeline. Consider adjusting your timeline or time availability.")
                
                progress_bar.progress(1.0)
                with status_container:
                    st.success("🎉 Course generated successfully!")
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating course: {e}")
                st.info("Please try again or check your API keys.")
                
                # Add debug info
                st.expander("Debug Information").write({
                    "Error": str(e),
                    "Preferences": prefs
                })
    
    # Display generated course
    if st.session_state.course_generated and st.session_state.generated_course:
        course = st.session_state.generated_course
        objectives = st.session_state.learning_objectives
        
        # Course overview
        st.subheader("🎓 Your Personalized Course")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Duration", course.total_estimated_time)
        with col2:
            st.metric("Total Resources", course.total_resources)
        with col3:
            st.metric("Modules", len(course.modules))
        
        st.info(f"**{course.title}**\n\n{course.description}")
        
        # Display learning objectives
        st.subheader("🎯 Learning Objectives")
        for i, objective in enumerate(objectives, 1):
            st.markdown(f"{i}. {objective}")
        
        # Display course modules with resources
        st.subheader("📖 Course Modules")
        
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
                
                # Display resources
                if module.resources:
                    st.markdown("**📚 Educational Resources:**")
                    for resource in module.resources:
                        icon = {"video": "📺", "article": "📄", "course": "🎓", "documentation": "📚"}.get(resource.type, "📚")
                        
                        # Create clickable link
                        st.markdown(f"{icon} **[{resource.title}]({resource.url})**")
                        
                        # Display objective match
                        if resource.objective_match:
                            st.markdown(f"🎯 **Covers:** {resource.objective_match}")
                        
                        # Display resource details
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"   └ *Source: {resource.source}* | *Time: {resource.estimated_time}*")
                            if resource.description:
                                st.markdown(f"   └ {resource.description[:100]}...")
                        
                        with col2:
                            if resource.relevance_score > 0:
                                score_color = "🟢" if resource.relevance_score >= 6 else "🟡" if resource.relevance_score >= 3 else "🔴"
                                st.markdown(f"{score_color} **Score: {resource.relevance_score:.1f}**")
                        
                        st.markdown("")
                else:
                    st.info("No resources found for this module.")
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📅 Schedule Learning", use_container_width=True):
                st.info("Feature coming soon!")
        
        with col2:
            # Automatic download button - replaces the manual export
            if hasattr(st.session_state, 'course_json') and st.session_state.course_json:
                st.download_button(
                    label="📄 Download Course JSON",
                    data=st.session_state.course_json,
                    file_name=st.session_state.course_filename,
                    mime="application/json",
                    use_container_width=True
                )
                # Clear the JSON data after download to prevent re-download
                del st.session_state.course_json
                del st.session_state.course_filename
            else:
                # Fallback if JSON data is not available
                import json
                course_data = {
                    "course": course.dict(),
                    "objectives": objectives,
                    "preferences": prefs,
                    "generated_at": date.today().strftime("%Y-%m-%d")
                }
                st.download_button(
                    label="📄 Download Course JSON",
                    data=json.dumps(course_data, indent=2),
                    file_name=f"{prefs['topic'].replace(' ', '_')}_course.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        with col3:
            if st.button("🔄 Start Over", use_container_width=True):
                # Reset everything
                for key in ['step', 'course_generated', 'generated_course', 'learning_preferences']:
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
        TAVILY_API_KEY=your_tavily_key
        ```
        
        **Get API Keys:**
        1. **OpenAI**: platform.openai.com
        2. **Tavily**: tavily.com (for web search)
        
        **Note**: Both APIs are required for the multi-agent workflow to function properly.
        """)

if __name__ == "__main__":
    # Check if required API keys are set
    if not os.getenv('OPENAI_API_KEY'):
        st.error("🚨 Please set your OPENAI_API_KEY in the .env file")
        st.stop()
    
    if not os.getenv('TAVILY_API_KEY'):
        st.error("🚨 Please set your TAVILY_API_KEY in the .env file")
        st.stop()
    
    main()