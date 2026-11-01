from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import memory
from ..config import settings

router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=300)
    limit: int = Field(default=5, ge=1, le=20)


@router.post("/memory/search")
def search_memory(request: SearchRequest):
    try:
        results = memory.search(settings.SECOND_BRAIN_ROOT, request.query, request.limit)
    except memory.MemoryUnavailable as exc:
        raise HTTPException(503, str(exc)) from None
    return {"results": results, "processing": "local_only", "external_delegation": False}
