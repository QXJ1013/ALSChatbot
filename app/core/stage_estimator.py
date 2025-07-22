from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np

class StageEstimator:
    """ALS stage identifier"""
    
    STAGES = {
        "early": "Early Stage",
        "middle": "Middle Stage", 
        "advanced": "Advanced Stage",
        "terminal": "Terminal Stage"
    }
    
    def __init__(self):
        self.features = [
            "mobility_score",
            "speech_clarity",
            "breathing_difficulty",
            "daily_activity_score",
            "time_since_diagnosis"
        ]
    
    async def estimate(self, user_id: str, context: Dict) -> Dict[str, Any]:
        """Estimate user's current disease stage"""
        # Get user health metrics
        health_metrics = await self._get_health_metrics(user_id)
        
        # Calculate stage probabilities
        stage_probabilities = self._calculate_stage_probabilities(health_metrics)
        
        # Get most likely stage
        current_stage = max(stage_probabilities, key=stage_probabilities.get)
        confidence = stage_probabilities[current_stage]
        
        return {
            "stage": current_stage,
            "stage_name": self.STAGES[current_stage],
            "confidence": confidence,
            "probabilities": stage_probabilities,
            "last_assessed": datetime.utcnow()
        }
    
    async def _get_health_metrics(self, user_id: str) -> Dict[str, float]:
        """Get user health metrics"""
        # TODO: Retrieve actual data from database
        # For now, return mock data
        return {
            "mobility_score": 0.7,        # 0.0 (no mobility) to 1.0 (full mobility)
            "speech_clarity": 0.8,        # 0.0 (no speech) to 1.0 (clear speech)
            "breathing_difficulty": 0.3,  # 0.0 (no difficulty) to 1.0 (severe difficulty)
            "daily_activity_score": 0.75, # 0.0 (no independence) to 1.0 (full independence)
            "time_since_diagnosis": 365   # days since diagnosis
        }
    
    def _calculate_stage_probabilities(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """Calculate probability for each stage"""
        # Simplified rule-based calculation
        mobility = metrics["mobility_score"]
        speech = metrics["speech_clarity"]
        breathing = metrics["breathing_difficulty"]
        daily_activities = metrics["daily_activity_score"]
        
        probabilities = {}
        
        # Early stage: Most functions normal
        if mobility > 0.8 and speech > 0.8 and breathing < 0.2:
            probabilities["early"] = 0.8
            probabilities["middle"] = 0.2
            probabilities["advanced"] = 0.0
            probabilities["terminal"] = 0.0
        
        # Middle stage: Some functions impaired
        elif mobility > 0.5 and speech > 0.5 and daily_activities > 0.5:
            probabilities["early"] = 0.1
            probabilities["middle"] = 0.7
            probabilities["advanced"] = 0.2
            probabilities["terminal"] = 0.0
        
        # Advanced stage: Severe functional impairment
        elif mobility > 0.2 or speech > 0.3:
            probabilities["early"] = 0.0
            probabilities["middle"] = 0.2
            probabilities["advanced"] = 0.7
            probabilities["terminal"] = 0.1
        
        # Terminal stage: Severe impairment across all functions
        else:
            probabilities["early"] = 0.0
            probabilities["middle"] = 0.0
            probabilities["advanced"] = 0.3
            probabilities["terminal"] = 0.7
            
        return probabilities
    
    def _extract_stage_indicators_from_text(self, text: str) -> Dict[str, float]:
        """Extract stage indicators from user's text input"""
        # AI-powered text analysis for stage estimation
        indicators = {
            "mobility_hints": 0.5,
            "speech_hints": 0.5,
            "breathing_hints": 0.5,
            "emotional_state": 0.5
        }
        
        text_lower = text.lower()
        
        # Mobility indicators
        if any(word in text_lower for word in ["can't walk", "wheelchair", "walker", "falling"]):
            indicators["mobility_hints"] = 0.2
        elif any(word in text_lower for word in ["walking slowly", "stiff", "weak legs"]):
            indicators["mobility_hints"] = 0.4
        elif any(word in text_lower for word in ["walking fine", "still mobile"]):
            indicators["mobility_hints"] = 0.8
        
        # Speech indicators
        if any(word in text_lower for word in ["can't speak", "slurred", "hard to understand"]):
            indicators["speech_hints"] = 0.3
        elif any(word in text_lower for word in ["speaking clearly", "no speech problems"]):
            indicators["speech_hints"] = 0.9
        
        # Breathing indicators
        if any(word in text_lower for word in ["breathing problems", "shortness of breath", "ventilator"]):
            indicators["breathing_hints"] = 0.2
        elif any(word in text_lower for word in ["breathing fine", "no breathing issues"]):
            indicators["breathing_hints"] = 0.9
        
        return indicators