# course_generator.py
from typing import Dict, List
import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
import json

from models import LearningPreferences, PersonalizedCourse, CourseModule, LearningResource
from hybrid_resource_fetcher import HybridResourceFetcher
from topic_detector import TopicDetector
from objective_based_fetcher import ObjectiveBasedFetcher

class EnhancedCourseGenerator:
    def __init__(self):
        self.resource_fetcher = HybridResourceFetcher()
        self.objective_fetcher = ObjectiveBasedFetcher()
        self.topic_detector = TopicDetector()
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
    def generate_course_with_real_resources(self, preferences: Dict) -> Dict:
        """Generate a course with real resources from APIs"""
        
        topic = preferences.get('topic', '')
        
        # Detect topic and enhance preferences
        st.info("🧠 Analyzing topic and determining optimal learning approach...")
        topic_analysis = self.topic_detector.analyze_topic(topic)
        
        # Enhance preferences with AI suggestions
        enhanced_preferences = self._enhance_preferences(preferences, topic_analysis)
        
        # Generate course structure first to get learning objectives
        st.info("🧠 Generating intelligent course structure...")
        course_structure = self.generate_intelligent_course_structure(enhanced_preferences, {})
        
        # Extract all learning objectives from modules
        all_objectives = []
        for module in course_structure.modules:
            all_objectives.extend(module.learning_objectives)
        
        # Fetch resources specifically for each learning objective
        st.info("🔍 Fetching resources for each learning objective...")
        objective_resources = self.objective_fetcher.fetch_resources_for_objectives(
            all_objectives, enhanced_preferences.get('topic_category', '')
        )
        
        # Assign resources to modules based on objectives
        course_structure = self.objective_fetcher.assign_resources_to_modules(
            course_structure, objective_resources
        )
        
        # Create a flat list of all resources for compatibility
        all_resources = {
            'videos': [],
            'articles': [],
            'courses': []
        }
        
        for module in course_structure.modules:
            for resource in module.resources:
                if resource.type == 'video':
                    all_resources['videos'].append(resource)
                elif resource.type == 'article':
                    all_resources['articles'].append(resource)
                elif resource.type == 'course':
                    all_resources['courses'].append(resource)
        
        # Create vector store for RAG (optional - for advanced queries)
        vector_store = self.create_vector_store(all_resources)
        
        # Use the course structure we already generated
        course = course_structure
        
        return {
            'course': course,
            'vector_store': vector_store,
            'all_resources': all_resources,
            'topic_analysis': topic_analysis
        }
    
    def create_vector_store(self, resources: Dict[str, List[LearningResource]]) -> FAISS:
        """Create a vector store from all fetched resources for RAG"""
        
        documents = []
        metadatas = []
        
        # Process all resource types
        for resource_type, resource_list in resources.items():
            for resource in resource_list:
                # Create document content
                content = f"""
                Title: {resource.title}
                Type: {resource.type}
                Source: {resource.source}
                Description: {resource.description}
                Difficulty: {resource.difficulty}
                Estimated Time: {resource.estimated_time}
                """
                
                # Split into chunks
                chunks = self.text_splitter.split_text(content)
                
                for chunk in chunks:
                    documents.append(chunk)
                    metadatas.append({
                        'title': resource.title,
                        'url': resource.url,
                        'type': resource.type,
                        'source': resource.source,
                        'resource_type': resource_type,
                        'relevance_score': resource.relevance_score
                    })
        
        # Create vector store
        if documents:
            vector_store = FAISS.from_texts(
                texts=documents,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            return vector_store
        else:
            return None
    
    def _enhance_preferences(self, preferences: Dict, topic_analysis) -> Dict:
        """Enhance user preferences with AI suggestions"""
        enhanced = preferences.copy()
        
        # Add topic category for quality scoring
        enhanced['topic_category'] = topic_analysis.broad_category
        
        # If user didn't specify learning styles, use AI suggestions
        if not preferences.get('learning_style'):
            enhanced['learning_style'] = topic_analysis.suggested_learning_styles
        
        # If user didn't specify content formats, use AI suggestions
        if not preferences.get('content_format'):
            enhanced['content_format'] = topic_analysis.suggested_content_formats
        
        # Add engagement level if not specified
        if not preferences.get('engagement_style'):
            enhanced['engagement_style'] = topic_analysis.suggested_engagement_level
        
        # Add safety requirements
        enhanced['safety_requirements'] = topic_analysis.safety_requirements
        
        return enhanced
    
    def generate_intelligent_course_structure(self, preferences: Dict, 
                                            resources: Dict[str, List[LearningResource]]) -> PersonalizedCourse:
        """Generate course structure using AI with real resources"""
        
        # Prepare resource summary for AI
        resource_summary = self.prepare_resource_summary(resources)
        
        course_generation_prompt = ChatPromptTemplate.from_template("""
        You are an expert curriculum designer. Create a comprehensive, personalized learning course based on the user's preferences and available resources.
        
        User Preferences:
        - Topic: {topic}
        - Current Level: {current_level}
        - Goal Level: {goal_level}
        - Timeline: {timeline}
        - Learning Style: {learning_style}
        - Content Format: {content_format}
        - Purpose: {purpose}
        - Engagement Style: {engagement_style}
        - Time Availability: {time_availability}
        - Special Requirements: {special_requirements}
        
        Available Resources Summary:
        {resource_summary}
        
        Create a structured learning course with:
        1. An engaging course title and description
        2. 3-5 progressive modules that build upon each other
        3. Each module should have:
           - Clear title and learning objectives
           - Appropriate difficulty progression
           - Mix of resource types based on user preferences
           - Realistic time estimates
        
        Guidelines:
        - Match the user's current level and goal level
        - Respect their time availability and timeline
        - Use their preferred learning styles and content formats
        - Create logical progression from basic to advanced concepts
        - Include practical application opportunities
        - Make it engaging based on their engagement style preference
        
        Return a JSON structure matching this format:
        {{
            "title": "Course title",
            "description": "Course description",
            "total_estimated_time": "X weeks",
            "difficulty_progression": "beginner to intermediate",
            "modules": [
                {{
                    "title": "Module title",
                    "description": "What this module covers",
                    "estimated_time": "X days/weeks",
                    "difficulty": "beginner/intermediate/advanced",
                    "learning_objectives": ["objective 1", "objective 2"],
                    "resource_allocation": {{
                        "videos": 2,
                        "articles": 2,
                        "courses": 1
                    }}
                }}
            ]
        }}
        """)
        
        try:
            # Generate course structure
            course_chain = course_generation_prompt | self.llm
            
            result = course_chain.invoke({
                "topic": preferences.get('topic', ''),
                "current_level": preferences.get('current_level', ''),
                "goal_level": preferences.get('goal_level', ''),
                "timeline": preferences.get('timeline', ''),
                "learning_style": ', '.join(preferences.get('learning_style', [])),
                "content_format": ', '.join(preferences.get('content_format', [])),
                "purpose": preferences.get('purpose', ''),
                "engagement_style": preferences.get('engagement_style', ''),
                "time_availability": preferences.get('time_availability', ''),
                "special_requirements": preferences.get('special_requirements', ''),
                "resource_summary": resource_summary
            })
            
            # Parse the JSON response
            json_str = result.content.strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            
            course_data = json.loads(json_str)
            
            # Create course with actual resources
            course = self.build_course_with_resources(course_data, resources, preferences)
            
            return course
            
        except Exception as e:
            st.error(f"Error generating course structure: {e}")
            # Fallback to manual course creation
            return self.create_fallback_course(preferences, resources)
    
    def prepare_resource_summary(self, resources: Dict[str, List[LearningResource]]) -> str:
        """Prepare a summary of available resources for the AI"""
        summary = []
        
        for resource_type, resource_list in resources.items():
            if resource_list:
                summary.append(f"\n{resource_type.title()} ({len(resource_list)} available):")
                for i, resource in enumerate(resource_list[:3], 1):  # Show top 3
                    summary.append(f"  {i}. {resource.title} - {resource.source} ({resource.difficulty})")
                if len(resource_list) > 3:
                    summary.append(f"  ... and {len(resource_list) - 3} more")
        
        return "\n".join(summary)
    
    def build_course_with_resources(self, course_data: Dict, 
                                   resources: Dict[str, List[LearningResource]], 
                                   preferences: Dict) -> PersonalizedCourse:
        """Build the final course with actual resources assigned to modules"""
        
        modules = []
        resource_index = {
            'videos': 0,
            'articles': 0,
            'courses': 0
        }
        
        for module_data in course_data.get('modules', []):
            # Get resource allocation for this module
            allocation = module_data.get('resource_allocation', {})
            
            # Assign actual resources to this module
            module_resources = []
            
            for resource_type, count in allocation.items():
                available_resources = resources.get(resource_type, [])
                start_idx = resource_index[resource_type]
                end_idx = min(start_idx + count, len(available_resources))
                
                # Add resources to module
                for i in range(start_idx, end_idx):
                    module_resources.append(available_resources[i])
                
                # Update index for next module
                resource_index[resource_type] = end_idx
            
            # Create module
            module = CourseModule(
                title=module_data['title'],
                description=module_data['description'],
                estimated_time=module_data['estimated_time'],
                difficulty=module_data['difficulty'],
                resources=module_resources,
                learning_objectives=module_data.get('learning_objectives', [])
            )
            modules.append(module)
        
        # Calculate total resources
        total_resources = sum(len(module.resources) for module in modules)
        
        # Create final course
        course = PersonalizedCourse(
            title=course_data['title'],
            description=course_data['description'],
            total_estimated_time=course_data['total_estimated_time'],
            modules=modules,
            total_resources=total_resources,
            difficulty_progression=course_data.get('difficulty_progression', 'Progressive')
        )
        
        return course
    
    def create_fallback_course(self, preferences: Dict, 
                              resources: Dict[str, List[LearningResource]]) -> PersonalizedCourse:
        """Create a fallback course if AI generation fails"""
        
        topic = preferences.get('topic', 'Your Topic')
        current_level = preferences.get('current_level', 'beginner')
        goal_level = preferences.get('goal_level', 'intermediate')
        
        # Create basic modules
        modules = []
        
        # Module 1: Foundations
        foundation_resources = []
        foundation_resources.extend(resources.get('documentation', [])[:2])  # Official docs first
        foundation_resources.extend([r for r in resources.get('videos', []) 
                                   if 'intro' in r.title.lower() or 'beginner' in r.title.lower()][:2])
        foundation_resources.extend([r for r in resources.get('articles', []) 
                                   if 'basic' in r.title.lower() or 'intro' in r.title.lower()][:2])
        
        modules.append(CourseModule(
            title=f'Foundations of {topic}',
            description=f'Build a solid understanding of {topic} fundamentals using official documentation and beginner resources',
            estimated_time='1 week',
            difficulty='Beginner',
            resources=foundation_resources[:5],
            learning_objectives=[
                f'Understand basic concepts of {topic}',
                f'Learn {topic} terminology and principles',
                f'Get familiar with {topic} applications'
            ]
        ))
        
        # Module 2: Practical Application
        practical_resources = []
        practical_resources.extend([r for r in resources.get('videos', []) 
                                  if 'practical' in r.title.lower() or 'tutorial' in r.title.lower()][:2])
        practical_resources.extend([r for r in resources.get('articles', []) 
                                  if 'guide' in r.title.lower() or 'how to' in r.title.lower()][:2])
        practical_resources.extend(resources.get('courses', [])[:1])
        
        modules.append(CourseModule(
            title=f'Practical {topic} Skills',
            description=f'Apply {topic} concepts through hands-on practice and real-world tutorials',
            estimated_time='2 weeks',
            difficulty='Intermediate',
            resources=practical_resources[:5],
            learning_objectives=[
                f'Apply {topic} concepts in practice',
                f'Complete hands-on {topic} projects',
                f'Develop practical {topic} skills'
            ]
        ))
        
        # Module 3: Advanced Topics (if goal is advanced/expert)
        if goal_level in ['advanced', 'expert']:
            advanced_resources = []
            advanced_resources.extend([r for r in resources.get('videos', []) 
                                     if 'advanced' in r.title.lower()][:2])
            advanced_resources.extend([r for r in resources.get('articles', []) 
                                     if 'advanced' in r.title.lower()][:2])
            advanced_resources.extend(resources.get('courses', [])[-1:])
            
            modules.append(CourseModule(
                title=f'Advanced {topic} Techniques',
                description=f'Master advanced {topic} concepts and techniques for professional use',
                estimated_time='2-3 weeks',
                difficulty='Advanced',
                resources=advanced_resources[:5],
                learning_objectives=[
                    f'Master advanced {topic} techniques',
                    f'Understand {topic} best practices',
                    f'Prepare for expert-level {topic} work'
                ]
            ))
        
        # Calculate totals
        total_resources = sum(len(module.resources) for module in modules)
        total_weeks = len(modules)
        
        return PersonalizedCourse(
            title=f'Complete {topic} Learning Path',
            description=f'A comprehensive course to take you from {current_level} to {goal_level} in {topic} using high-quality educational resources',
            total_estimated_time=f'{total_weeks} weeks',
            modules=modules,
            total_resources=total_resources,
            difficulty_progression=f'{current_level.title()} to {goal_level.title()}'
        )