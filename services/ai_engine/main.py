import tracing  # noqa: F401  # initialize Phoenix tracing before LangChain imports

import json
import os
import psycopg

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from graph import graph
from tools import document_summarizer_tool

from config import (
    DATABASE_URL,
    llm_client,
    groq_client,
    LLM_MODEL,
    embedding_model
)


tracer = trace.get_tracer(__name__)


app = FastAPI(title="DocuBrain AI Engine")

# Allow the Laravel/Vite frontend (different origin/port) to call RAG endpoints.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



def split_text(text, chunk_size=800, overlap=100):
    separators = ["\n\n", "\n", ". ", " ", ""]

    def recursive_split(text, separators):

        # If the text already fits, return it as one chunk
        if len(text) <= chunk_size:
            return [text]

        # If there are no separators left,
        # split the text directly by character count
        if not separators:
            return [
                text[i:i + chunk_size]
                for i in range(0, len(text), chunk_size)
            ]

        separator = separators[0] # Start with the largest separator (paragraph)

        # Split using the current separator
        if separator == "":
            parts = list(text)
        else:
            parts = text.split(separator)

        chunks = []
        current = ""

        # Build chunks without exceeding chunk_size
        for part in parts:

            candidate = (
                current + separator + part
                if current
                else part
            )

            if len(candidate) <= chunk_size:
                current = candidate

            else:
                if current:
                    chunks.append(current)

                current = part

        # Add the last chunk
        if current:
            chunks.append(current)

        final_chunks = []

        # Recursively split chunks that are still too large
        for chunk in chunks:

            if len(chunk) <= chunk_size:
                final_chunks.append(chunk)

            else:
                final_chunks.extend(
                    recursive_split(
                        chunk,
                        separators[1:]
                    )
                )

        return final_chunks

    # First create the normal chunks
    chunks = recursive_split(text, separators)

    # Add overlap between neighboring chunks
    overlapped_chunks = []

    for i, chunk in enumerate(chunks):

        if i == 0:
            overlapped_chunks.append(chunk)

        else:
            previous = chunks[i - 1]

            overlap_text = previous[-overlap:]

            overlapped_chunks.append(
                overlap_text + chunk
            )

    return overlapped_chunks


def scan_document_for_injection(text: str) -> bool:
    """
    Returns True if the document appears to contain
    a prompt injection attempt.
    """

    response = groq_client.chat.completions.create(
        model="meta-llama/llama-prompt-guard-2-22m",
        messages=[
            {
                "role": "user",
                "content": text
            }
        ]
    )

    security_score = float(
        response.choices[0].message.content
    )

    return security_score >= 0.5


class SearchRequest(BaseModel):
    query: str
    workspace_id: int
    conversation_id: int
    top_k: int = 4


@app.post("/search")
def search(request: SearchRequest):

  #Langgragh security check
    security_result = graph.invoke(
    {
        "query": request.query,
        "workspace_id": request.workspace_id,
        "security_score": 0.0,
        "blocked": False,
        "messages": [
            {
                "role": "user",
                "content": request.query
            }
        ]
    },
    config={
        "configurable": {
            "thread_id": str(request.conversation_id)
        }
    }
)

    if security_result["blocked"]:

        return {
            "error": "Security Policy Violation: Malicious prompt detected.",
            "security_score": security_result["security_score"]
        }

    # 1. Convert the user's question into a 384-dimensional vector
    query_embedding = embedding_model.encode(
        request.query
    ).tolist()

    # 2. Convert the Python list to pgvector format
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

            # 4. Find the most similar chunks
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
                    request.workspace_id,
                    query_embedding_string,
                    request.top_k
                )
            )

            rows = cursor.fetchall()

        # 5. Convert database rows into JSON
        results = []

        for row in rows:

            results.append({
                "chunk_id": row[0],
                "document_id": row[1],
                "page_number": row[2],
                "content": row[3],
                "distance": row[4]
            })

        return {
            "query": request.query,
            "results": results
        }

    finally:
        connection.close()




@app.post("/query/stream")
def query_stream(request: SearchRequest):

    def generate():

        with tracer.start_as_current_span("query_stream") as span:
            span.set_attribute("query", request.query)
            span.set_attribute("workspace_id", request.workspace_id)
            span.set_attribute("conversation_id", request.conversation_id)

            try:

                config = {
                    "configurable": {
                        "thread_id": str(request.conversation_id)
                    }
                }

                graph_input = {
                    "query": request.query,
                    "workspace_id": request.workspace_id,
                    "security_score": 0.0,
                    "blocked": False,
                    "messages": [
                        {
                            "role": "user",
                            "content": request.query
                        }
                    ]
                }

                answer_started = False

                for message, metadata in graph.stream(
                    graph_input,
                    config=config,
                    stream_mode="messages"
                ):

                    # Only stream messages produced by the agent node
                    if metadata.get("langgraph_node") != "agent":
                        continue

                    # Tool-call messages do not contain answer text
                    if not message.content:
                        continue

                    # Content should normally be a string
                    if isinstance(message.content, str):

                        answer_started = True

                        yield f"data: {message.content}\n\n"

                # If the graph produced no answer, check whether
                # the security node blocked the request.
                if not answer_started:

                    state = graph.get_state(config)

                    if state.values.get("blocked"):

                        span.set_attribute("security.blocked", True)
                        span.set_attribute(
                            "security.score",
                            state.values.get("security_score", 0.0),
                        )

                        yield (
                            "data: Security Policy Violation: "
                            "Malicious prompt detected.\n\n"
                        )

                    else:

                        yield (
                            "data: No answer was generated.\n\n"
                        )

                yield "data: [DONE]\n\n"

            except Exception as e:

                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))

                yield f"data: Error: {str(e)}\n\n"
                yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@app.post("/documents/{document_id}/summarize")
