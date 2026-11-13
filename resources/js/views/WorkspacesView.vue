<template>
    <div class="page">
        <div class="page-header">
            <div>
                <h1>Workspaces</h1>
                <p class="muted">Owned and shared workspaces.</p>
            </div>
            <button type="button" class="btn btn-primary" @click="openCreate">New workspace</button>
        </div>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="loading" class="muted">Loading workspaces…</p>

        <div v-else-if="workspaces.length === 0" class="empty">
            <p>No workspaces yet. Create one or ask someone to share with you.</p>
        </div>

        <ul v-else class="workspace-list">
            <li v-for="workspace in workspaces" :key="`${workspace.id}-${workspace.role}`" class="workspace-row">
                <div class="workspace-main">
                    <div class="title-row">
                        <strong>{{ workspace.name }}</strong>
                        <span class="role-badge" :class="`role-${workspace.role || 'owner'}`">
                            {{ formatRole(workspace.role) }}
                        </span>
                    </div>
                    <span class="muted">{{ workspace.description || 'No description' }}</span>
                    <span class="muted meta-line">ID {{ workspace.id }} · Updated {{ formatDate(workspace.updated_at) }}</span>
                </div>
                <div class="row-actions">
                    <RouterLink
                        class="btn btn-primary"
                        :to="{ name: 'workspace-detail', params: { id: workspace.id } }"
                    >
                        View
                    </RouterLink>
                    <button
                        v-if="workspace.is_owner"
                        type="button"
                        class="btn btn-ghost"
                        @click="openEdit(workspace)"
                    >
                        Edit
                    </button>
                    <button
                        v-if="workspace.is_owner"
                        type="button"
                        class="btn btn-danger"
                        @click="remove(workspace)"
                    >
                        Delete
                    </button>
                </div>
            </li>
        </ul>

        <div v-if="dialogOpen" class="modal-backdrop" @click.self="closeDialog">
            <form class="modal stack" @submit.prevent="save">
                <h2>{{ editingId ? 'Edit workspace' : 'New workspace' }}</h2>
                <label>
                    Name
                    <input v-model="form.name" type="text" required maxlength="255" />
                </label>
                <label>
                    Description
                    <textarea v-model="form.description" rows="3" placeholder="Optional"></textarea>
                </label>
                <p v-if="dialogError" class="error">{{ dialogError }}</p>
                <div class="row-actions">
                    <button type="button" class="btn btn-ghost" @click="closeDialog">Cancel</button>
                    <button type="submit" class="btn btn-primary" :disabled="saving">
                        {{ saving ? 'Saving…' : 'Save' }}
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import api from '../api/client';

const workspaces = ref([]);
const loading = ref(true);
const error = ref('');
const dialogOpen = ref(false);
const dialogError = ref('');
const saving = ref(false);
const editingId = ref(null);

const form = reactive({
    name: '',
    description: '',
});

function formatDate(value) {
    if (!value) return '—';
    return new Date(value).toLocaleString();
}

function formatRole(role) {
    const value = role || 'owner';
    return value.charAt(0).toUpperCase() + value.slice(1);
}

async function fetchWorkspaces() {
    loading.value = true;
    error.value = '';
    try {
        const { data } = await api.get('/workspaces');
        workspaces.value = Array.isArray(data) ? data : [];
    } catch (err) {
        error.value = err.response?.data?.message || 'Could not load workspaces.';
    } finally {
        loading.value = false;
    }
}

function openCreate() {
    editingId.value = null;
    form.name = '';
    form.description = '';
    dialogError.value = '';
    dialogOpen.value = true;
}

function openEdit(workspace) {
    editingId.value = workspace.id;
    form.name = workspace.name;
    form.description = workspace.description || '';
    dialogError.value = '';
    dialogOpen.value = true;
}

function closeDialog() {
    dialogOpen.value = false;
}

async function save() {
    saving.value = true;
    dialogError.value = '';
    const payload = {
        name: form.name,
        description: form.description || null,
    };

    try {
        if (editingId.value) {
            const { data } = await api.put(`/workspaces/${editingId.value}`, payload);
            const index = workspaces.value.findIndex((w) => w.id === editingId.value && w.is_owner);
            if (index !== -1) {
                workspaces.value[index] = {
                    ...data.workspace,
                    role: 'owner',
                    is_owner: true,
                };
            }
        } else {
            const { data } = await api.post('/workspaces', payload);
            workspaces.value.unshift({
                ...data.workspace,
                role: 'owner',
                is_owner: true,
            });
        }
        closeDialog();
    } catch (err) {
        dialogError.value = err.response?.data?.message || 'Could not save workspace.';
    } finally {
        saving.value = false;
    }
}

async function remove(workspace) {
    if (!confirm(`Delete workspace “${workspace.name}”? Documents inside will be removed.`)) {
        return;
    }

    try {
        await api.delete(`/workspaces/${workspace.id}`);
        workspaces.value = workspaces.value.filter((w) => w.id !== workspace.id);
    } catch (err) {
        error.value = err.response?.data?.message || 'Could not delete workspace.';
    }
}

onMounted(fetchWorkspaces);
</script>
