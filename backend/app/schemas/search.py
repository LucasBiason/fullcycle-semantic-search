"""Pydantic schemas for search domain."""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=5000)
    k: int = Field(default=20, ge=1, le=50)


class SearchResponse(BaseModel):
    answer: str
