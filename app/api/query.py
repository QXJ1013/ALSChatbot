from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.embedding.retriever import SemanticRetriever
from app.utils.auth import get_current_user

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    filters: Optional[dict] = None

class QueryResult(BaseModel):
    content: str
    score: float
    metadata: dict

class QueryResponse(BaseModel):
    results: List[QueryResult]
    query_id: str

@router.post("/search", response_model=QueryResponse)
async def semantic_search(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """语义搜索接口"""
    retriever = SemanticRetriever()
    results = await retriever.search(
        query=request.query,
        top_k=request.top_k,
        filters=request.filters
    )
    
    return QueryResponse(
        results=results,
        query_id=str(uuid.uuid4())
    )