<template>
    <div class="page">
        <div class="page-header">
            <div>
                <RouterLink class="back-link" :to="backLink">← Back</RouterLink>
                <h1>{{ document?.file_name || 'Document' }}</h1>
                <p class="muted">Document details from the API.</p>
            </div>
            <StatusBadge v-if="document" :status="document.status" />
        </div>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="loading" class="muted">Loading document…</p>

        <section v-else-if="document" class="detail-panel">
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

            <div class="row-actions">
                <button type="button" class="btn btn-danger" @click="remove">Delete document</button>
            </div>
        </section>
    </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api/client';
import StatusBadge from '../components/StatusBadge.vue';

const route = useRoute();
const router = useRouter();

const document = ref(null);
const loading = ref(true);
const error = ref('');
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

async function load() {
    loading.value = true;
    error.value = '';
    stopPolling();

    try {
        const { data } = await api.get(`/documents/${documentId.value}`);
        document.value = data;
        maybeStartPolling();
    } catch (err) {
        document.value = null;
        error.value = err.response?.data?.message || 'Could not load document.';
    } finally {
        loading.value = false;
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
onUnmounted(stopPolling);
</script>