def summarize_document(document_id: int):
    result = document_summarizer_tool.invoke({"document_id": document_id})

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {
            "title": "Document summary",
            "summary": result,
            "key_points": [],
        }


@app.get("/")
def root():
    return {
        "message": "DocuBrain AI Engine is running"
    }


# Test endpoint for the embedding model
@app.get("/test-embedding")
def test_embedding():

    text = "What is consistency in distributed systems?"

    embedding = embedding_model.encode(text).tolist()

    return {
        "text": text,
        "embedding_dimensions": len(embedding),
        "embedding": embedding
    }


def scan_for_prompt_injection(text: str) -> float:
    """
    Scan the document text in smaller segments because
    Prompt Guard has a limited context window.

    Returns the highest attack score found.
    """

    max_score = 0.0

    # Keep each security scan reasonably small.
    chunk_size = 1200

    for start in range(0, len(text), chunk_size):

        segment = text[start:start + chunk_size]

        response = groq_client.chat.completions.create(
            model="meta-llama/llama-prompt-guard-2-22m",
            messages=[
                {
                    "role": "user",
                    "content": segment
                }
            ]
        )

        score = float(
            response.choices[0].message.content
        )

        max_score = max(max_score, score)

    return max_score

@app.post("/process-document")
async def process_document(
    file: UploadFile = File(...),
    document_id: int = Form(...),
    workspace_id: int = Form(...)
):

    # 1. Connect to PostgreSQL
    connection = psycopg.connect(DATABASE_URL)

    try:

        # 2. Verify the document
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT id
                FROM documents
                WHERE id = %s
                AND workspace_id = %s
                """,
                (document_id, workspace_id)
            )

            document = cursor.fetchone()

            if document is None:
                return {
                    "error": "Document does not belong to this workspace"
                }

        # 3. Read the PDF
        reader = PdfReader(file.file)

        # 4. Extract text from ALL pages first
        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text() or ""

            pages.append({
                "page_number": page_number,
                "text": text
            })

        # Combine all extracted text
        full_text = "\n".join(
            page["text"]
            for page in pages
        )

        
        # SECURITY GUARDRAIL
        security_score = scan_for_prompt_injection(full_text)

        if security_score >= 0.5:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE documents
                    SET status = %s
                    WHERE id = %s
                    """,
                    (
                        "flagged_security_risk",
                        document_id
                    )
                )

            connection.commit()

            return {
                "message": "Document blocked by security guardrail",
                "document_id": document_id,
                "status": "flagged_security_risk",
                "security_score": security_score
            }
        

        # 5. Create chunks
        chunks = []

        for page in pages:

            page_number = page["page_number"]
            text = page["text"]

            # Split page into chunks
            page_chunks = split_text(text)

            # Create embedding for every chunk
            for chunk in page_chunks:

                embedding = (
                    embedding_model
                    .encode(chunk)
                    .tolist()
                )

                # Convert Python list into
                # PostgreSQL vector format
                embedding_string = (
                    "["
                    + ",".join(
                        str(value)
                        for value in embedding
                    )
                    + "]"
                )

                chunks.append({
                    "page_number": page_number,
                    "content": chunk,
                    "embedding": embedding_string
                })

        # 6. Remove old chunks
        #    if document was processed before
        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM document_chunks
                WHERE document_id = %s
                """,
                (document_id,)
            )

        # 7. Save chunks in PostgreSQL
        with connection.cursor() as cursor:

            for chunk in chunks:

                cursor.execute(
                    """
                    INSERT INTO document_chunks
                    (
                        document_id,
                        workspace_id,
                        content,
                        page_number,
                        embedding
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s::vector
                    )
                    """,
                    (
                        document_id,
                        workspace_id,
                        chunk["content"],
                        chunk["page_number"],
                        chunk["embedding"]
                    )
                )

        # 8. Save everything
        connection.commit()

        return {
            "message": "Document processed successfully",
            "filename": file.filename,
            "document_id": document_id,
            "workspace_id": workspace_id,
            "total_pages": len(reader.pages),
            "total_chunks": len(chunks)
        }

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()