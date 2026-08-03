<template>
    <div class="page">
        <div class="page-header">
            <div>
                <RouterLink class="back-link" to="/workspaces">← Workspaces</RouterLink>
                <h1>{{ workspace?.name || 'Workspace' }}</h1>
                <p class="muted">View workspace details and documents.</p>
            </div>
        </div>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="loading" class="muted">Loading workspace…</p>

        <template v-else-if="workspace">
            <section class="detail-panel">
                <h2>Workspace details</h2>
                <dl class="detail-grid">
                    <div>
                        <dt>ID</dt>
                        <dd>{{ workspace.id }}</dd>
                    </div>
                    <div>
                        <dt>Name</dt>
                        <dd>{{ workspace.name }}</dd>
                    </div>
                    <div class="full">
                        <dt>Description</dt>
                        <dd>{{ workspace.description || 'No description' }}</dd>
                    </div>
                    <div>
                        <dt>Created</dt>
                        <dd>{{ formatDate(workspace.created_at) }}</dd>
                    </div>
                    <div>
                        <dt>Updated</dt>
                        <dd>{{ formatDate(workspace.updated_at) }}</dd>
                    </div>
                </dl>
            </section>

            <section class="upload-panel">
                <h2>Upload PDF</h2>
                <p class="muted">PDF only, max 10 MB. Status starts as pending until the queue finishes.</p>
                <form class="upload-row" @submit.prevent="upload">
                    <input ref="fileInput" type="file" accept="application/pdf,.pdf" required @change="onFileChange" />
                    <button class="btn btn-primary" type="submit" :disabled="uploading || !selectedFile">
                        {{ uploading ? 'Uploading…' : 'Upload' }}
                    </button>
                </form>
                <p v-if="uploadError" class="error">{{ uploadError }}</p>
            </section>

            <div class="section-heading">
                <h2>Documents</h2>
                <p class="muted">{{ documents.length }} file(s)</p>
            </div>

            <div v-if="documents.length === 0" class="empty">
                <p>No documents in this workspace yet.</p>
            </div>

            <ul v-else class="document-list">
                <li v-for="doc in documents" :key="doc.id" class="document-row">
                    <div class="document-main">
                        <strong>{{ doc.file_name }}</strong>
                        <span class="muted">Uploaded {{ formatDate(doc.created_at) }}</span>
                    </div>
                    <StatusBadge :status="doc.status" />
                    <div class="row-actions">
                        <RouterLink
                            class="btn btn-primary"
                            :to="{ name: 'document-detail', params: { id: doc.id } }"
                        >
                            View
                        </RouterLink>
                        <button type="button" class="btn btn-danger" @click="remove(doc)">Delete</button>
                    </div>
                </li>
            </ul>
        </template>
    </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '../api/client';
import StatusBadge from '../components/StatusBadge.vue';

const route = useRoute();
const workspaceId = computed(() => route.params.id);

const workspace = ref(null);
const documents = ref([]);
const loading = ref(true);
const error = ref('');
const selectedFile = ref(null);
const fileInput = ref(null);
const uploading = ref(false);
const uploadError = ref('');

let pollTimer = null;

function formatDate(value) {
    if (!value) return '—';
    return new Date(value).toLocaleString();
}

function onFileChange(event) {
    selectedFile.value = event.target.files?.[0] || null;
    uploadError.value = '';
}

async function fetchWorkspace() {
    const { data } = await api.get(`/workspaces/${workspaceId.value}`);
    workspace.value = data;
}

async function fetchDocuments() {
    const { data } = await api.get(`/workspaces/${workspaceId.value}/documents`);
    documents.value = Array.isArray(data) ? data : [];
    maybeStartPolling();
}

function hasPending() {
    return documents.value.some((doc) => doc.status === 'pending');
}

function stopPolling() {
    if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
    }
}

function maybeStartPolling() {
    if (!hasPending()) {
        stopPolling();
        return;
    }

    if (pollTimer) {
        return;
    }

    pollTimer = setInterval(async () => {
        try {
            const { data } = await api.get(`/workspaces/${workspaceId.value}/documents`);
            documents.value = Array.isArray(data) ? data : [];
            if (!hasPending()) {
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
    workspace.value = null;
    documents.value = [];

    try {
        await Promise.all([fetchWorkspace(), fetchDocuments()]);
    } catch (err) {
        error.value = err.response?.data?.message || 'Could not load workspace.';
    } finally {
        loading.value = false;
    }
}

async function upload() {
    if (!selectedFile.value) {
        return;
    }

    uploading.value = true;
    uploadError.value = '';

    const formData = new FormData();
    formData.append('file', selectedFile.value);

    try {
        const { data } = await api.post(`/workspaces/${workspaceId.value}/documents`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        documents.value.unshift(data.document);
        selectedFile.value = null;
        if (fileInput.value) {
            fileInput.value.value = '';
        }
        maybeStartPolling();
    } catch (err) {
        const payload = err.response?.data;
        if (payload?.errors?.file) {
            uploadError.value = payload.errors.file.join(' ');
        } else {
            uploadError.value = payload?.message || 'Upload failed.';
        }
    } finally {
        uploading.value = false;
    }
}

async function remove(doc) {
    if (!confirm(`Delete “${doc.file_name}”?`)) {
        return;
    }

    try {
        await api.delete(`/documents/${doc.id}`);
        documents.value = documents.value.filter((item) => item.id !== doc.id);
        if (!hasPending()) {
            stopPolling();
        }
    } catch (err) {
        error.value = err.response?.data?.message || 'Could not delete document.';
    }
}

watch(workspaceId, load);
onMounted(load);
onUnmounted(stopPolling);
</script>
