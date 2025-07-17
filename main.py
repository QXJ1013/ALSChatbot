from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.api import chat, user, profile, query, feedback
from app.core.context_memory import ContextMemory
from app.utils.config import settings
from app.utils.logger import setup_logging

from app.core.prompt_builder import PromptBuilder
from app.utils.ibm_client import IBMClient 

# Set up structured logging
setup_logging()
logger = structlog.get_logger()

# Global singleton instances
prompt_builder: PromptBuilder = None
ibm_client: IBMClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global prompt_builder, ibm_client

    logger.info("🔁 Initializing ALS Semantic Assistant...", version=settings.APP_VERSION)

    # 1. Context memory module
    ContextMemory.initialize()

    # 2. Load and cache prompt templates
    prompt_builder = PromptBuilder(prompt_dir=settings.PROMPT_PATH, language=settings.DEFAULT_LANGUAGE)
    logger.info("✅ PromptBuilder loaded", prompt_templates=prompt_builder.templates.keys())

    # 3. Initialize IBM Watson client (or Granite model endpoint)
    ibm_client = IBMClient(api_key=settings.IBM_API_KEY, base_url=settings.IBM_API_URL)
    logger.info("✅ IBM Client initialized", base_url=settings.IBM_API_URL)

    yield

    logger.info("🧹 Cleaning up resources before shutdown...")
    await ContextMemory.cleanup()
    logger.info("👋 ALS Semantic Assistant shutdown complete.")

# FastAPI application object
app = FastAPI(
    title="ALS Semantic Assistant",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS configuration (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(query.router, prefix="/api/query", tags=["query"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "ALS Semantic Assistant API", "version": settings.APP_VERSION}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
