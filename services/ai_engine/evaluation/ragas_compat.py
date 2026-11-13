"""Evaluation-only compatibility shims for RAGAS imports."""

from __future__ import annotations

import sys
from types import ModuleType


def install_ragas_import_compat() -> None:
    """
    RAGAS imports a legacy Vertex AI module that is not present in current
    langchain-community releases. Stub it before importing RAGAS.
    """
    module_name = "langchain_community.chat_models.vertexai"
    if module_name not in sys.modules:
        stub = ModuleType(module_name)

        class ChatVertexAI:  # pragma: no cover - import shim only
            pass

        stub.ChatVertexAI = ChatVertexAI
        sys.modules[module_name] = stub


def load_ragas_evaluator():
    install_ragas_import_compat()

    from datasets import Dataset
    from langchain_groq import ChatGroq
    from ragas import evaluate
    from ragas.embeddings.base import LangchainEmbeddingsWrapper
    from ragas.llms.base import LangchainLLMWrapper
    from ragas.metrics import AnswerRelevancy, context_recall, faithfulness

    from config import GROQ_API_KEY, embedding_model

    class SentenceTransformerEmbeddings:
        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return embedding_model.encode(texts).tolist()

        def embed_query(self, text: str) -> list[float]:
            return embedding_model.encode(text).tolist()

    llm = LangchainLLMWrapper(
        ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=GROQ_API_KEY,
            temperature=0.2,
        )
    )
    embeddings = LangchainEmbeddingsWrapper(SentenceTransformerEmbeddings())
    answer_relevancy = AnswerRelevancy(strictness=1)

    return evaluate, Dataset, faithfulness, answer_relevancy, context_recall, llm, embeddings
