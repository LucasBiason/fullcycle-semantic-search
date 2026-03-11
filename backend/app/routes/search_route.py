"""Search route. Thin layer that delegates to controller."""

from fastapi import APIRouter

from app.controllers.search_controller import SearchController
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(body: SearchRequest) -> SearchResponse:
    """Perform semantic search and return LLM-generated answer."""
    controller = SearchController()
    answer = controller.ask(body.question, k=body.k)
    return SearchResponse(answer=answer)
