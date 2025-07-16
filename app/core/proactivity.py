from typing import Optional, Dict, List
import random
from datetime import datetime, timedelta

class ProactivityEngine:
    """主动提问策略引擎"""
    
    def __init__(self):
        self.load_question_templates()
    
    def load_question_templates(self):
        """加载提问模板"""
        self.questions = {
            "early": {
                "information": [
                    "您想了解更多关于ALS的科学进展吗？",
                    "需要我介绍一些早期康复训练的方法吗？"
                ],
                "emotional": [
                    "最近心情怎么样？有什么想聊的吗？",
                    "诊断后的适应期确实不容易，您现在感觉如何？"
                ]
            },
            "middle": {
                "physical": [
                    "今天的活动能力如何？有遇到什么困难吗？",
                    "最近有使用什么辅助设备吗？效果怎么样？"
                ],
                "social": [
                    "家人对您的支持怎么样？",
                    "有考虑加入患者互助组织吗？"
                ]
            },
            "advanced": {
                "comfort": [
                    "现在有什么不舒服的地方吗？",
                    "睡眠质量怎么样？需要一些改善建议吗？"
                ],
                "spiritual": [
                    "有什么心愿或者想完成的事情吗？",
                    "想聊聊您觉得重要的事情吗？"
                ]
            }
        }
        
        self.follow_ups = {
            "symptom_mentioned": "您提到的这个症状持续多久了？",
            "medication_discussed": "这个药物的效果怎么样？有副作用吗？",
            "family_mentioned": "家人对这个情况了解吗？他们是怎么看的？"
        }
    
    async def get_next_question(self, context: Dict, stage_info: Dict) -> Optional[str]:
        """获取下一个主动提问"""
        # 检查是否应该提问
        if not self._should_ask_question(context):
            return None
        
        # 获取相关问题
        stage = stage_info["stage"]
        last_topic = context.get("last_topic")
        
        # 优先跟进问题
        if last_topic in self.follow_ups:
            return self.follow_ups[last_topic]
        
        # 根据阶段选择问题类别
        stage_questions = self.questions.get(stage, {})
        if not stage_questions:
            return None
        
        # 随机选择类别和问题
        category = random.choice(list(stage_questions.keys()))
        questions = stage_questions[category]
        
        return random.choice(questions) if questions else None
    
    def _should_ask_question(self, context: Dict) -> bool:
        """判断是否应该主动提问"""
        # 检查对话轮次
        turn_count = context.get("turn_count", 0)
        if turn_count < 3:  # 前几轮不主动提问
            return False
        
        # 检查上次提问时间
        last_question_time = context.get("last_question_time")
        if last_question_time:
            time_since = datetime.utcnow() - last_question_time
            if time_since < timedelta(minutes=5):  # 5分钟内不重复提问
                return False
        
        # 概率性提问
        return random.random() < 0.3  # 30%概率提问