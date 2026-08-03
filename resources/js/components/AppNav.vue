<template>
    <header class="topbar" v-if="auth.isAuthenticated">
        <RouterLink class="brand" to="/workspaces">DocuBrain</RouterLink>
        <div class="topbar-actions">
            <span class="user-label">{{ auth.user?.name }}</span>
            <button type="button" class="btn btn-ghost" @click="onLogout">Log out</button>
        </div>
    </header>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const router = useRouter();

async function onLogout() {
    await auth.logout();
    router.push({ name: 'login' });
}
</script>
