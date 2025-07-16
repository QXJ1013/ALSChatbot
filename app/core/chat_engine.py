from typing import Dict, Any, Optional
import asyncio
from langchain.memory import ConversationBufferMemory

from app.core.stage_estimator import StageEstimator
from app.core.needs_analyzer import NeedsAnalyzer
from app.core.recommend_engine import RecommendEngine
from app.core.emotion_detector import EmotionDetector
from app.core.proactivity import ProactivityEngine
from app.core.context_memory import ContextMemory
from app.core.prompt_builder import PromptBuilder
from app.utils.ibm_client import IBMClient  # Placeholder for Watson API wrapper
import structlog

logger = structlog.get_logger()

class ChatEngine:
    """Multiturn conversation manager for ALS semantic assistant."""

    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id

        self.stage_estimator = StageEstimator()
        self.needs_analyzer = NeedsAnalyzer()
        self.recommend_engine = RecommendEngine()
        self.emotion_detector = EmotionDetector()
        self.proactivity_engine = ProactivityEngine()
        self.prompt_builder = PromptBuilder()

        self.memory = ConversationBufferMemory()
        self.llm_client = IBMClient()  # Can support .generate(prompt) or similar

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message and return AI-driven response"""

        # 1. Load context history
        context = await ContextMemory.get_context(self.session_id)

        # 2. Run emotion detection
        emotion = await self.emotion_detector.detect(message)
        logger.info("Emotion detected", emotion=emotion)

        # 3. Estimate current ALS stage
        stage_info = await self.stage_estimator.estimate(self.user_id, context)
        logger.info("Stage estimated", stage=stage_info)

        # 4. Analyze user needs
        needs = await self.needs_analyzer.analyze(message, stage_info)
        logger.info("Needs extracted", needs=needs)

        # 5. Generate resource or content recommendations
        recommendations = await self.recommend_engine.generate(needs, stage_info)

        # 6. Build structured prompt
        prompt = self.prompt_builder.build(
            message=message,
            context=context,
            emotion=emotion,
            stage_name=stage_info.get("stage_name", "unknown"),
            needs=needs
        )

        # 7. Generate response using IBM Granite
        try:
            response = await self._generate_response(prompt)
        except Exception as e:
            logger.error("LLM generation failed", error=str(e))
            response = "I'm sorry, something went wrong while generating a response."

        # 8. Optionally ask proactive follow-up question
        proactive_question = await self.proactivity_engine.get_next_question(
            context=context,
            stage_info=stage_info
        )
        if proactive_question:
            response += f"\n\n{proactive_question}"

        # 9. Update context memory
        await ContextMemory.update_context(self.session_id, message, response)

        return {
            "response": response,
            "recommendations": recommendations,
            "stage_info": stage_info,
            "emotion": emotion,
            "needs": needs
        }

    async def _generate_response(self, prompt: str) -> str:
        """Call IBM Granite or Watson LLM to generate a response"""
        result = await self.llm_client.generate(prompt=prompt)
        return result.strip()
