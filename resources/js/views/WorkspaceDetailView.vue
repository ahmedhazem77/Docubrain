<template>
    <div class="page">
        <div class="page-header">
            <div>
                <RouterLink class="back-link" to="/workspaces">← Workspaces</RouterLink>
                <h1>{{ workspace?.name || 'Workspace' }}</h1>
                <p class="muted">
                    <span v-if="workspace" class="role-badge" :class="`role-${workspace.role || 'owner'}`">
                        {{ roleLabel }}
                    </span>
                    View workspace details and documents.
                </p>
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
                        <dt>Your role</dt>
                        <dd>{{ roleLabel }}</dd>
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

            <ShareWorkspaceForm v-if="isOwner" :workspace-id="workspace.id" />

            <section v-if="canEdit" class="upload-panel">
                <h2>Upload PDF</h2>
                <p class="muted">PDF only, max 10 MB. Drop a file or choose one manually.</p>

                <div
                    class="drop-zone"
                    :class="{ dragging: isDragging, 'has-file': Boolean(selectedFile) }"
                    @dragenter.prevent="onDragEnter"
                    @dragover.prevent="onDragOver"
                    @dragleave.prevent="onDragLeave"
                    @drop.prevent="onDrop"
                    @click="openFilePicker"
                >
                    <input
                        ref="fileInput"
                        class="file-input"
                        type="file"
                        accept="application/pdf,.pdf"
                        @change="onFileChange"
                        @click.stop
                    />

                    <p class="drop-title">
                        {{ isDragging ? 'Drop PDF to upload' : 'Drag & drop PDF here' }}
                    </p>
                    <p class="muted">
                        {{ selectedFile ? selectedFile.name : 'or click to browse' }}
                    </p>
                </div>

                <div class="upload-row">
                    <button
                        class="btn btn-primary"
                        type="button"
                        :disabled="uploading || !selectedFile"
                        @click="upload"
                    >
                        {{ uploading ? 'Uploading…' : 'Upload' }}
                    </button>
                    <button
                        v-if="selectedFile && !uploading"
                        class="btn btn-ghost"
                        type="button"
                        @click="clearSelection"
                    >
                        Clear
                    </button>
                </div>

                <p v-if="uploadError" class="error">{{ uploadError }}</p>
            </section>

            <p v-else class="muted viewer-note">You have viewer access. You can open files but not upload or delete them.</p>

            <div class="section-heading">
                <h2>Documents</h2>
                <p class="muted">{{ documents.length }} file(s)</p>
            </div>

            <div v-if="documents.length === 0" class="empty">
                <p>No documents in this workspace yet.</p>
            </div>

            <ul v-else class="document-list">
                <li v-for="doc in documents" :key="doc.id" class="document-item">
                    <div class="document-row">
                        <div class="document-main">
                            <strong>{{ doc.file_name }}</strong>
                            <span class="muted">Uploaded {{ formatDate(doc.created_at) }}</span>
                        </div>
                        <StatusBadge :status="doc.status" />
                        <div class="row-actions">
                            <RouterLink
                                class="btn btn-ghost"
                                :to="{ name: 'document-detail', params: { id: doc.id } }"
                            >
                                Details
                            </RouterLink>
                            <button
                                type="button"
                                class="btn btn-ghost"
                                :disabled="summarizingId === doc.id || doc.status !== 'processed'"
                                @click="summarizeDocument(doc)"
                            >
                                {{ summarizingId === doc.id ? 'Summarizing…' : 'Summarize' }}
                            </button>
                            <button
                                type="button"
                                class="btn btn-primary"
                                :disabled="openingId === doc.id"
                                @click="openFile(doc)"
                            >
                                {{ openingId === doc.id ? 'Opening…' : 'Open file' }}
                            </button>
                            <button
                                v-if="canEdit"
                                type="button"
                                class="btn btn-danger"
                                @click="remove(doc)"
                            >
                                Delete
                            </button>
                        </div>
                    </div>

                    <div
                        v-if="summarizingId === doc.id || summaries[doc.id] || summaryErrors[doc.id]"
                        class="summary-panel"
                    >
                        <p v-if="summarizingId === doc.id" class="muted">Generating summary…</p>
                        <p v-else-if="summaryErrors[doc.id]" class="error">{{ summaryErrors[doc.id] }}</p>
                        <template v-else-if="summaries[doc.id]">
                            <h3>{{ summaries[doc.id].title }}</h3>
                            <p class="summary-text">{{ summaries[doc.id].summary }}</p>
                            <div v-if="summaries[doc.id].key_points?.length" class="summary-points">
                                <strong>Key points</strong>
                                <ul>
                                    <li v-for="(point, index) in summaries[doc.id].key_points" :key="index">
                                        {{ point }}
                                    </li>
                                </ul>
                            </div>
                        </template>
                    </div>
                </li>
            </ul>

            <ConversationPanel
                v-model:selected-conversation-id="selectedConversationId"
                :workspace-id="workspace.id"
            />

            <WorkspaceChat
                v-if="selectedConversationId"
                :workspace-id="workspace.id"
                :conversation-id="selectedConversationId"
            />

            <section v-else class="detail-panel chat-panel">
                <p class="muted chat-empty">Create a conversation to start asking questions.</p>
            </section>
        </template>
    </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '../api/client';
