# chatbot.py
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from typing import Optional, Dict
import json
import streamlit as st
from models import LearningPreferences

class ConversationalLearningChatbot:
    def __init__(self, initial_preferences: Optional[Dict] = None):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.memory = ConversationBufferWindowMemory(
            k=10,
            return_messages=True
        )
        
        # Initialize preferences from form data or empty
        if initial_preferences:
            self.preferences = LearningPreferences(**initial_preferences)
        else:
            self.preferences = LearningPreferences()
        
        # Track conversation state
        self.conversation_complete = False
        self.user_ready_to_generate = False
        
    def extract_preferences_from_input(self, user_input: str) -> LearningPreferences:
        """Use LLM to extract and update preferences from user input"""
        
        extraction_prompt = ChatPromptTemplate.from_template("""
        You are an expert at extracting learning preferences from user responses.
        
        Current preferences (in JSON format):
        {current_preferences}
        
        User's latest response:
        "{user_input}"
        
        Based on the user's response, extract any NEW information and update the preferences.
        Pay special attention to:
        - Changes to existing preferences (user wants to modify something)
        - New requirements or constraints
        - Learning style preferences
        - Timeline adjustments
        - Special requests
        
        For learning_style, possible values are: ["visual", "auditory", "kinesthetic", "reading"]
        For content_format, possible values are: ["video", "text", "interactive", "practice", "audio"]
        For engagement_style, possible values are: "structured", "fun", "mixed"
        
        Return the UPDATED preferences in valid JSON format matching this schema:
        {{
            "topic": "string",
            "timeline": "string", 
            "current_level": "string",
            "goal_level": "string",
            "learning_style": ["list", "of", "strings"],
            "content_format": ["list", "of", "strings"],
            "purpose": "string",
            "engagement_style": "string",
            "time_availability": "string",
            "special_requirements": "string"
        }}
        
        Important: 
        - Keep existing values unless the user explicitly provides new information
        - If user wants to change something, update that field
        - Capture any special requirements or constraints mentioned
        """)
        
        try:
            extraction_chain = extraction_prompt | self.llm
            
            result = extraction_chain.invoke({
                "current_preferences": json.dumps(self.preferences.dict(), indent=2),
                "user_input": user_input
            })
            
            # Clean the JSON response
            json_str = result.content.strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            
            updated_data = json.loads(json_str)
            updated_preferences = LearningPreferences(**updated_data)
            
            return updated_preferences
            
        except Exception as e:
            st.warning(f"Error extracting preferences: {e}")
            return self.preferences
    
    def chat_turn(self, user_input: str) -> str:
        """Process one turn of conversation"""
        # Add user message to memory
        self.memory.chat_memory.add_user_message(user_input)
        
        # Check if user wants to generate the course
        generate_keywords = ["generate", "create", "build", "make"]
        course_keywords = ["course", "plan", "curriculum", "program"]
        ready_keywords = ["ready", "done", "finished", "complete"]
        
        user_input_lower = user_input.lower()
        
        if (any(word in user_input_lower for word in generate_keywords) and 
            any(word in user_input_lower for word in course_keywords)) or \
           any(word in user_input_lower for word in ready_keywords):
            
            if self.preferences.is_complete():
                self.conversation_complete = True
                self.user_ready_to_generate = True
                return "Perfect! I have all the information I need. I'll now generate your personalized learning course. Please click the 'Generate Course' button below!"
            else:
                missing = ", ".join(self.preferences.get_missing_fields())
                return f"I'd love to generate your course, but I still need some information about: {missing}. Let's complete these details first!"
        
        # Extract preferences from user input FIRST
        self.preferences = self.extract_preferences_from_input(user_input)
        
        # Generate contextual response
        response = self.generate_contextual_response(user_input)
        
        # Add AI response to memory
        self.memory.chat_memory.add_ai_message(response)
        
        return response
    
    def generate_contextual_response(self, user_input: str) -> str:
        """Generate a contextual response using the conversation history"""
        
        missing_fields = self.preferences.get_missing_fields()
        
        system_prompt = f"""
        You are a friendly, helpful learning consultant having a natural conversation with a user to create their personalized learning plan.
        
        Current user preferences: {json.dumps(self.preferences.dict(), indent=2)}
        Missing information: {', '.join(missing_fields) if missing_fields else 'None - all core info collected!'}
        
        Your conversation goals:
        1. Have a natural, engaging conversation about their learning needs
        2. Help them refine and adjust their preferences
        3. Address any questions or concerns they have
        4. If information is missing, naturally work it into the conversation
        5. If they want to change something, be flexible and accommodating
        6. When you have enough info, offer to generate their learning plan
        
        Conversation guidelines:
        - Be conversational and warm, not robotic
        - Ask follow-up questions to understand their needs better
        - Acknowledge what they've shared and build on it
        - If they mention specific requirements, ask clarifying questions
        - If they want to modify something, confirm the changes
        - Only ask about 1-2 things at a time, don't overwhelm
        - Show enthusiasm for their learning goals
        
        User just said: "{user_input}"
        
        Respond naturally as a learning consultant would in a real conversation.
        """
        
        # Get conversation history
        messages = [SystemMessage(content=system_prompt)]
        
        # Add relevant conversation history (last 6 messages)
        if self.memory.chat_memory.messages:
            messages.extend(self.memory.chat_memory.messages[-6:])
        
        # Add the current user input as context
        messages.append(HumanMessage(content=user_input))
        
        response = self.llm.invoke(messages)
        return response.content