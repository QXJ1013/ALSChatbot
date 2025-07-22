from typing import List, Dict, Any
import yaml
from app.embedding.retriever import SemanticRetriever

class RecommendEngine:
    """Recommendation system (rules + semantic)"""
    
    def __init__(self):
        self.load_rules()
        self.semantic_retriever = SemanticRetriever()
    
    def load_rules(self):
        """Load recommendation rules"""
        # TODO: Load from YAML file
        self.rules = {
            "physical": [
                {"type": "exercise", "name": "Breathing exercises", "priority": 1},
                {"type": "equipment", "name": "Assistive device recommendations", "priority": 2},
                {"type": "therapy", "name": "Physical therapy", "priority": 3}
            ],
            "emotional": [
                {"type": "therapy", "name": "Psychological counseling", "priority": 1},
                {"type": "activity", "name": "Meditation practice", "priority": 2},
                {"type": "support", "name": "Peer support groups", "priority": 3}
            ],
            "social": [
                {"type": "community", "name": "Patient support groups", "priority": 1},
                {"type": "service", "name": "Volunteer companionship", "priority": 2},
                {"type": "resource", "name": "Family support resources", "priority": 3}
            ],
            "information": [
                {"type": "education", "name": "ALS educational materials", "priority": 1},
                {"type": "research", "name": "Latest research updates", "priority": 2},
                {"type": "guide", "name": "Treatment option guides", "priority": 3}
            ],
            "spiritual": [
                {"type": "counseling", "name": "Spiritual counseling", "priority": 1},
                {"type": "activity", "name": "Meaningful activities", "priority": 2},
                {"type": "legacy", "name": "Legacy planning resources", "priority": 3}
            ]
        }
    
    async def generate(self, needs: List[Dict], stage_info: Dict) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = []
        
        for need in needs[:2]:  # Process top 2 primary needs
            need_type = need["type"]
            
            # Rule-based recommendations
            rule_recs = self._get_rule_recommendations(need_type, stage_info)
            
            # Semantic recommendations
            semantic_recs = await self._get_semantic_recommendations(need, stage_info)
            
            # Combine and sort
            combined = self._combine_recommendations(rule_recs, semantic_recs)
            recommendations.extend(combined[:2])
        
        return self._deduplicate(recommendations)
    
    def _get_rule_recommendations(self, need_type: str, stage_info: Dict) -> List[Dict]:
        """Rule-based recommendations"""
        base_recs = self.rules.get(need_type, [])
        
        # Adjust based on stage
        stage = stage_info["stage"]
        adjusted_recs = []
        
        for rec in base_recs:
            rec_copy = rec.copy()
            # Advanced stage patients prioritize low-intensity activities
            if stage in ["advanced", "terminal"] and rec["type"] == "exercise":
                rec_copy["priority"] *= 0.5
            # Early stage patients benefit more from information
            elif stage == "early" and rec["type"] == "education":
                rec_copy["priority"] *= 1.3
            adjusted_recs.append(rec_copy)
        
        return adjusted_recs
    
    async def _get_semantic_recommendations(self, need: Dict, stage_info: Dict) -> List[Dict]:
        """Semantic search-based recommendations"""
        # Construct search query
        query = f"{need['type']} {stage_info['stage']} ALS patient support"
        
        # Semantic search
        results = await self.semantic_retriever.search(query, top_k=3)
        
        # Convert to recommendation format
        semantic_recs = []
        for result in results:
            semantic_recs.append({
                "type": "resource",
                "name": result.metadata.get("title", "Related resource"),
                "content": result.content[:200],
                "score": result.score,
                "priority": result.score
            })
        
        return semantic_recs
    
    def _combine_recommendations(self, rule_recs: List[Dict], semantic_recs: List[Dict]) -> List[Dict]:
        """Combine rule and semantic recommendations"""
        all_recs = rule_recs + semantic_recs
        # Sort by priority
        all_recs.sort(key=lambda x: x.get("priority", 0), reverse=True)
        return all_recs
    
    def _deduplicate(self, recommendations: List[Dict]) -> List[Dict]:
        """Remove duplicates"""
        seen = set()
        unique_recs = []
        for rec in recommendations:
            key = f"{rec['type']}:{rec['name']}"
            if key not in seen:
                seen.add(key)
                unique_recs.append(rec)
        return unique_recs