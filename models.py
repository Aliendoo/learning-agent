# models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class LearningPreferences(BaseModel):
    topic: str = Field(default="", description="Main learning topic")
    timeline: str = Field(default="", description="Desired timeline for completion")
    current_level: str = Field(default="", description="Current knowledge level")
    goal_level: str = Field(default="", description="Target knowledge level")
    learning_style: List[str] = Field(default=[], description="Visual, auditory, kinesthetic, reading/writing")
    content_format: List[str] = Field(default=[], description="Video, text, interactive, practice")
    purpose: str = Field(default="", description="Career, hobby, academic, etc.")
    engagement_style: str = Field(default="", description="Fun/engaging vs structured")
    time_availability: str = Field(default="", description="Hours per day/week available")
    special_requirements: str = Field(default="", description="Any special requirements or constraints")
    
    def is_complete(self) -> bool:
        """Check if we have enough core information"""
        required_fields = [self.topic, self.current_level, self.goal_level, self.timeline, self.purpose]
        return all(field.strip() for field in required_fields)
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing important fields"""
        missing = []
        if not self.topic.strip():
            missing.append("topic")
        if not self.current_level.strip():
            missing.append("current_level")
        if not self.goal_level.strip():
            missing.append("goal_level")
        if not self.timeline.strip():
            missing.append("timeline")
        if not self.purpose.strip():
            missing.append("purpose")
        if not self.learning_style:
            missing.append("learning_style")
        if not self.engagement_style.strip():
            missing.append("engagement_style")
        if not self.time_availability.strip():
            missing.append("time_availability")
        return missing

class LearningResource(BaseModel):
    type: str = Field(description="video, article, course, etc.")
    title: str = Field(description="Resource title")
    url: str = Field(description="Resource URL")
    description: str = Field(default="", description="Resource description")
    source: str = Field(default="", description="Source platform")
    estimated_time: str = Field(default="", description="Time to complete")
    difficulty: str = Field(default="", description="Difficulty level")
    relevance_score: float = Field(default=0.0, description="Relevance to user preferences")
    quality_score: float = Field(default=0.0, description="Overall quality score")
    credibility_score: float = Field(default=0.0, description="Source credibility score")
    engagement_score: float = Field(default=0.0, description="Engagement metrics score")
    depth_score: float = Field(default=0.0, description="Content depth score")
    recency_score: float = Field(default=0.0, description="Content recency score")
    topic_category: str = Field(default="", description="Detected topic category")
    safety_warnings: List[str] = Field(default_factory=list, description="Safety warnings")
    source_credibility: str = Field(default="", description="Credibility level")
    objective_match: str = Field(default="", description="Learning objective this resource matches")

class CourseModule(BaseModel):
    title: str = Field(description="Module title")
    description: str = Field(description="Module description")
    estimated_time: str = Field(description="Time to complete module")
    difficulty: str = Field(description="Module difficulty")
    resources: List[LearningResource] = Field(description="Module resources")
    learning_objectives: List[str] = Field(description="What student will learn")

class PersonalizedCourse(BaseModel):
    title: str = Field(description="Course title")
    description: str = Field(description="Course description")
    total_estimated_time: str = Field(description="Total course duration")
    modules: List[CourseModule] = Field(description="Course modules")
    total_resources: int = Field(description="Total number of resources")
    difficulty_progression: str = Field(description="How difficulty progresses")

class TopicAnalysis(BaseModel):
    """Result of AI topic detection and analysis"""
    broad_category: str = Field(description="Broad topic category")
    subcategory: str = Field(description="Specific subcategory")
    suggested_learning_styles: List[str] = Field(description="Suggested learning styles")
    suggested_content_formats: List[str] = Field(description="Suggested content formats")
    suggested_engagement_level: str = Field(description="Suggested engagement level")
    safety_requirements: List[str] = Field(default_factory=list, description="Safety requirements")