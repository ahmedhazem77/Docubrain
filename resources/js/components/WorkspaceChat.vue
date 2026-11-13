<template>
    <section class="detail-panel chat-panel">
        <div class="section-heading">
            <div>
                <h2>Ask about documents</h2>
                <p class="muted">Questions are answered from PDFs in this workspace.</p>
            </div>
        </div>

        <div ref="transcriptEl" class="chat-transcript" aria-live="polite">
            <p v-if="loadingHistory" class="muted chat-empty">Loading conversation…</p>
            <p v-else-if="messages.length === 0" class="muted chat-empty">
                Ask a question to search this workspace and stream an answer.
            </p>

            <div
                v-for="message in messages"
                :key="message.id"
                class="chat-message"
                :class="`chat-${message.role}`"
            >
                <div class="chat-label">{{ message.role === 'user' ? 'You' : 'DocuBrain' }}</div>
                <div class="chat-bubble">
                    <p v-if="message.role === 'user'" class="chat-text">{{ message.content }}</p>
                    <p v-else-if="message.streaming && !message.content" class="chat-text">…</p>
                    <div
                        v-else-if="message.role === 'assistant' && message.content"
                        class="chat-text chat-text-markdown"
                        v-html="renderAssistantMarkdown(message.content)"
                    ></div>
                    <p v-else-if="message.role === 'assistant'" class="chat-text"></p>

                    <p v-if="message.streaming" class="muted chat-status">Writing answer…</p>

                    <div v-if="message.citations?.length" class="chat-sources">
                        <strong>Sources:</strong>
                        <ul>
                            <li v-for="(cite, index) in message.citations" :key="`${cite.document_id}-${cite.page_number}-${index}`">
                                Document {{ cite.document_id }} — Page {{ cite.page_number }}
                            </li>
                        </ul>
                    </div>

                    <p v-if="message.persistWarning" class="muted chat-status">{{ message.persistWarning }}</p>
                    <p v-if="message.error" class="error">{{ message.error }}</p>

                    <button
                        v-if="message.error && message.canRetry"
                        type="button"
                        class="btn btn-ghost chat-retry"
                        :disabled="streaming"
                        @click="retry(message)"
                    >
                        Retry
                    </button>
                </div>
            </div>
        </div>

        <form class="chat-form" @submit.prevent="ask">
            <label class="chat-input-label">
                Question
                <textarea
                    v-model="question"
                    rows="3"
                    maxlength="2000"
                    placeholder="Ask something about the PDFs in this workspace…"
                    :disabled="streaming || loadingHistory"
                    @keydown.enter.exact.prevent="ask"
                ></textarea>
            </label>
            <button class="btn btn-primary" type="submit" :disabled="streaming || loadingHistory || !question.trim()">
                {{ streaming ? 'Streaming…' : 'Ask' }}
            </button>
        </form>
    </section>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue';
import api from '../api/client';
import { streamQuery } from '../api/ragClient';
import { renderAssistantMarkdown } from '../utils/renderAssistantMarkdown';

const props = defineProps({
    workspaceId: {
        type: [Number, String],
        required: true,
    },
    conversationId: {
        type: [Number, String],
        required: true,
    },
});

const question = ref('');
const messages = ref([]);
const transcriptEl = ref(null);
const streaming = ref(false);
const loadingHistory = ref(false);
let abortController = null;
let messageSeq = 0;

function nextId() {
    messageSeq += 1;
    return `msg-${Date.now()}-${messageSeq}`;
}

async function scrollToBottom() {
    await nextTick();
    if (transcriptEl.value) {
        transcriptEl.value.scrollTop = transcriptEl.value.scrollHeight;
    }
}

function findMessage(id) {
    return messages.value.find((item) => item.id === id);
}

function mapStoredMessage(message) {
    return {
        id: `db-${message.id}`,
        role: message.role,
        content: message.content,
        citations: message.citations || [],
        streaming: false,
        done: true,
        error: '',
        persistWarning: '',
        canRetry: false,
        retryQuery: '',
    };
}

function saveErrorMessage(err) {
    return err.response?.data?.message || 'Could not save message to history.';
}

async function saveMessage({ role, content, citations = [] }) {
    await api.post(`/conversations/${props.conversationId}/messages`, {
        role,
        content,
        citations,
    });
}

async function loadConversationHistory() {
    if (abortController) {
        abortController.abort();
        abortController = null;
    }

    streaming.value = false;
    loadingHistory.value = true;
    messages.value = [];

    try {
        const { data } = await api.get(`/conversations/${props.conversationId}`);
        messages.value = (data.messages || [])
            .filter((message) => message.role === 'user' || message.role === 'assistant')
            .map(mapStoredMessage);
        await scrollToBottom();
    } catch {
        messages.value = [];
    } finally {
        loadingHistory.value = false;
    }
}

async function ask() {
    const text = question.value.trim();
    if (!text || streaming.value || loadingHistory.value) {
        return;
    }

    question.value = '';
    await runQuestion(text);
}

async function retry(message) {
    if (!message?.retryQuery || streaming.value) {
        return;
    }

    message.canRetry = false;
    await runQuestion(message.retryQuery);
}

async function persistAssistantMessage(assistant) {
    if (!assistant) {
        return;
    }

    try {
        await saveMessage({
            role: 'assistant',
            content: assistant.content,
            citations: assistant.citations || [],
        });
    } catch (err) {
        assistant.persistWarning = saveErrorMessage(err);
    }
}

async function runQuestion(text) {
    if (abortController) {
        abortController.abort();
    }

    abortController = new AbortController();
    const { signal } = abortController;

    const userMessage = {
        id: nextId(),
        role: 'user',
        content: text,
    };

    const assistantId = nextId();
    const assistantMessage = {
        id: assistantId,
        role: 'assistant',
        content: '',
        citations: [],
        streaming: true,
        done: false,
        error: '',
        persistWarning: '',
        canRetry: false,
        retryQuery: text,
    };

    messages.value.push(userMessage, assistantMessage);
    await scrollToBottom();

    try {
        await saveMessage({
            role: 'user',
            content: text,
            citations: [],
        });
    } catch (err) {
        assistantMessage.persistWarning = saveErrorMessage(err);
    }

    streaming.value = true;

    try {
        await streamQuery({
            query: text,
            workspaceId: props.workspaceId,
            conversationId: props.conversationId,
            topK: 4,
            signal,
            onToken(token) {
                const current = findMessage(assistantId);

                if (!current) {
                    return;
                }

                current.content += token;
                scrollToBottom();
            },
        });

        const doneMessage = findMessage(assistantId);
        if (doneMessage) {
            doneMessage.streaming = false;
            doneMessage.done = true;

            if (!doneMessage.content.trim()) {
                doneMessage.content = 'No answer was returned.';
            }

            await persistAssistantMessage(doneMessage);
        }
    } catch (err) {
        if (err?.name === 'AbortError') {
            return;
        }

        const assistant = findMessage(assistantId);
        if (assistant) {
            assistant.streaming = false;
            assistant.done = true;
            assistant.error = err.message || 'Something went wrong.';
            assistant.canRetry = true;

            if (!assistant.content) {
                assistant.content = '';
            }
        }
    } finally {
        streaming.value = false;
        await scrollToBottom();
    }
}

watch(
    () => props.conversationId,
    () => {
        loadConversationHistory();
    },
    { immediate: true }
);
</script>
