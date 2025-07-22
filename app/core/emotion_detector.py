from typing import Dict, Any, Optional
import json
from transformers import pipeline

class EmotionDetector:
    """Emotion detection module"""
    
    def __init__(self):
        # Load emotion analysis model
        self.classifier = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
        self.load_emotion_keywords()
    
    def load_emotion_keywords(self):
        """Load emotion keywords"""
        # TODO: Load from file
        self.emotion_keywords = {
            "positive": ["happy", "hope", "grateful", "relieved", "optimistic", "blessed", "peaceful", "content"],
            "negative": ["sad", "despair", "pain", "afraid", "anxious", "worried", "frustrated", "angry", "lonely"],
            "neutral": ["understand", "know", "ask", "question", "wonder", "curious"]
        }
    
    async def detect(self, message: str) -> Dict[str, Any]:
        """Detect user emotion"""
        # Use pre-trained model
        model_result = self.classifier(message)[0]
        
        # Keyword enhancement
        keyword_emotion = self._detect_by_keywords(message)
        
        # Combined judgment
        emotion = self._combine_results(model_result, keyword_emotion)
        
        # Determine response strategy
        strategy = self._determine_strategy(emotion)
        
        return {
            "emotion": emotion["label"],
            "confidence": emotion["score"],
            "strategy": strategy,
            "details": {
                "model_result": model_result,
                "keyword_result": keyword_emotion
            }
        }
    
    def _detect_by_keywords(self, message: str) -> Dict[str, float]:
        """Keyword-based emotion detection"""
        scores = {"positive": 0, "negative": 0, "neutral": 0}
        
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword.lower() in message.lower():
                    scores[emotion] += 1
        
        # Normalize
        total = sum(scores.values()) or 1
        for emotion in scores:
            scores[emotion] /= total
        
        return scores
    
    def _combine_results(self, model_result: Dict, keyword_result: Dict) -> Dict:
        """Combine model and keyword results"""
        # Simple weighted average
        model_weight = 0.7
        keyword_weight = 0.3
        
        # Map model labels to emotion categories
        label_map = {
            "POSITIVE": "positive",
            "NEGATIVE": "negative",
            "NEUTRAL": "neutral"
        }
        
        model_emotion = label_map.get(model_result["label"], "neutral")
        model_score = model_result["score"]
        
        # Find highest scoring keyword emotion
        keyword_emotion = max(keyword_result, key=keyword_result.get)
        keyword_score = keyword_result[keyword_emotion]
        
        # If both agree, boost confidence
        if model_emotion == keyword_emotion:
            final_score = model_weight * model_score + keyword_weight * keyword_score
            return {"label": model_emotion, "score": final_score}
        else:
            # When inconsistent, prioritize model
            return {"label": model_emotion, "score": model_score * 0.8}
    
    def _determine_strategy(self, emotion: Dict) -> str:
        """Determine response strategy based on emotion"""
        emotion_label = emotion["label"]
        confidence = emotion["score"]
        
        if emotion_label == "negative" and confidence > 0.7:
            return "empathetic"  # Empathetic response
        elif emotion_label == "positive":
            return "encouraging"  # Encouraging response
        else:
            return "informative"  # Informative response