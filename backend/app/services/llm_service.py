"""LLM service factory. Creates the appropriate provider and builds the RAG chain."""

import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from app.services.providers import Provider, create_fallback_provider, create_provider
from app.exceptions import ProviderNotConfiguredError

logger = logging.getLogger("semantic_search")

SEARCH_PROMPT = """\
Voce e um assistente que responde perguntas com base no contexto fornecido abaixo.

CONTEXTO:
{contexto}

INSTRUCOES:
1. Use APENAS as informacoes presentes no CONTEXTO para formular sua resposta.
2. Responda SEMPRE em portugues brasileiro, independente do idioma da pergunta.
3. Responda em linguagem natural, de forma clara e direta.
4. Nunca responda em formato JSON, listas de bullet points ou codigo.
5. Nunca invente informacoes ou use conhecimento externo ao CONTEXTO.
6. Se a pergunta pedir um resumo, visao geral ou perguntar sobre o que se trata o conteudo, sintetize os temas e assuntos presentes no CONTEXTO.
7. Se houver qualquer trecho no CONTEXTO relacionado a pergunta, use-o para responder. Extraia o maximo de informacao relevante.
8. SOMENTE responda "Nao tenho informacoes necessarias para responder sua pergunta." quando a pergunta for sobre um assunto COMPLETAMENTE ausente do CONTEXTO (ex: culinaria, esportes, geografia, se o CONTEXTO nao menciona nada disso).

PERGUNTA DO USUARIO:
{pergunta}

RESPOSTA:"""


class LLMService:
    """Factory that creates the correct provider and builds the RAG chain.

    Consumers receive this service ready to use and call ask(), build_chain()
    or get_provider_name() without knowing which provider is behind it.
    """

    def __init__(self):
        self._provider: Provider | None = None
        self._fallback_provider: Provider | None = None
        self._chain = None

    def _get_provider(self) -> Provider:
        """Create and cache the primary provider."""
        if self._provider is not None:
            return self._provider

        self._provider = create_provider()
        logger.info("[llm] Primary provider: %s", self._provider.get_provider_name())
        return self._provider

    def _get_fallback_provider(self) -> Provider | None:
        """Create and cache the fallback provider if both APIs are configured."""
        if self._fallback_provider is not None:
            return self._fallback_provider

        self._fallback_provider = create_fallback_provider()
        if self._fallback_provider:
            logger.info(
                "[llm] Fallback provider: %s",
                self._fallback_provider.get_provider_name(),
            )
        return self._fallback_provider

    def get_provider_name(self) -> str:
        """Return human-readable name of the active LLM provider."""
        try:
            return self._get_provider().get_provider_name()
        except ProviderNotConfiguredError:
            return "None"

    def build_chain(self):
        """Build LangChain chain with prompt, LLM and optional fallback."""
        if self._chain is not None:
            return self._chain

        prompt = PromptTemplate(
            input_variables=["contexto", "pergunta"],
            template=SEARCH_PROMPT,
        )

        primary = self._get_provider()
        chain = prompt | primary.get_llm() | StrOutputParser()

        fallback = self._get_fallback_provider()
        if fallback:
            fallback_chain = prompt | fallback.get_llm() | StrOutputParser()
            chain = chain.with_fallbacks([fallback_chain])

        self._chain = chain
        logger.info("[llm] Chain built with provider: %s", primary.get_provider_name())
        return self._chain

    def ask(self, context: str, question: str) -> str:
        """Invoke the chain with context and question, return the answer."""
        chain = self.build_chain()
        return chain.invoke({"contexto": context, "pergunta": question})


llm_service = LLMService()
