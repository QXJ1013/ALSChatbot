from typing import List, Dict, Any
import yaml
from app.embedding.retriever import SemanticRetriever

class RecommendEngine:
    """推荐系统（规则+语义）"""
    
    def __init__(self):
        self.load_rules()
        self.semantic_retriever = SemanticRetriever()
    
    def load_rules(self):
        """加载推荐规则"""
        # TODO: 从YAML文件加载
        self.rules = {
            "physical": [
                {"type": "exercise", "name": "呼吸训练", "priority": 1},
                {"type": "equipment", "name": "辅助设备推荐", "priority": 2}
            ],
            "emotional": [
                {"type": "therapy", "name": "心理咨询", "priority": 1},
                {"type": "activity", "name": "冥想练习", "priority": 2}
            ],
            "social": [
                {"type": "community", "name": "患者互助群", "priority": 1},
                {"type": "service", "name": "志愿者陪伴", "priority": 2}
            ]
        }
    
    async def generate(self, needs: List[Dict], stage_info: Dict) -> List[Dict[str, Any]]:
        """生成个性化推荐"""
        recommendations = []
        
        for need in needs[:2]:  # 处理前2个主要需求
            need_type = need["type"]
            
            # 规则推荐
            rule_recs = self._get_rule_recommendations(need_type, stage_info)
            
            # 语义推荐
            semantic_recs = await self._get_semantic_recommendations(need, stage_info)
            
            # 合并和排序
            combined = self._combine_recommendations(rule_recs, semantic_recs)
            recommendations.extend(combined[:2])
        
        return self._deduplicate(recommendations)
    
    def _get_rule_recommendations(self, need_type: str, stage_info: Dict) -> List[Dict]:
        """基于规则的推荐"""
        base_recs = self.rules.get(need_type, [])
        
        # 根据阶段调整
        stage = stage_info["stage"]
        adjusted_recs = []
        
        for rec in base_recs:
            rec_copy = rec.copy()
            # 晚期患者优先推荐低强度活动
            if stage in ["advanced", "terminal"] and rec["type"] == "exercise":
                rec_copy["priority"] *= 0.5
            adjusted_recs.append(rec_copy)
        
        return adjusted_recs
    
    async def _get_semantic_recommendations(self, need: Dict, stage_info: Dict) -> List[Dict]:
        """基于语义搜索的推荐"""
        # 构建搜索查询
        query = f"{need['type']} {stage_info['stage_name']} ALS患者"
        
        # 语义搜索
        results = await self.semantic_retriever.search(query, top_k=3)
        
        # 转换为推荐格式
        semantic_recs = []
        for result in results:
            semantic_recs.append({
                "type": "resource",
                "name": result.metadata.get("title", "相关资源"),
                "content": result.content[:200],
                "score": result.score,
                "priority": result.score
            })
        
        return semantic_recs
    
    def _combine_recommendations(self, rule_recs: List[Dict], semantic_recs: List[Dict]) -> List[Dict]:
        """合并规则和语义推荐"""
        all_recs = rule_recs + semantic_recs
        # 按优先级排序
        all_recs.sort(key=lambda x: x.get("priority", 0), reverse=True)
        return all_recs
    
    def _deduplicate(self, recommendations: List[Dict]) -> List[Dict]:
        """去重"""
        seen = set()
        unique_recs = []
        for rec in recommendations:
            key = f"{rec['type']}:{rec['name']}"
            if key not in seen:
                seen.add(key)
                unique_recs.append(rec)
        return unique_recs