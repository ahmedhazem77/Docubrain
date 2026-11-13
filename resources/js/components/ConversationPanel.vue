<template>
    <section class="detail-panel conversation-panel">
        <div class="section-heading">
            <div>
                <h2>Conversations</h2>
                <p class="muted">Switch between chat threads in this workspace.</p>
            </div>
            <button
                type="button"
                class="btn btn-primary"
                :disabled="creating"
                @click="createConversation"
            >
                {{ creating ? 'Creating…' : 'New conversation' }}
            </button>
        </div>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="loading" class="muted">Loading conversations…</p>

        <div v-else-if="conversations.length === 0" class="empty conversation-empty">
            <p>No conversations yet.</p>
            <button
                type="button"
                class="btn btn-primary"
                :disabled="creating"
                @click="createConversation"
            >
                {{ creating ? 'Creating…' : 'Start a conversation' }}
            </button>
        </div>

        <ul v-else class="conversation-list">
            <li
                v-for="conversation in conversations"
                :key="conversation.id"
                class="conversation-row"
                :class="{ active: conversation.id === selectedConversationId }"
            >
                <button
                    type="button"
                    class="conversation-select"
                    @click="selectConversation(conversation.id)"
                >
                    <strong>{{ conversation.title || 'Untitled conversation' }}</strong>
                    <span class="muted">Updated {{ formatDate(conversation.updated_at) }}</span>
                </button>
                <button
                    type="button"
                    class="btn btn-danger"
                    :disabled="deletingId === conversation.id"
                    @click="deleteConversation(conversation)"
                >
                    {{ deletingId === conversation.id ? 'Deleting…' : 'Delete' }}
                </button>
            </li>
        </ul>
    </section>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import api from '../api/client';

const props = defineProps({
    workspaceId: {
        type: [Number, String],
        required: true,
    },
    selectedConversationId: {
        type: [Number, String, null],
        default: null,
    },
});

const emit = defineEmits(['update:selectedConversationId']);

const conversations = ref([]);
const loading = ref(false);
const creating = ref(false);
const deletingId = ref(null);
const error = ref('');

function formatDate(value) {
    if (!value) return '—';
    return new Date(value).toLocaleString();
}

function selectConversation(id) {
    emit('update:selectedConversationId', id);
}

async function fetchConversations() {
    loading.value = true;
    error.value = '';

    try {
        const { data } = await api.get(`/workspaces/${props.workspaceId}/conversations`);
        conversations.value = Array.isArray(data) ? data : [];

        const stillExists = conversations.value.some(
            (item) => item.id === props.selectedConversationId
        );

        if (stillExists) {
            return;
        }

        if (conversations.value.length > 0) {
            emit('update:selectedConversationId', conversations.value[0].id);
        } else {
            emit('update:selectedConversationId', null);
        }
    } catch (err) {
        error.value = err.response?.data?.message || 'Could not load conversations.';
        conversations.value = [];
        emit('update:selectedConversationId', null);
    } finally {
        loading.value = false;
    }
}

async function createConversation() {
    creating.value = true;
    error.value = '';

    try {
        const { data } = await api.post('/conversations', {
            workspace_id: Number(props.workspaceId),
            title: 'New Conversation',
        });

        conversations.value.unshift(data);
        emit('update:selectedConversationId', data.id);
    } catch (err) {
        error.value = err.response?.data?.message || 'Could not create conversation.';
    } finally {
        creating.value = false;
    }
}

async function deleteConversation(conversation) {
    if (!confirm(`Delete “${conversation.title || 'this conversation'}”?`)) {
        return;
    }

    deletingId.value = conversation.id;
    error.value = '';

    try {
        await api.delete(`/conversations/${conversation.id}`);
        conversations.value = conversations.value.filter((item) => item.id !== conversation.id);

        if (props.selectedConversationId === conversation.id) {
            emit(
                'update:selectedConversationId',
                conversations.value[0]?.id ?? null
            );
        }
    } catch (err) {
        error.value = err.response?.data?.message || 'Could not delete conversation.';
    } finally {
        deletingId.value = null;
    }
}

watch(
    () => props.workspaceId,
    () => {
        fetchConversations();
    }
);

onMounted(fetchConversations);
</script>
