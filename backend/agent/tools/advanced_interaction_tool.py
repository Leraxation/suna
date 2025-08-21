"""
Advanced Interaction and Communication Tool for Suna AI
Implements sophisticated communication, user adaptation, and task management capabilities
Built on top of existing Suna AI infrastructure
"""

import json
import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import hashlib
import re
from collections import defaultdict, deque
import itertools

from agentpress.tool import Tool, ToolResult, openapi_schema, xml_schema
from services.llm import make_llm_api_call
from utils.logger import logger
from utils.config import config

class AdvancedInteractionTool(Tool):
    """Advanced interaction capabilities including natural communication, user adaptation, and task management."""

    def __init__(self):
        super().__init__()
        # Communication systems
        self.conversation_memory = deque(maxlen=1000)
        self.user_profiles = {}
        self.communication_patterns = defaultdict(list)
        
        # Task management systems
        self.active_tasks = {}
        self.task_history = []
        self.task_priorities = {}
        
        # User adaptation systems
        self.user_preferences = {}
        self.interaction_styles = {}
        self.learning_patterns = {}
        
        # Context management
        self.context_windows = {}
        self.topic_transitions = []
        self.conversation_threads = {}

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "natural_conversation_management",
            "description": "Manage natural conversation flow with context awareness, memory, and adaptive responses",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_input": {
                        "type": "string",
                        "description": "User's input message or query"
                    },
                    "conversation_id": {
                        "type": "string",
                        "description": "Unique identifier for the conversation thread",
                        "default": "default"
                    },
                    "context_depth": {
                        "type": "integer",
                        "description": "Number of previous messages to consider for context",
                        "default": 10
                    },
                    "response_style": {
                        "type": "string",
                        "description": "Desired response style (casual, professional, technical, creative, educational)",
                        "default": "adaptive"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier for personalization",
                        "default": "anonymous"
                    }
                },
                "required": ["user_input"]
            }
        }
    })
    async def natural_conversation_management(
        self, 
        user_input: str,
        conversation_id: str = "default",
        context_depth: int = 10,
        response_style: str = "adaptive",
        user_id: str = "anonymous"
    ) -> ToolResult:
        """Manage natural conversation with advanced context awareness and memory."""
        try:
            model_to_use = config.MODEL_TO_USE
            
            # Retrieve conversation context
            conversation_context = self._get_conversation_context(conversation_id, context_depth)
            user_profile = self._get_user_profile(user_id)
            communication_style = self._determine_communication_style(user_input, user_profile, response_style)
            
            # Analyze conversation elements
            conversation_analysis = await self._analyze_conversation_elements(user_input, conversation_context)
            
            # Detect conversation patterns and intent
            intent_analysis = await self._analyze_user_intent(user_input, conversation_context)
            
            messages = [{
                "role": "user",
                "content": f"""
                Manage natural conversation with advanced context awareness:
                
                Current User Input: {user_input}
                
                Conversation Context: {json.dumps(conversation_context, indent=2)}
                
                User Profile: {json.dumps(user_profile, indent=2)}
                
                Communication Style: {communication_style}
                
                Conversation Analysis: {json.dumps(conversation_analysis, indent=2)}
                
                Intent Analysis: {json.dumps(intent_analysis, indent=2)}
                
                Please provide a natural, contextually aware response that includes:
                
                1. **Context Integration**:
                   - Reference relevant previous conversation points
                   - Maintain conversation thread continuity
                   - Address any unresolved topics
                   - Build upon established context
                
                2. **Natural Language Processing**:
                   - Understand implied meaning and subtext
                   - Recognize emotional undertones
                   - Detect sarcasm, humor, or cultural references
                   - Interpret professional jargon or domain-specific language
                
                3. **Adaptive Communication**:
                   - Match user's communication style and tone
                   - Adjust complexity level to user's expertise
                   - Use appropriate formality level
                   - Incorporate user's preferred terminology
                
                4. **Memory Integration**:
                   - Reference relevant past interactions
                   - Show learning from previous conversations
                   - Maintain consistency with established facts
                   - Update understanding based on new information
                
                5. **Conversation Flow**:
                   - Provide smooth topic transitions
                   - Ask clarifying questions when needed
                   - Offer relevant follow-up suggestions
                   - Maintain engaging dialogue rhythm
                
                6. **Personalization**:
                   - Adapt to user's preferences and style
                   - Consider user's expertise level
                   - Respect cultural and personal sensitivities
                   - Provide relevant examples and analogies
                
                7. **Response Structure**:
                   - Main response addressing user's input
                   - Context acknowledgments
                   - Follow-up questions or suggestions
                   - Conversation continuation strategies
                
                Return response in structured JSON format with conversation management metadata.
                """
            }]
            
            response = await make_llm_api_call(
                messages=messages,
                model_name=model_to_use,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            conversation_response = json.loads(response.choices[0].message.content)
            
            # Update conversation memory and user profile
            self._update_conversation_memory(conversation_id, user_input, conversation_response, user_id)
            self._update_user_profile(user_id, user_input, conversation_response)
            
            return self.success_response({
                "conversation_response": conversation_response,
                "conversation_id": conversation_id,
                "user_id": user_id,
                "communication_style": communication_style,
                "context_depth": context_depth,
                "conversation_analysis": conversation_analysis,
                "intent_analysis": intent_analysis
            })
            
        except Exception as e:
            logger.error(f"Natural conversation management failed: {str(e)}")
            return self.fail_response(f"Natural conversation management failed: {str(e)}")

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "advanced_task_management",
            "description": "Manage complex multi-task scenarios with priority management, scheduling, and progress tracking",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_request": {
                        "type": "string",
                        "description": "Description of the task or task management request"
                    },
                    "task_type": {
                        "type": "string",
                        "description": "Type of task management (create, update, prioritize, schedule, track, complete)",
                        "default": "create"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier for task ownership",
                        "default": "anonymous"
                    },
                    "priority_level": {
                        "type": "string",
                        "description": "Task priority level (low, medium, high, urgent, critical)",
                        "default": "medium"
                    },
                    "deadline": {
                        "type": "string",
                        "description": "Task deadline in ISO format (optional)"
                    },
                    "dependencies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Task dependencies or prerequisites",
                        "default": []
                    }
                },
                "required": ["task_request"]
            }
        }
    })
    async def advanced_task_management(
        self, 
        task_request: str,
        task_type: str = "create",
        user_id: str = "anonymous",
        priority_level: str = "medium",
        deadline: Optional[str] = None,
        dependencies: List[str] = None
    ) -> ToolResult:
        """Manage complex tasks with advanced scheduling and tracking."""
        try:
            if dependencies is None:
                dependencies = []
            
            model_to_use = config.MODEL_TO_USE
            
            # Get current task context
            user_tasks = self._get_user_tasks(user_id)
            task_analytics = self._analyze_task_patterns(user_id)
            resource_availability = self._assess_resource_availability(user_id)
            
            messages = [{
                "role": "user",
                "content": f"""
                Manage advanced task with comprehensive planning and tracking:
                
                Task Request: {task_request}
                
                Task Type: {task_type}
                
                User ID: {user_id}
                
                Priority Level: {priority_level}
                
                Deadline: {deadline or "Not specified"}
                
                Dependencies: {json.dumps(dependencies, indent=2)}
                
                Current User Tasks: {json.dumps(user_tasks, indent=2)}
                
                Task Analytics: {json.dumps(task_analytics, indent=2)}
                
                Resource Availability: {json.dumps(resource_availability, indent=2)}
                
                Please provide comprehensive task management including:
                
                1. **Task Analysis and Decomposition**:
                   - Break down complex tasks into subtasks
                   - Identify required skills and resources
                   - Estimate time and effort requirements
                   - Determine task complexity and risk factors
                
                2. **Priority Management**:
                   - Assess task importance and urgency
                   - Consider impact on other tasks
                   - Evaluate resource constraints
                   - Recommend priority adjustments
                
                3. **Scheduling and Planning**:
                   - Optimal task sequencing
                   - Resource allocation planning
                   - Timeline development
                   - Milestone identification
                
                4. **Dependency Management**:
                   - Map task dependencies
                   - Identify critical path
                   - Plan for dependency resolution
                   - Risk mitigation for blocked tasks
                
                5. **Progress Tracking**:
                   - Define measurable progress indicators
                   - Set up monitoring checkpoints
                   - Create progress reporting structure
                   - Establish completion criteria
                
                6. **Resource Optimization**:
                   - Identify required resources
                   - Optimize resource allocation
                   - Plan for resource conflicts
                   - Suggest efficiency improvements
                
                7. **Risk Management**:
                   - Identify potential risks and blockers
                   - Develop contingency plans
                   - Monitor risk indicators
                   - Plan mitigation strategies
                
                8. **Task Coordination**:
                   - Integration with existing tasks
                   - Team collaboration requirements
                   - Communication planning
                   - Handoff procedures
                
                Return comprehensive task management plan in structured JSON format.
                """
            }]
            
            response = await make_llm_api_call(
                messages=messages,
                model_name=model_to_use,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            task_management = json.loads(response.choices[0].message.content)
            
            # Update task management systems
            task_id = self._update_task_management(user_id, task_request, task_management, task_type)
            
            return self.success_response({
                "task_management": task_management,
                "task_id": task_id,
                "task_type": task_type,
                "user_id": user_id,
                "priority_level": priority_level,
                "deadline": deadline,
                "dependencies": dependencies
            })
            
        except Exception as e:
            logger.error(f"Advanced task management failed: {str(e)}")
            return self.fail_response(f"Advanced task management failed: {str(e)}")

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "user_adaptation_learning",
            "description": "Learn and adapt to user preferences, communication styles, and interaction patterns",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier for personalization"
                    },
                    "interaction_data": {
                        "type": "object",
                        "description": "Data about user interaction patterns and preferences"
                    },
                    "feedback": {
                        "type": "object",
                        "description": "User feedback on previous interactions",
                        "default": {}
                    },
                    "adaptation_focus": {
                        "type": "string",
                        "description": "Focus area for adaptation (communication, expertise, preferences, workflow)",
                        "default": "comprehensive"
                    }
                },
                "required": ["user_id", "interaction_data"]
            }
        }
    })
    async def user_adaptation_learning(
        self, 
        user_id: str,
        interaction_data: Dict[str, Any],
        feedback: Dict[str, Any] = None,
        adaptation_focus: str = "comprehensive"
    ) -> ToolResult:
        """Learn and adapt to user preferences and patterns."""
        try:
            if feedback is None:
                feedback = {}
            
            model_to_use = config.MODEL_TO_USE
            
            # Get current user profile and learning patterns
            current_profile = self._get_user_profile(user_id)
            learning_history = self._get_learning_patterns(user_id)
            interaction_patterns = self._analyze_interaction_patterns(user_id, interaction_data)
            
            messages = [{
                "role": "user",
                "content": f"""
                Analyze user interaction patterns and adapt personalization:
                
                User ID: {user_id}
                
                Interaction Data: {json.dumps(interaction_data, indent=2)}
                
                User Feedback: {json.dumps(feedback, indent=2)}
                
                Adaptation Focus: {adaptation_focus}
                
                Current User Profile: {json.dumps(current_profile, indent=2)}
                
                Learning History: {json.dumps(learning_history, indent=2)}
                
                Interaction Patterns: {json.dumps(interaction_patterns, indent=2)}
                
                Please provide comprehensive user adaptation analysis including:
                
                1. **Communication Style Analysis**:
                   - Preferred communication tone and formality
                   - Language complexity and technical level
                   - Response length and detail preferences
                   - Cultural and contextual considerations
                
                2. **Expertise Level Assessment**:
                   - Domain knowledge evaluation
                   - Skill level in different areas
                   - Learning pace and style preferences
                   - Information processing preferences
                
                3. **Interaction Preferences**:
                   - Preferred interaction modes
                   - Response timing expectations
                   - Information presentation preferences
                   - Feedback and confirmation needs
                
                4. **Workflow Adaptation**:
                   - Task management preferences
                   - Work style and methodology
                   - Collaboration preferences
                   - Tool and interface preferences
                
                5. **Learning Pattern Recognition**:
                   - Learning style identification
                   - Knowledge retention patterns
                   - Skill development trajectories
                   - Adaptation speed and preferences
                
                6. **Personalization Recommendations**:
                   - Communication adjustments
                   - Interface customizations
                   - Content personalization
                   - Workflow optimizations
                
                7. **Feedback Integration**:
                   - Feedback analysis and interpretation
                   - Preference updates based on feedback
                   - Satisfaction improvement strategies
                   - Continuous learning adjustments
                
                8. **Adaptation Strategy**:
                   - Immediate adaptation actions
                   - Long-term learning goals
                   - Monitoring and measurement
                   - Continuous improvement plan
                
                Return comprehensive adaptation analysis in structured JSON format.
                """
            }]
            
            response = await make_llm_api_call(
                messages=messages,
                model_name=model_to_use,
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            
            adaptation_analysis = json.loads(response.choices[0].message.content)
            
            # Update user profile and learning patterns
            self._update_user_adaptation(user_id, adaptation_analysis, interaction_data, feedback)
            
            return self.success_response({
                "adaptation_analysis": adaptation_analysis,
                "user_id": user_id,
                "adaptation_focus": adaptation_focus,
                "interaction_patterns": interaction_patterns,
                "profile_updates": adaptation_analysis.get("personalization_recommendations", {}),
                "learning_improvements": adaptation_analysis.get("adaptation_strategy", {})
            })
            
        except Exception as e:
            logger.error(f"User adaptation learning failed: {str(e)}")
            return self.fail_response(f"User adaptation learning failed: {str(e)}")

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "multi_modal_communication",
            "description": "Handle multi-modal communication including text, context, and structured information processing",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "object",
                        "description": "Multi-modal content including text, structured data, and metadata"
                    },
                    "communication_mode": {
                        "type": "string",
                        "description": "Communication mode (text, structured, visual, interactive, educational)",
                        "default": "adaptive"
                    },
                    "target_audience": {
                        "type": "string",
                        "description": "Target audience level (beginner, intermediate, advanced, expert)",
                        "default": "intermediate"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Desired output format (narrative, structured, technical, creative, educational)",
                        "default": "adaptive"
                    },
                    "context_integration": {
                        "type": "boolean",
                        "description": "Whether to integrate with conversation context",
                        "default": True
                    }
                },
                "required": ["content"]
            }
        }
    })
    async def multi_modal_communication(
        self, 
        content: Dict[str, Any],
        communication_mode: str = "adaptive",
        target_audience: str = "intermediate",
        output_format: str = "adaptive",
        context_integration: bool = True
    ) -> ToolResult:
        """Handle sophisticated multi-modal communication."""
        try:
            model_to_use = config.MODEL_TO_USE
            
            # Analyze content structure and requirements
            content_analysis = self._analyze_content_structure(content)
            communication_requirements = self._determine_communication_requirements(
                content, communication_mode, target_audience
            )
            
            messages = [{
                "role": "user",
                "content": f"""
                Process multi-modal communication with sophisticated understanding:
                
                Content: {json.dumps(content, indent=2)}
                
                Communication Mode: {communication_mode}
                
                Target Audience: {target_audience}
                
                Output Format: {output_format}
                
                Context Integration: {context_integration}
                
                Content Analysis: {json.dumps(content_analysis, indent=2)}
                
                Communication Requirements: {json.dumps(communication_requirements, indent=2)}
                
                Please provide sophisticated multi-modal communication including:
                
                1. **Content Understanding**:
                   - Deep content analysis and interpretation
                   - Context and meaning extraction
                   - Relationship and pattern identification
                   - Key insight and theme recognition
                
                2. **Audience Adaptation**:
                   - Complexity level adjustment
                   - Terminology and language adaptation
                   - Cultural and contextual sensitivity
                   - Learning style accommodation
                
                3. **Communication Optimization**:
                   - Information structure optimization
                   - Clarity and comprehension enhancement
                   - Engagement and interest maintenance
                   - Accessibility and inclusivity
                
                4. **Multi-Modal Integration**:
                   - Text and structured data integration
                   - Visual and conceptual representation
                   - Interactive element suggestions
                   - Cross-modal consistency
                
                5. **Format Adaptation**:
                   - Output format optimization
                   - Presentation structure design
                   - Information hierarchy organization
                   - User experience enhancement
                
                6. **Context Integration**:
                   - Conversation context incorporation
                   - Historical reference integration
                   - Continuity and coherence maintenance
                   - Progressive disclosure planning
                
                7. **Educational Enhancement**:
                   - Learning objective alignment
                   - Knowledge building progression
                   - Skill development support
                   - Assessment and feedback integration
                
                8. **Communication Strategy**:
                   - Message delivery optimization
                   - Engagement strategy development
                   - Follow-up planning
                   - Effectiveness measurement
                
                Return comprehensive multi-modal communication in structured JSON format.
                """
            }]
            
            response = await make_llm_api_call(
                messages=messages,
                model_name=model_to_use,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            communication_result = json.loads(response.choices[0].message.content)
            
            # Store communication patterns for learning
            self._store_communication_pattern(content, communication_result, communication_mode)
            
            return self.success_response({
                "communication_result": communication_result,
                "communication_mode": communication_mode,
                "target_audience": target_audience,
                "output_format": output_format,
                "content_analysis": content_analysis,
                "communication_requirements": communication_requirements
            })
            
        except Exception as e:
            logger.error(f"Multi-modal communication failed: {str(e)}")
            return self.fail_response(f"Multi-modal communication failed: {str(e)}")

    # Helper methods for advanced interaction capabilities
    
    def _get_conversation_context(self, conversation_id: str, depth: int) -> List[Dict]:
        """Get conversation context for specified depth."""
        context = []
        for entry in reversed(list(self.conversation_memory)):
            if entry.get("conversation_id") == conversation_id:
                context.append(entry)
                if len(context) >= depth:
                    break
        
        return list(reversed(context))
    
    def _get_user_profile(self, user_id: str) -> Dict:
        """Get user profile with preferences and patterns."""
        return self.user_profiles.get(user_id, {
            "communication_style": "adaptive",
            "expertise_level": "intermediate",
            "preferences": {},
            "interaction_history": [],
            "learning_patterns": {}
        })
    
    def _determine_communication_style(self, user_input: str, user_profile: Dict, requested_style: str) -> str:
        """Determine optimal communication style."""
        if requested_style != "adaptive":
            return requested_style
        
        # Analyze user input for style indicators
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["please", "could you", "would you mind"]):
            return "professional"
        elif any(word in input_lower for word in ["hey", "yo", "sup", "cool", "awesome"]):
            return "casual"
        elif any(word in input_lower for word in ["implement", "algorithm", "function", "code"]):
            return "technical"
        elif any(word in input_lower for word in ["create", "design", "imagine", "innovative"]):
            return "creative"
        elif any(word in input_lower for word in ["explain", "teach", "learn", "understand"]):
            return "educational"
        
        # Fall back to user profile preference
        return user_profile.get("communication_style", "professional")
    
    async def _analyze_conversation_elements(self, user_input: str, context: List[Dict]) -> Dict:
        """Analyze conversation elements for better understanding."""
        analysis = {
            "emotional_tone": self._detect_emotional_tone(user_input),
            "complexity_level": self._assess_complexity_level(user_input),
            "topic_continuity": self._assess_topic_continuity(user_input, context),
            "question_type": self._classify_question_type(user_input),
            "urgency_level": self._assess_urgency_level(user_input)
        }
        
        return analysis
    
    async def _analyze_user_intent(self, user_input: str, context: List[Dict]) -> Dict:
        """Analyze user intent and conversation goals."""
        intent_analysis = {
            "primary_intent": self._classify_primary_intent(user_input),
            "secondary_intents": self._identify_secondary_intents(user_input),
            "conversation_goal": self._infer_conversation_goal(user_input, context),
            "action_required": self._determine_action_required(user_input),
            "information_seeking": self._assess_information_seeking(user_input)
        }
        
        return intent_analysis
    
    def _detect_emotional_tone(self, text: str) -> str:
        """Detect emotional tone in text."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["excited", "amazing", "fantastic", "love"]):
            return "positive"
        elif any(word in text_lower for word in ["frustrated", "annoyed", "problem", "issue"]):
            return "negative"
        elif any(word in text_lower for word in ["urgent", "asap", "immediately", "quickly"]):
            return "urgent"
        elif any(word in text_lower for word in ["curious", "wondering", "interested"]):
            return "curious"
        else:
            return "neutral"
    
    def _assess_complexity_level(self, text: str) -> str:
        """Assess complexity level of user input."""
        word_count = len(text.split())
        technical_terms = len([word for word in text.split() if len(word) > 8])
        
        if word_count > 50 or technical_terms > 3:
            return "high"
        elif word_count > 20 or technical_terms > 1:
            return "medium"
        else:
            return "low"
    
    def _assess_topic_continuity(self, user_input: str, context: List[Dict]) -> str:
        """Assess topic continuity in conversation."""
        if not context:
            return "new_topic"
        
        recent_topics = [entry.get("topic", "") for entry in context[-3:]]
        current_words = set(user_input.lower().split())
        
        for topic in recent_topics:
            topic_words = set(topic.lower().split())
            overlap = len(current_words.intersection(topic_words))
            if overlap > 2:
                return "continuing"
        
        return "topic_shift"
    
    def _classify_question_type(self, text: str) -> str:
        """Classify the type of question being asked."""
        text_lower = text.lower()
        
        if text_lower.startswith(("what", "which", "who")):
            return "factual"
        elif text_lower.startswith(("how", "can you")):
            return "procedural"
        elif text_lower.startswith(("why", "explain")):
            return "explanatory"
        elif "?" in text:
            return "general_inquiry"
        else:
            return "statement"
    
    def _classify_primary_intent(self, text: str) -> str:
        """Classify primary user intent."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["help", "assist", "support"]):
            return "seeking_help"
        elif any(word in text_lower for word in ["create", "make", "build", "generate"]):
            return "creation_request"
        elif any(word in text_lower for word in ["explain", "understand", "learn"]):
            return "learning"
        elif any(word in text_lower for word in ["analyze", "review", "evaluate"]):
            return "analysis_request"
        elif any(word in text_lower for word in ["fix", "solve", "debug", "troubleshoot"]):
            return "problem_solving"
        else:
            return "general_inquiry"
    
    def _update_conversation_memory(self, conversation_id: str, user_input: str, response: Dict, user_id: str):
        """Update conversation memory with new interaction."""
        entry = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response,
            "topic": self._extract_topic(user_input)
        }
        
        self.conversation_memory.append(entry)
    
    def _update_user_profile(self, user_id: str, user_input: str, response: Dict):
        """Update user profile based on interaction."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "communication_style": "adaptive",
                "expertise_level": "intermediate",
                "preferences": {},
                "interaction_history": [],
                "learning_patterns": {}
            }
        
        profile = self.user_profiles[user_id]
        
        # Update interaction history
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "response_type": response.get("response_type", "general"),
            "satisfaction": response.get("satisfaction_score", 0.5)
        }
        
        profile["interaction_history"].append(interaction)
        
        # Keep only recent interactions
        if len(profile["interaction_history"]) > 50:
            profile["interaction_history"] = profile["interaction_history"][-50:]
    
    def _extract_topic(self, text: str) -> str:
        """Extract main topic from text."""
        # Simple topic extraction - could be enhanced with NLP
        words = text.lower().split()
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        content_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        return " ".join(content_words[:3]) if content_words else "general"
    
    def _get_user_tasks(self, user_id: str) -> List[Dict]:
        """Get current tasks for user."""
        user_tasks = []
        for task_id, task_data in self.active_tasks.items():
            if task_data.get("user_id") == user_id:
                user_tasks.append({
                    "task_id": task_id,
                    "description": task_data.get("description", ""),
                    "priority": task_data.get("priority", "medium"),
                    "status": task_data.get("status", "active"),
                    "deadline": task_data.get("deadline"),
                    "progress": task_data.get("progress", 0)
                })
        
        return user_tasks
    
    def _analyze_task_patterns(self, user_id: str) -> Dict:
        """Analyze user's task patterns and preferences."""
        user_task_history = [task for task in self.task_history if task.get("user_id") == user_id]
        
        if not user_task_history:
            return {"pattern_analysis": "insufficient_data"}
        
        # Analyze patterns
        avg_completion_time = sum(task.get("completion_time", 0) for task in user_task_history) / len(user_task_history)
        common_priorities = {}
        for task in user_task_history:
            priority = task.get("priority", "medium")
            common_priorities[priority] = common_priorities.get(priority, 0) + 1
        
        return {
            "average_completion_time": avg_completion_time,
            "preferred_priorities": common_priorities,
            "task_count": len(user_task_history),
            "success_rate": sum(1 for task in user_task_history if task.get("status") == "completed") / len(user_task_history)
        }
    
    def _assess_resource_availability(self, user_id: str) -> Dict:
        """Assess resource availability for user."""
        # Simplified resource assessment
        active_task_count = len(self._get_user_tasks(user_id))
        
        return {
            "active_tasks": active_task_count,
            "capacity_utilization": min(active_task_count / 10, 1.0),  # Assume max 10 concurrent tasks
            "availability_status": "high" if active_task_count < 3 else "medium" if active_task_count < 7 else "low"
        }
    
    def _update_task_management(self, user_id: str, task_request: str, task_management: Dict, task_type: str) -> str:
        """Update task management systems."""
        task_id = hashlib.md5(f"{user_id}{task_request}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        if task_type == "create":
            self.active_tasks[task_id] = {
                "user_id": user_id,
                "description": task_request,
                "management_plan": task_management,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "priority": task_management.get("priority_assessment", {}).get("recommended_priority", "medium"),
                "progress": 0
            }
        
        return task_id
    
    def _get_learning_patterns(self, user_id: str) -> Dict:
        """Get learning patterns for user."""
        return self.learning_patterns.get(user_id, {
            "learning_style": "adaptive",
            "pace": "medium",
            "preferences": {},
            "strengths": [],
            "areas_for_improvement": []
        })
    
    def _analyze_interaction_patterns(self, user_id: str, interaction_data: Dict) -> Dict:
        """Analyze user interaction patterns."""
        user_profile = self._get_user_profile(user_id)
        interaction_history = user_profile.get("interaction_history", [])
        
        if not interaction_history:
            return {"pattern_analysis": "insufficient_data"}
        
        # Analyze patterns
        response_preferences = {}
        for interaction in interaction_history:
            response_type = interaction.get("response_type", "general")
            satisfaction = interaction.get("satisfaction", 0.5)
            
            if response_type not in response_preferences:
                response_preferences[response_type] = []
            response_preferences[response_type].append(satisfaction)
        
        # Calculate average satisfaction by response type
        avg_satisfaction = {}
        for response_type, satisfactions in response_preferences.items():
            avg_satisfaction[response_type] = sum(satisfactions) / len(satisfactions)
        
        return {
            "interaction_count": len(interaction_history),
            "response_preferences": avg_satisfaction,
            "overall_satisfaction": sum(interaction.get("satisfaction", 0.5) for interaction in interaction_history) / len(interaction_history)
        }
    
    def _update_user_adaptation(self, user_id: str, adaptation_analysis: Dict, interaction_data: Dict, feedback: Dict):
        """Update user adaptation based on analysis."""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        # Update preferences based on adaptation analysis
        recommendations = adaptation_analysis.get("personalization_recommendations", {})
        self.user_preferences[user_id].update(recommendations)
        
        # Update learning patterns
        learning_updates = adaptation_analysis.get("learning_pattern_recognition", {})
        if user_id not in self.learning_patterns:
            self.learning_patterns[user_id] = {}
        self.learning_patterns[user_id].update(learning_updates)
    
    def _analyze_content_structure(self, content: Dict) -> Dict:
        """Analyze structure and characteristics of content."""
        analysis = {
            "content_type": self._determine_content_type(content),
            "complexity_level": self._assess_content_complexity(content),
            "information_density": self._assess_information_density(content),
            "structure_type": self._identify_structure_type(content)
        }
        
        return analysis
    
    def _determine_content_type(self, content: Dict) -> str:
        """Determine the type of content."""
        if "code" in content or "programming" in str(content).lower():
            return "technical"
        elif "data" in content or "analysis" in str(content).lower():
            return "analytical"
        elif "story" in content or "narrative" in str(content).lower():
            return "narrative"
        elif "instructions" in content or "steps" in str(content).lower():
            return "procedural"
        else:
            return "informational"
    
    def _determine_communication_requirements(self, content: Dict, mode: str, audience: str) -> Dict:
        """Determine communication requirements based on content and context."""
        requirements = {
            "clarity_level": "high" if audience in ["beginner", "intermediate"] else "medium",
            "detail_level": "comprehensive" if mode == "educational" else "balanced",
            "interaction_level": "high" if mode == "interactive" else "medium",
            "visual_aids": mode in ["visual", "educational", "interactive"]
        }
        
        return requirements
    
    def _store_communication_pattern(self, content: Dict, result: Dict, mode: str):
        """Store communication pattern for learning."""
        pattern = {
            "content_type": self._determine_content_type(content),
            "communication_mode": mode,
            "result_quality": result.get("quality_score", 0.5),
            "timestamp": datetime.now().isoformat()
        }
        
        self.communication_patterns[mode].append(pattern)
        
        # Keep only recent patterns
        if len(self.communication_patterns[mode]) > 50:
            self.communication_patterns[mode] = self.communication_patterns[mode][-50:]