import api from '../api/client';

async function messageFromBlob(blob) {
    try {
        const text = await blob.text();
        const data = JSON.parse(text);
        return data.message || 'Could not open file.';
    } catch {
        return 'Could not open file.';
    }
}

/**
 * Fetches a document PDF with the Sanctum Bearer token and returns an object URL.
 * Caller must revoke the URL with URL.revokeObjectURL when done.
 */
export async function fetchDocumentObjectUrl(documentId) {
    try {
        const response = await api.get(`/documents/${documentId}/view`, {
            responseType: 'blob',
        });

        const contentType = response.headers['content-type'] || '';
        if (contentType.includes('application/json')) {
            throw new Error(await messageFromBlob(response.data));
        }

        return URL.createObjectURL(response.data);
    } catch (err) {
        if (err.response?.data instanceof Blob) {
            throw new Error(await messageFromBlob(err.response.data));
        }
        throw new Error(err.message || 'Could not open file.');
    }
}

export async function openDocumentInNewTab(documentId) {
    const url = await fetchDocumentObjectUrl(documentId);
    const tab = window.open(url, '_blank', 'noopener,noreferrer');

    if (!tab) {
        URL.revokeObjectURL(url);
        throw new Error('Pop-up blocked. Allow pop-ups to open the file.');
    }

    // Revoke after the tab has had time to load the blob.
    window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
}
