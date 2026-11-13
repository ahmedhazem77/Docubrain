<template>
    <section class="detail-panel share-panel">
        <div class="section-heading">
            <div>
                <h2>Share workspace</h2>
                <p class="muted">Invite users and manage who already has access.</p>
            </div>
        </div>

        <form class="share-form" @submit.prevent="share">
            <label>
                Email
                <input
                    v-model="form.email"
                    type="email"
                    required
                    placeholder="colleague@example.com"
                    autocomplete="email"
                />
            </label>

            <label>
                Role
                <select v-model="form.role" required>
                    <option value="viewer">Viewer — can open documents</option>
                    <option value="editor">Editor — can upload and delete</option>
                </select>
            </label>

            <button class="btn btn-primary" type="submit" :disabled="sharing">
                {{ sharing ? 'Sharing…' : 'Share' }}
            </button>
        </form>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">{{ success }}</p>

        <div class="shared-users">
            <div class="section-heading">
                <h2>Shared with</h2>
                <p class="muted">{{ sharedUsers.length }} user(s)</p>
            </div>

            <p v-if="loadingUsers" class="muted">Loading shared users…</p>
            <p v-else-if="usersError" class="error">{{ usersError }}</p>
            <div v-else-if="sharedUsers.length === 0" class="empty shared-users-empty">
                <p>No one else has access yet.</p>
            </div>
            <ul v-else class="shared-user-list">
                <li v-for="user in sharedUsers" :key="user.id" class="shared-user-row">
                    <div class="shared-user-main">
                        <strong>{{ user.name }}</strong>
                        <span class="muted">{{ user.email }}</span>
                    </div>
                    <span class="role-badge" :class="`role-${user.role}`">
                        {{ formatRole(user.role) }}
                    </span>
                    <button
                        type="button"
                        class="btn btn-danger"
                        :disabled="removingId === user.id"
                        @click="removeUser(user)"
                    >
                        {{ removingId === user.id ? 'Removing…' : 'Remove' }}
                    </button>
                </li>
            </ul>
        </div>
    </section>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue';
import api from '../api/client';

const props = defineProps({
    workspaceId: {
        type: [Number, String],
        required: true,
    },
});

const form = reactive({
    email: '',
    role: 'viewer',
});
const sharing = ref(false);
const error = ref('');
const success = ref('');

const sharedUsers = ref([]);
const loadingUsers = ref(false);
const usersError = ref('');
const removingId = ref(null);

function formatRole(role) {
    const value = role || 'viewer';
    return value.charAt(0).toUpperCase() + value.slice(1);
}

function formatErrors(data) {
    if (data?.errors) {
        return Object.values(data.errors).flat().join(' ');
    }
    return data?.message || 'Could not share workspace.';
}

async function fetchSharedUsers() {
    loadingUsers.value = true;
    usersError.value = '';

    try {
        const { data } = await api.get(`/workspaces/${props.workspaceId}/shared-users`);
        sharedUsers.value = Array.isArray(data) ? data : [];
    } catch (err) {
        usersError.value = err.response?.data?.message || 'Could not load shared users.';
        sharedUsers.value = [];
    } finally {
        loadingUsers.value = false;
    }
}

async function share() {
    sharing.value = true;
    error.value = '';
    success.value = '';

    try {
        const { data } = await api.post(`/workspaces/${props.workspaceId}/share`, {
            email: form.email,
            role: form.role,
        });

        const name = data.user?.name || form.email;
        const role = data.role || form.role;
        success.value = `Shared with ${name} as ${role}.`;
        form.email = '';
        form.role = 'viewer';
        await fetchSharedUsers();
    } catch (err) {
        error.value = formatErrors(err.response?.data);
    } finally {
        sharing.value = false;
    }
}

async function removeUser(user) {
    if (!confirm(`Remove ${user.name} (${user.email}) from this workspace?`)) {
        return;
    }

    removingId.value = user.id;
    usersError.value = '';
    success.value = '';

    try {
        const { data } = await api.delete(
            `/workspaces/${props.workspaceId}/shared-users/${user.id}`
        );
        sharedUsers.value = sharedUsers.value.filter((item) => item.id !== user.id);
        success.value = data.message || `${user.name} was removed.`;
    } catch (err) {
        usersError.value = err.response?.data?.message || 'Could not remove user.';
    } finally {
        removingId.value = null;
    }
}

watch(
    () => props.workspaceId,
    () => {
        fetchSharedUsers();
    }
);

onMounted(fetchSharedUsers);
</script>
