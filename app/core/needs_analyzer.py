from typing import List, Dict, Any
import re
import json

class NeedsAnalyzer:
    """Needs identification analyzer"""
    
    def __init__(self):
        self.load_patterns()
    
    def load_patterns(self):
        """Load needs identification patterns"""
        # TODO: Load from file
        self.patterns = {
            "physical": {
                "keywords": ["pain", "weakness", "fatigue", "breathing", "swallowing", "mobility", "walking", "movement"],
                "patterns": [r".*feel.*weak.*", r".*breathing.*difficult.*", r".*trouble.*swallowing.*", r".*can't.*move.*"]
            },
            "emotional": {
                "keywords": ["anxious", "scared", "worried", "depressed", "lonely", "upset", "frustrated", "angry"],
                "patterns": [r".*feel.*anxious.*", r".*very.*scared.*", r".*feeling.*depressed.*"]
            },
            "social": {
                "keywords": ["family", "friends", "talk", "understand", "company", "support", "isolation", "alone"],
                "patterns": [r".*want.*to.*talk.*", r".*need.*company.*", r".*feeling.*alone.*"]
            },
            "information": {
                "keywords": ["understand", "know", "information", "treatment", "medication", "therapy", "research"],
                "patterns": [r".*want.*to.*understand.*", r".*what.*treatment.*", r".*how.*does.*work.*"]
            },
            "spiritual": {
                "keywords": ["meaning", "purpose", "faith", "hope", "legacy", "God", "prayer", "afterlife"],
                "patterns": [r".*life.*meaning.*", r".*still.*hope.*", r".*what.*purpose.*"]
            }
        }
    
    async def analyze(self, message: str, stage_info: Dict) -> List[Dict[str, Any]]:
        """Analyze user needs"""
        needs = []
        
        # Keyword matching
        for need_type, config in self.patterns.items():
            score = self._calculate_need_score(message, config)
            if score > 0.3:
                needs.append({
                    "type": need_type,
                    "confidence": score,
                    "matched_keywords": self._find_matched_keywords(message, config["keywords"])
                })
        
        # Adjust need weights based on stage
        needs = self._adjust_by_stage(needs, stage_info)
        
        # Sort by confidence
        needs.sort(key=lambda x: x["confidence"], reverse=True)
        
        return needs[:3]  # Return top 3 most likely needs
    
    def _calculate_need_score(self, message: str, config: Dict) -> float:
        """Calculate need matching score"""
        score = 0.0
        message_lower = message.lower()
        
        # Keyword matching
        for keyword in config["keywords"]:
            if keyword.lower() in message_lower:
                score += 0.3
        
        # Pattern matching
        for pattern in config["patterns"]:
            if re.search(pattern, message_lower):
                score += 0.5
        
        return min(score, 1.0)
    
    def _find_matched_keywords(self, message: str, keywords: List[str]) -> List[str]:
        """Find matched keywords"""
        message_lower = message.lower()
        return [kw for kw in keywords if kw.lower() in message_lower]
    
    def _adjust_by_stage(self, needs: List[Dict], stage_info: Dict) -> List[Dict]:
        """Adjust need weights based on disease stage"""
        stage = stage_info["stage"]
        
        # Stage-specific need weight adjustments
        adjustments = {
            "early": {"information": 1.2, "emotional": 1.1},
            "middle": {"physical": 1.2, "social": 1.1},
            "advanced": {"physical": 1.3, "spiritual": 1.2},
            "terminal": {"spiritual": 1.4, "emotional": 1.3}
        }
        
        stage_adj = adjustments.get(stage, {})
        
        for need in needs:
            need_type = need["type"]
            if need_type in stage_adj:
                need["confidence"] *= stage_adj[need_type]
        
        return needs