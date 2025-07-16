from typing import Dict, Any, Optional
import json
from transformers import pipeline

class EmotionDetector:
    """情绪识别模块"""
    
    def __init__(self):
        # 加载情绪分析模型
        self.classifier = pipeline(
            "sentiment-analysis",
            model="uer/chinese_roberta_L-12_H-768"
        )
        self.load_emotion_keywords()
    
    def load_emotion_keywords(self):
        """加载情绪关键词"""
        # TODO: 从文件加载
        self.emotion_keywords = {
            "positive": ["开心", "希望", "感谢", "欣慰", "乐观"],
            "negative": ["难过", "绝望", "痛苦", "害怕", "焦虑"],
            "neutral": ["了解", "知道", "询问", "请问"]
        }
    
    async def detect(self, message: str) -> Dict[str, Any]:
        """检测用户情绪"""
        # 使用预训练模型
        model_result = self.classifier(message)[0]
        
        # 关键词增强
        keyword_emotion = self._detect_by_keywords(message)
        
        # 综合判断
        emotion = self._combine_results(model_result, keyword_emotion)
        
        # 决定回应策略
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
        """基于关键词的情绪检测"""
        scores = {"positive": 0, "negative": 0, "neutral": 0}
        
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    scores[emotion] += 1
        
        # 归一化
        total = sum(scores.values()) or 1
        for emotion in scores:
            scores[emotion] /= total
        
        return scores
    
    def _combine_results(self, model_result: Dict, keyword_result: Dict) -> Dict:
        """综合模型和关键词结果"""
        # 简单加权平均
        model_weight = 0.7
        keyword_weight = 0.3
        
        # 映射模型标签到情绪类别
        label_map = {
            "POSITIVE": "positive",
            "NEGATIVE": "negative",
            "NEUTRAL": "neutral"
        }
        
        model_emotion = label_map.get(model_result["label"], "neutral")
        model_score = model_result["score"]
        
        # 找出关键词最高分的情绪
        keyword_emotion = max(keyword_result, key=keyword_result.get)
        keyword_score = keyword_result[keyword_emotion]
        
        # 如果两者一致，增强置信度
        if model_emotion == keyword_emotion:
            final_score = model_weight * model_score + keyword_weight * keyword_score
            return {"label": model_emotion, "score": final_score}
        else:
            # 不一致时，以模型为主
            return {"label": model_emotion, "score": model_score * 0.8}
    
    def _determine_strategy(self, emotion: Dict) -> str:
        """根据情绪决定回应策略"""
        emotion_label = emotion["label"]
        confidence = emotion["score"]
        
        if emotion_label == "negative" and confidence > 0.7:
            return "empathetic"  # 共情回应
        elif emotion_label == "positive":
            return "encouraging"  # 鼓励回应
        else:
            return "informative"  # 信息性回应