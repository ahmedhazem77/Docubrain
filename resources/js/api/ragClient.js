const RAG_API_URL = (import.meta.env.VITE_RAG_API_URL || '').replace(/\/$/, '');

function authHeaders() {
    const headers = {
        Accept: 'application/json',
        'Content-Type': 'application/json',
    };

    const token = localStorage.getItem('token');
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    return headers;
}

function ensureConfigured() {
    if (!RAG_API_URL) {
        throw new Error('RAG API URL is not configured. Set VITE_RAG_API_URL in .env');
    }
}

async function readErrorMessage(response) {
    try {
        const data = await response.json();
        return data.detail || data.message || `Request failed (${response.status})`;
    } catch {
        return `Request failed (${response.status})`;
    }
}

/**
 * POST /search — returns citation candidates for the workspace query.
 */
export async function searchDocuments({ query, workspaceId, conversationId, topK = 4, signal } = {}) {
    ensureConfigured();

    const response = await fetch(`${RAG_API_URL}/search`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({
            query,
            workspace_id: Number(workspaceId),
            conversation_id: Number(conversationId),
            top_k: topK,
        }),
        signal,
    });

    if (!response.ok) {
        throw new Error(await readErrorMessage(response));
    }

    return response.json();
}

/**
 * POST /query/stream — SSE stream via fetch + ReadableStream.
 * Calls onToken(chunk) for each data event until [DONE].
 */
export async function streamQuery({
    query,
    workspaceId,
    conversationId,
    topK = 4,
    onToken,
    signal,
} = {}) {
    ensureConfigured();

    const response = await fetch(`${RAG_API_URL}/query/stream`, {
        method: 'POST',
        headers: {
            ...authHeaders(),
            Accept: 'text/event-stream',
        },
        body: JSON.stringify({
            query,
            workspace_id: Number(workspaceId),
            conversation_id: Number(conversationId),
            top_k: topK,
        }),
        signal,
    });

    if (!response.ok) {
        throw new Error(await readErrorMessage(response));
    }

    if (!response.body) {
        throw new Error('Streaming is not supported in this browser.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    function processBuffer() {
        const events = buffer.split('\n\n');
        buffer = events.pop() ?? '';

        for (const event of events) {
            if (!event.trim()) {
                continue;
            }

            const lines = event.split('\n');

            for (const line of lines) {
                if (!line.startsWith('data:')) {
                    continue;
                }

                const payload = line.startsWith('data: ')
                    ? line.slice(6)
                    : line.slice(5);

                if (payload === '[DONE]') {
                    return true;
                }

                onToken?.(payload);
            }
        }

        return false;
    }

    while (true) {
        const { done, value } = await reader.read();

        if (value) {
            buffer += decoder.decode(value, { stream: true });
            if (processBuffer()) {
                return;
            }
        }

        if (done) {
            buffer += decoder.decode();
            processBuffer();
            return;
        }
    }
}
export function dedupeCitations(results = []) {
    const seen = new Set();
    const citations = [];

    for (const item of results) {
        const documentId = item.document_id;
        const pageNumber = item.page_number;
        const key = `${documentId}:${pageNumber}`;

        if (documentId == null || pageNumber == null || seen.has(key)) {
            continue;
        }

        seen.add(key);
        citations.push({
            document_id: documentId,
            page_number: pageNumber,
        });
    }

    return citations;
}
