from typing import Optional, Dict, List
import random
from datetime import datetime, timedelta

class ProactivityEngine:
    """Proactive questioning strategy engine"""
    
    def __init__(self):
        self.load_question_templates()
    
    def load_question_templates(self):
        """Load question templates"""
        self.questions = {
            "early": {
                "information": [
                    "Would you like to learn more about recent ALS research developments?",
                    "Would you like me to introduce some early-stage rehabilitation methods?",
                    "Are you interested in knowing about adaptive equipment that might help?"
                ],
                "emotional": [
                    "How have you been feeling lately? Is there anything you'd like to talk about?",
                    "The adjustment period after diagnosis can be challenging. How are you coping?",
                    "What emotions are you experiencing right now?"
                ]
            },
            "middle": {
                "physical": [
                    "How is your mobility today? Are you facing any particular challenges?",
                    "Have you been using any assistive devices recently? How are they working for you?",
                    "Are you experiencing any new symptoms we should discuss?"
                ],
                "social": [
                    "How is your family supporting you through this?",
                    "Have you considered joining any patient support groups?",
                    "Are you feeling connected to your support network?"
                ]
            },
            "advanced": {
                "comfort": [
                    "Are you experiencing any discomfort right now?",
                    "How has your sleep quality been? Would you like some suggestions for improvement?",
                    "Is there anything we can do to make you more comfortable?"
                ],
                "spiritual": [
                    "Are there any wishes or things you'd like to accomplish?",
                    "Would you like to talk about what's most important to you right now?",
                    "What gives your life meaning at this stage?"
                ]
            }
        }
        
        self.follow_ups = {
            "symptom_mentioned": "How long have you been experiencing this symptom?",
            "medication_discussed": "How is that medication working for you? Are there any side effects?",
            "family_mentioned": "Are your family members aware of this situation? How do they feel about it?",
            "treatment_mentioned": "How are you responding to this treatment?",
            "mood_mentioned": "Can you tell me more about how you're feeling emotionally?"
        }
    
    async def get_next_question(self, context: Dict, stage_info: Dict) -> Optional[str]:
        """Get next proactive question"""
        # Check if we should ask a question
        if not self._should_ask_question(context):
            return None
        
        # Get relevant questions
        stage = stage_info["stage"]
        last_topic = context.get("last_topic")
        
        # Prioritize follow-up questions
        if last_topic in self.follow_ups:
            return self.follow_ups[last_topic]
        
        # Select questions based on stage
        stage_questions = self.questions.get(stage, {})
        if not stage_questions:
            return None
        
        # Randomly select category and question
        category = random.choice(list(stage_questions.keys()))
        questions = stage_questions[category]
        
        return random.choice(questions) if questions else None
    
    def _should_ask_question(self, context: Dict) -> bool:
        """Determine if we should ask a proactive question"""
        # Check conversation turn count
        turn_count = context.get("turn_count", 0)
        if turn_count < 3:  # Don't ask proactive questions in first few turns
            return False
        
        # Check time since last question
        last_question_time = context.get("last_question_time")
        if last_question_time:
            time_since = datetime.utcnow() - last_question_time
            if time_since < timedelta(minutes=5):  # Don't repeat questions within 5 minutes
                return False
        
        # Check if user seems engaged
        user_engagement = context.get("engagement_score", 0.5)
        if user_engagement < 0.3:  # Don't ask if user seems disengaged
            return False
        
        # Probabilistic questioning
        return random.random() < 0.3  # 30% chance of asking