"""
AI-powered topic detection and analysis system
"""

from typing import List, Dict
from langchain_openai import ChatOpenAI
from models import TopicAnalysis
import json

class TopicDetector:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
        
    def analyze_topic(self, topic: str) -> TopicAnalysis:
        """Analyze a topic and return comprehensive analysis"""
        
        prompt = f"""
        Analyze the following learning topic and provide a comprehensive analysis.
        
        Topic: {topic}
        
        Please provide your analysis in the following JSON format:
        {{
            "broad_category": "technical|creative|health_wellness|language|business|academic",
            "subcategory": "specific subcategory within the broad category",
            "suggested_learning_styles": ["visual", "reading", "hands-on", "auditory"],
            "suggested_content_formats": ["videos", "articles", "interactive", "courses"],
            "suggested_engagement_level": "fun|balanced|serious",
            "safety_requirements": ["list", "of", "safety", "considerations"]
        }}
        
        Guidelines:
        - Broad categories: technical (programming, engineering), creative (art, music), health_wellness (fitness, meditation), language (spoken languages), business (marketing, finance), academic (science, history)
        - Learning styles: visual (diagrams, videos), reading (articles, books), hands-on (practice, projects), auditory (podcasts, lectures)
        - Content formats: videos, articles, interactive (apps, games), courses (structured learning)
        - Engagement: fun (entertaining, gamified), balanced (mix of serious and engaging), serious (academic, professional)
        - Safety: Only include relevant safety considerations (e.g., "consult doctor" for fitness, "backup data" for technical)
        
        Be specific and accurate in your categorization.
        """
        
        try:
            response = self.llm.invoke(prompt)
            result = json.loads(response.content.strip())
            
            return TopicAnalysis(
                broad_category=result["broad_category"],
                subcategory=result["subcategory"],
                suggested_learning_styles=result["suggested_learning_styles"],
                suggested_content_formats=result["suggested_content_formats"],
                suggested_engagement_level=result["suggested_engagement_level"],
                safety_requirements=result["safety_requirements"]
            )
            
        except Exception as e:
            # Fallback to basic analysis
            return self._fallback_analysis(topic)
    
    def _fallback_analysis(self, topic: str) -> TopicAnalysis:
        """Fallback analysis when AI detection fails"""
        topic_lower = topic.lower()
        
        # Basic keyword-based detection
        if any(word in topic_lower for word in ['python', 'javascript', 'programming', 'coding', 'web', 'app', 'software']):
            return TopicAnalysis(
                broad_category="technical",
                subcategory="programming",
                suggested_learning_styles=["visual", "hands-on"],
                suggested_content_formats=["videos", "interactive", "courses"],
                suggested_engagement_level="balanced",
                safety_requirements=["Backup your data before making changes"]
            )
        elif any(word in topic_lower for word in ['yoga', 'meditation', 'fitness', 'workout', 'health', 'nutrition']):
            return TopicAnalysis(
                broad_category="health_wellness",
                subcategory="fitness",
                suggested_learning_styles=["visual", "hands-on"],
                suggested_content_formats=["videos", "courses"],
                suggested_engagement_level="balanced",
                safety_requirements=["Consult your doctor before starting any new exercise program"]
            )
        elif any(word in topic_lower for word in ['art', 'music', 'drawing', 'painting', 'creative', 'design']):
            return TopicAnalysis(
                broad_category="creative",
                subcategory="art",
                suggested_learning_styles=["visual", "hands-on"],
                suggested_content_formats=["videos", "articles"],
                suggested_engagement_level="fun",
                safety_requirements=["Use appropriate materials and ensure proper ventilation"]
            )
        else:
            return TopicAnalysis(
                broad_category="academic",
                subcategory="general",
                suggested_learning_styles=["reading", "visual"],
                suggested_content_formats=["articles", "videos", "courses"],
                suggested_engagement_level="balanced",
                safety_requirements=[]
            ) 