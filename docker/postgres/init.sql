CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL,
    workspace_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    embedding vector(384)
);

CREATE INDEX IF NOT EXISTS document_chunks_workspace_id_idx
    ON document_chunks (workspace_id);

CREATE INDEX IF NOT EXISTS document_chunks_document_id_idx
    ON document_chunks (document_id);
