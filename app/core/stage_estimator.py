from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np

class StageEstimator:
    """ALS阶段识别器"""
    
    STAGES = {
        "early": "早期",
        "middle": "中期", 
        "advanced": "晚期",
        "terminal": "终末期"
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
        """评估用户当前的疾病阶段"""
        # 获取用户健康指标
        health_metrics = await self._get_health_metrics(user_id)
        
        # 计算阶段概率
        stage_probabilities = self._calculate_stage_probabilities(health_metrics)
        
        # 获取最可能的阶段
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
        """获取用户健康指标"""
        # TODO: 从数据库获取实际数据
        return {
            "mobility_score": 0.7,
            "speech_clarity": 0.8,
            "breathing_difficulty": 0.3,
            "daily_activity_score": 0.75,
            "time_since_diagnosis": 365  # 天数
        }
    
    def _calculate_stage_probabilities(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """计算各阶段的概率"""
        # 简化的规则基础计算
        mobility = metrics["mobility_score"]
        speech = metrics["speech_clarity"]
        breathing = metrics["breathing_difficulty"]
        
        probabilities = {}
        
        # 早期：功能大部分正常
        if mobility > 0.8 and speech > 0.8 and breathing < 0.2:
            probabilities["early"] = 0.8
            probabilities["middle"] = 0.2
            probabilities["advanced"] = 0.0
            probabilities["terminal"] = 0.0
        # 中期：部分功能受损
        elif mobility > 0.5 and speech > 0.5:
            probabilities["early"] = 0.1
            probabilities["middle"] = 0.7
            probabilities["advanced"] = 0.2
            probabilities["terminal"] = 0.0
        # 晚期：严重功能受损
        elif mobility > 0.2:
            probabilities["early"] = 0.0
            probabilities["middle"] = 0.2
            probabilities["advanced"] = 0.7
            probabilities["terminal"] = 0.1
        # 终末期
        else:
            probabilities["early"] = 0.0
            probabilities["middle"] = 0.0
            probabilities["advanced"] = 0.3
            probabilities["terminal"] = 0.7
            
        return probabilities