import ConversationPanel from '../components/ConversationPanel.vue';
import ShareWorkspaceForm from '../components/ShareWorkspaceForm.vue';
import StatusBadge from '../components/StatusBadge.vue';
import WorkspaceChat from '../components/WorkspaceChat.vue';
import { openDocumentInNewTab } from '../utils/documentFile';

const MAX_BYTES = 10 * 1024 * 1024;

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
const openingId = ref(null);
const isDragging = ref(false);
const selectedConversationId = ref(null);
const summarizingId = ref(null);
const summaries = ref({});
const summaryErrors = ref({});

let pollTimer = null;
let dragDepth = 0;

const isOwner = computed(() => Boolean(workspace.value?.is_owner));
const canEdit = computed(() => {
    const role = workspace.value?.role;
    return role === 'owner' || role === 'editor';
});
const roleLabel = computed(() => {
    const role = workspace.value?.role || 'owner';
    return role.charAt(0).toUpperCase() + role.slice(1);
});

function formatDate(value) {
    if (!value) return '—';
    return new Date(value).toLocaleString();
}

function validatePdf(file) {
    const isPdf =
        file.type === 'application/pdf' ||
        file.name.toLowerCase().endsWith('.pdf');

    if (!isPdf) {
        return 'Only PDF files are allowed.';
    }

    if (file.size > MAX_BYTES) {
        return 'File must be 10 MB or smaller.';
    }

    return '';
}

function openFilePicker() {
    fileInput.value?.click();
}

function clearSelection() {
    selectedFile.value = null;
    uploadError.value = '';
    if (fileInput.value) {
        fileInput.value.value = '';
    }
}

function onFileChange(event) {
    const file = event.target.files?.[0] || null;
    if (!file) {
        selectedFile.value = null;
        return;
    }

    const validationError = validatePdf(file);
    if (validationError) {
        clearSelection();
        uploadError.value = validationError;
        return;
    }

    selectedFile.value = file;
    uploadError.value = '';
}

function onDragEnter() {
    dragDepth += 1;
    isDragging.value = true;
}

function onDragOver() {
    isDragging.value = true;
}

function onDragLeave() {
    dragDepth = Math.max(0, dragDepth - 1);
    if (dragDepth === 0) {
        isDragging.value = false;
    }
}

async function onDrop(event) {
    dragDepth = 0;
    isDragging.value = false;

    const file = event.dataTransfer.files?.[0];
    if (!file) {
        return;
    }

    const validationError = validatePdf(file);
    if (validationError) {
        uploadError.value = validationError;
        return;
    }

    selectedFile.value = file;
    uploadError.value = '';
    await upload();
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
    selectedConversationId.value = null;
    summaries.value = {};
    summaryErrors.value = {};
    summarizingId.value = null;

    try {
        await Promise.all([fetchWorkspace(), fetchDocuments()]);
    } catch (err) {
        error.value = err.response?.data?.message || 'Could not load workspace.';
    } finally {
        loading.value = false;
    }
}

async function upload() {
    if (!selectedFile.value || uploading.value) {
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
        clearSelection();
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

async function openFile(doc) {
    openingId.value = doc.id;
    error.value = '';

    try {
        await openDocumentInNewTab(doc.id);
    } catch (err) {
        error.value = err.message || 'Could not open file.';
    } finally {
        openingId.value = null;
    }
}

async function summarizeDocument(doc) {
    summarizingId.value = doc.id;
    summaryErrors.value = {
        ...summaryErrors.value,
        [doc.id]: '',
    };

    try {
        const { data } = await api.post(`/documents/${doc.id}/summarize`);
        summaries.value = {
            ...summaries.value,
            [doc.id]: data,
        };
    } catch (err) {
        summaries.value = {
            ...summaries.value,
            [doc.id]: null,
        };
        summaryErrors.value = {
            ...summaryErrors.value,
            [doc.id]: err.response?.data?.message || 'Could not summarize document.',
        };
    } finally {
        summarizingId.value = null;
    }
}

async function remove(doc) {
    if (!confirm(`Delete “${doc.file_name}”?`)) {
        return;
    }

    try {
        await api.delete(`/documents/${doc.id}`);
        documents.value = documents.value.filter((item) => item.id !== doc.id);
        const nextSummaries = { ...summaries.value };
        const nextSummaryErrors = { ...summaryErrors.value };
        delete nextSummaries[doc.id];
        delete nextSummaryErrors[doc.id];
        summaries.value = nextSummaries;
        summaryErrors.value = nextSummaryErrors;
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
