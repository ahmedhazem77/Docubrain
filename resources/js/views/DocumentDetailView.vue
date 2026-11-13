<template>
    <div class="page page-wide">
        <div class="page-header">
            <div>
                <RouterLink class="back-link" :to="backLink">← Back</RouterLink>
                <h1>{{ document?.file_name || 'Document' }}</h1>
                <p class="muted">Preview the PDF or open it in a new tab.</p>
            </div>
            <StatusBadge v-if="document" :status="document.status" />
        </div>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="loading" class="muted">Loading document…</p>

        <template v-else-if="document">
            <section class="detail-panel">
                <div class="preview-toolbar">
                    <div>
                        <h2>File preview</h2>
                        <p class="muted">Served from <code>/api/documents/{{ document.id }}/view</code></p>
                    </div>
                    <div class="row-actions">
                        <button
                            type="button"
                            class="btn btn-primary"
                            :disabled="opening || previewLoading"
                            @click="openInNewTab"
                        >
                            {{ opening ? 'Opening…' : 'Open in new tab' }}
                        </button>
                        <button type="button" class="btn btn-danger" @click="remove">Delete</button>
                    </div>
                </div>

                <p v-if="fileError" class="error">{{ fileError }}</p>
                <p v-else-if="previewLoading" class="muted">Loading PDF preview…</p>

                <div v-else-if="previewUrl" class="pdf-frame-wrap">
                    <iframe
                        class="pdf-frame"
                        :src="previewUrl"
                        :title="document.file_name"
                    ></iframe>
                </div>
            </section>

            <section class="detail-panel">
                <h2>Document details</h2>
                <dl class="detail-grid">
                    <div>
                        <dt>ID</dt>
                        <dd>{{ document.id }}</dd>
                    </div>
                    <div>
                        <dt>File name</dt>
                        <dd>{{ document.file_name }}</dd>
                    </div>
                    <div>
                        <dt>Status</dt>
                        <dd><StatusBadge :status="document.status" /></dd>
                    </div>
                    <div>
                        <dt>Workspace ID</dt>
                        <dd>{{ document.workspace_id }}</dd>
                    </div>
                    <div>
                        <dt>Storage path</dt>
                        <dd class="mono">{{ document.file_path }}</dd>
                    </div>
                    <div>
                        <dt>Uploaded</dt>
                        <dd>{{ formatDate(document.created_at) }}</dd>
                    </div>
                    <div>
                        <dt>Updated</dt>
                        <dd>{{ formatDate(document.updated_at) }}</dd>
                    </div>
                    <div class="full">
                        <dt>Metadata</dt>
                        <dd>
                            <pre class="metadata">{{ formatMetadata(document.metadata) }}</pre>
                        </dd>
                    </div>
                </dl>
            </section>
        </template>
    </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api/client';
import StatusBadge from '../components/StatusBadge.vue';
import { fetchDocumentObjectUrl, openDocumentInNewTab } from '../utils/documentFile';

const route = useRoute();
const router = useRouter();

const document = ref(null);
const loading = ref(true);
const error = ref('');
const previewUrl = ref('');
const previewLoading = ref(false);
const fileError = ref('');
const opening = ref(false);
let pollTimer = null;

const documentId = computed(() => route.params.id);

const backLink = computed(() => {
    if (document.value?.workspace_id) {
        return { name: 'workspace-detail', params: { id: document.value.workspace_id } };
    }
    return { name: 'workspaces' };
});

function formatDate(value) {
    if (!value) return '—';
    return new Date(value).toLocaleString();
}

function formatMetadata(metadata) {
    if (metadata == null || (Array.isArray(metadata) && metadata.length === 0)) {
        return 'None';
    }
    return JSON.stringify(metadata, null, 2);
}

function revokePreview() {
    if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value);
        previewUrl.value = '';
    }
}

function stopPolling() {
    if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
    }
}

function maybeStartPolling() {
    stopPolling();
    if (document.value?.status !== 'pending') {
        return;
    }

    pollTimer = setInterval(async () => {
        try {
            const { data } = await api.get(`/documents/${documentId.value}`);
            document.value = data;
            if (data.status !== 'pending') {
                stopPolling();
            }
        } catch {
            stopPolling();
        }
    }, 2500);
}

async function loadPreview() {
    revokePreview();
    fileError.value = '';
    previewLoading.value = true;

    try {
        previewUrl.value = await fetchDocumentObjectUrl(documentId.value);
    } catch (err) {
        fileError.value = err.message || 'Could not load PDF preview.';
    } finally {
        previewLoading.value = false;
    }
}

async function load() {
    loading.value = true;
    error.value = '';
    stopPolling();
    revokePreview();

    try {
        const { data } = await api.get(`/documents/${documentId.value}`);
        document.value = data;
        maybeStartPolling();
        await loadPreview();
    } catch (err) {
        document.value = null;
        error.value = err.response?.data?.message || 'Could not load document.';
    } finally {
        loading.value = false;
    }
}

async function openInNewTab() {
    opening.value = true;
    fileError.value = '';

    try {
        await openDocumentInNewTab(documentId.value);
    } catch (err) {
        fileError.value = err.message || 'Could not open file.';
    } finally {
        opening.value = false;
    }
}

async function remove() {
    if (!document.value) {
        return;
    }

    if (!confirm(`Delete “${document.value.file_name}”?`)) {
        return;
    }

    try {
        const workspaceId = document.value.workspace_id;
        await api.delete(`/documents/${document.value.id}`);
        router.push({ name: 'workspace-detail', params: { id: workspaceId } });
    } catch (err) {
        error.value = err.response?.data?.message || 'Could not delete document.';
    }
}

watch(documentId, load);
onMounted(load);
onUnmounted(() => {
    stopPolling();
    revokePreview();
});
</script>
