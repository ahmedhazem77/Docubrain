from langchain_core.tools import tool
from langchain_groq import ChatGroq
from config import DATABASE_URL, GROQ_API_KEY, embedding_model
import psycopg
import json
from pydantic import BaseModel

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


tracer = trace.get_tracer(__name__)

class DocumentSummary(BaseModel):
    title: str
    summary: str
    key_points: list[str]


summarizer_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    temperature=0.2
)


def resolve_document_id_by_filename(workspace_id: int, file_name: str) -> int | None:
    """
    Resolve a document ID from a workspace-scoped filename lookup.
    """
    connection = psycopg.connect(DATABASE_URL)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM documents
                WHERE workspace_id = %s
                  AND file_name = %s
                LIMIT 1
                """,
                (workspace_id, file_name),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return int(row[0])

    finally:
        connection.close()


@tool
def vector_search_tool(
    query: str,
    workspace_id: int,
    top_k: int = 4
) -> list:
    """
    Search the uploaded PDF chunks for information relevant
    to the user's query within the specified workspace.
    """
    with tracer.start_as_current_span("vector_search") as span:
        span.set_attribute("vector_search.query", query)
        span.set_attribute("vector_search.workspace_id", workspace_id)
        span.set_attribute("vector_search.top_k", top_k)

        try:
            # 1. Create the query embedding
            query_embedding = embedding_model.encode(
                query
            ).tolist()

            # 2. Convert embedding to pgvector format
            query_embedding_string = (
                "["
                + ",".join(
                    str(value)
                    for value in query_embedding
                )
                + "]"
            )

            # 3. Connect to PostgreSQL
            connection = psycopg.connect(DATABASE_URL)

            try:

                with connection.cursor() as cursor:

                    # 4. Search for the most similar chunks
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
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                        """,
                        (
                            query_embedding_string,
                            workspace_id,
                            query_embedding_string,
                            top_k
                        )
                    )

                    rows = cursor.fetchall()

                # 5. Format results for the agent
                results = []

                for row in rows:
                    results.append({
                        "chunk_id": row[0],
                        "document_id": row[1],
                        "page_number": row[2],
                        "content": row[3],
                        "distance": row[4]
                    })

                span.set_attribute("vector_search.result_count", len(results))

                for result in results:
                    span.add_event(
                        "vector_search.retrieved_chunk",
                        attributes={
                            "chunk_id": result["chunk_id"],
                            "document_id": result["document_id"],
                            "page_number": result["page_number"],
                            "content": result["content"],
                        },
                    )

                return json.dumps(results)

            finally:
                connection.close()

        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise

@tool
def workspace_stats_tool(workspace_id: int) -> str:
    """
    Get statistics and metadata about a workspace,
    including document counts and latest upload date.
    """

    connection = psycopg.connect(DATABASE_URL)

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    w.name,
                    COUNT(d.id) AS document_count,
                    COUNT(d.id) FILTER (
                        WHERE d.status = 'processed'
                    ) AS processed_documents,
                    COUNT(d.id) FILTER (
                        WHERE d.status = 'pending'
                    ) AS processing_documents,
                    COUNT(d.id) FILTER (
                        WHERE d.status = 'flagged_security_risk'
                    ) AS security_risk_documents,
                    MAX(d.created_at) AS latest_upload
                FROM workspaces w
                LEFT JOIN documents d
                    ON d.workspace_id = w.id
                WHERE w.id = %s
                GROUP BY w.id, w.name
                """,
                (workspace_id,)
            )

            row = cursor.fetchone()

        if row is None:
            return "Workspace not found."

        return (
            f"Workspace: {row[0]}\n"
            f"Total documents: {row[1]}\n"
            f"Processed documents: {row[2]}\n"
            f"Processing documents: {row[3]}\n"
            f"Security-risk documents: {row[4]}\n"
            f"Latest upload: {row[5]}"
        )

    finally:
        connection.close()


@tool
def document_summarizer_tool(document_id: int) -> str:
    """
    Generate a structured summary for a specific document.
    """

    connection = psycopg.connect(DATABASE_URL)

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    d.file_name,
                    c.page_number,
                    c.content
                FROM documents d
                JOIN document_chunks c
                    ON c.document_id = d.id
                WHERE d.id = %s
                ORDER BY c.page_number, c.id
                """,
                (document_id,)
            )

            rows = cursor.fetchall()

        if not rows:
            return "Document not found or contains no content."

        document_name = rows[0][0]

        max_chars = 12000

        batches = []
        current_batch = []
        current_size = 0

        for row in rows:
            chunk_text = f"Page {row[1]}:\n{row[2]}"

            # If adding this chunk would make the batch too large,
            # finish the current batch first.
            if current_batch and current_size + len(chunk_text) > max_chars:
                batches.append(current_batch)
                current_batch = []
                current_size = 0

            current_batch.append(row)
            current_size += len(chunk_text)

        # Add the final batch
        if current_batch:
            batches.append(current_batch)

        batch_summaries = []

        for batch in batches:
            batch_content = "\n\n".join(
                f"Page {row[1]}:\n{row[2]}"
                for row in batch
            )

            # Keep intermediate summarization requests small
            max_chars = 12000
            batch_content = batch_content[:max_chars]

            prompt = f"""
Summarize the following section of the document.

Document name:
{document_name}

Content:
{batch_content}

Extract the most important information.
Do not use outside knowledge.
"""

            response = summarizer_llm.invoke(prompt)
            batch_summaries.append(response.content)

        # Combine the smaller summaries
        combined_summaries = "\n\n".join(batch_summaries)

        final_prompt = f"""
Create a final structured summary of this document.

Document name:
{document_name}

The following are summaries of different sections
of the document:

{combined_summaries}

Return ONLY valid JSON in exactly this format:

{{
    "title": "A concise title",
    "summary": "A concise overall summary",
    "key_points": [
        "Important point 1",
        "Important point 2",
        "Important point 3"
    ]
}}

Do not include markdown.
Do not include ```json.
Do not use information outside the provided summaries.
"""

        final_response = summarizer_llm.invoke(final_prompt)

        content = final_response.content

        try:
            summary = DocumentSummary.model_validate_json(content)
            return summary.model_dump_json()

        except Exception:
            return json.dumps({
                "title": document_name,
                "summary": content,
                "key_points": []
            })

    finally:
        connection.close()