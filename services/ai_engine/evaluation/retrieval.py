"""Evaluation-only retrieval mirroring production vector search logic."""

from __future__ import annotations

import json

import psycopg

from config import DATABASE_URL, embedding_model


def evaluation_vector_search(
    query: str,
    workspace_id: int,
    document_id: int,
    top_k: int = 4,
) -> list[dict]:
    """
    Evaluation-only vector search using the same embedding model and pgvector
    cosine distance as vector_search_tool, with an additional document_id filter.
    """
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is required for evaluation retrieval.")

    query_embedding = embedding_model.encode(query).tolist()

    query_embedding_string = (
        "["
        + ",".join(str(value) for value in query_embedding)
        + "]"
    )

    connection = psycopg.connect(DATABASE_URL)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    document_id,
                    page_number,
                    content,
                    embedding <=> %s::vector AS distance
                FROM document_chunks
                WHERE workspace_id = %s
                  AND document_id = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    query_embedding_string,
                    workspace_id,
                    document_id,
                    query_embedding_string,
                    top_k,
                ),
            )
            rows = cursor.fetchall()
    finally:
        connection.close()

    results = []
    for row in rows:
        results.append(
            {
                "chunk_id": row[0],
                "document_id": row[1],
                "page_number": row[2],
                "content": row[3],
                "distance": row[4],
            }
        )

    return results


def contexts_as_strings(results: list[dict]) -> list[str]:
    return [result["content"] for result in results]


def results_as_json(results: list[dict]) -> str:
    return json.dumps(results)
