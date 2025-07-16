from typing import List, Dict, Any
import re
import json

class NeedsAnalyzer:
    """需求识别分析器"""
    
    def __init__(self):
        self.load_patterns()
    
    def load_patterns(self):
        """加载需求识别模式"""
        # TODO: 从文件加载
        self.patterns = {
            "physical": {
                "keywords": ["疼痛", "无力", "疲劳", "呼吸", "吞咽"],
                "patterns": [r".*感觉.*无力.*", r".*呼吸.*困难.*"]
            },
            "emotional": {
                "keywords": ["焦虑", "害怕", "担心", "抑郁", "孤独"],
                "patterns": [r".*感到.*焦虑.*", r".*很.*害怕.*"]
            },
            "social": {
                "keywords": ["家人", "朋友", "交流", "理解", "陪伴"],
                "patterns": [r".*想.*聊天.*", r".*需要.*陪伴.*"]
            },
            "information": {
                "keywords": ["了解", "知道", "信息", "治疗", "药物"],
                "patterns": [r".*想.*了解.*", r".*有什么.*方法.*"]
            },
            "spiritual": {
                "keywords": ["意义", "价值", "信仰", "希望"],
                "patterns": [r".*生活.*意义.*", r".*还有.*希望.*"]
            }
        }
    
    async def analyze(self, message: str, stage_info: Dict) -> List[Dict[str, Any]]:
        """分析用户需求"""
        needs = []
        
        # 关键词匹配
        for need_type, config in self.patterns.items():
            score = self._calculate_need_score(message, config)
            if score > 0.3:
                needs.append({
                    "type": need_type,
                    "confidence": score,
                    "matched_keywords": self._find_matched_keywords(message, config["keywords"])
                })
        
        # 根据阶段调整需求权重
        needs = self._adjust_by_stage(needs, stage_info)
        
        # 排序
        needs.sort(key=lambda x: x["confidence"], reverse=True)
        
        return needs[:3]  # 返回前3个最可能的需求
    
    def _calculate_need_score(self, message: str, config: Dict) -> float:
        """计算需求匹配分数"""
        score = 0.0
        
        # 关键词匹配
        for keyword in config["keywords"]:
            if keyword in message:
                score += 0.3
        
        # 模式匹配
        for pattern in config["patterns"]:
            if re.match(pattern, message):
                score += 0.5
        
        return min(score, 1.0)
    
    def _find_matched_keywords(self, message: str, keywords: List[str]) -> List[str]:
        """找出匹配的关键词"""
        return [kw for kw in keywords if kw in message]
    
    def _adjust_by_stage(self, needs: List[Dict], stage_info: Dict) -> List[Dict]:
        """根据疾病阶段调整需求权重"""
        stage = stage_info["stage"]
        
        # 阶段特定的需求权重调整
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