"""Search controller. Orchestrates semantic search and LLM-powered Q&A."""

from app.services.llm_service import llm_service
from app.services.vector_store_service import vector_store_service

NO_INFO_RESPONSE = "Nao tenho informacoes necessarias para responder sua pergunta."

CONTEXT_SEPARATOR = "\n\n---\n\n"
MAX_CONTEXT_LENGTH = 5000


class SearchController:
    """Orchestrates semantic search: retrieve documents, build context, ask LLM."""

    def __init__(self):
        self.vector_store = vector_store_service
        self.llm = llm_service

    def ask(self, question: str, k: int = 20) -> str:
        """Search for relevant documents and generate an answer using LLM.

        Args:
            question: User's question in natural language.
            k: Number of similar documents to retrieve.

        Returns:
            LLM-generated answer based on retrieved context.
        """
        results = self.vector_store.search_similar(question, k=k)

        if not results:
            return NO_INFO_RESPONSE

        context = self._build_context(results)
        return self.llm.ask(context, question)

    @staticmethod
    def _build_context(
        results: list[tuple], max_length: int = MAX_CONTEXT_LENGTH
    ) -> str:
        """Join page_content of retrieved documents, limited by max_length.

        Results are already sorted by relevance (best first). Chunks are added
        until the total context reaches max_length, ensuring the most relevant
        content is always included.
        """
        parts = []
        current_length = 0

        for doc, _score in results:
            content = doc.page_content
            added_length = len(content) + len(CONTEXT_SEPARATOR)

            if current_length + added_length > max_length and parts:
                break

            parts.append(content)
            current_length += added_length

        return CONTEXT_SEPARATOR.join(parts)
