<template>
    <div class="auth-page">
        <div class="auth-panel">
            <p class="brand-mark">DocuBrain</p>
            <h1>Sign in</h1>
            <p class="muted">Access your workspaces and documents.</p>

            <form class="stack" @submit.prevent="onSubmit">
                <label>
                    Email
                    <input v-model="form.email" type="email" required autocomplete="email" />
                </label>
                <label>
                    Password
                    <input v-model="form.password" type="password" required autocomplete="current-password" />
                </label>

                <p v-if="error" class="error">{{ error }}</p>

                <button class="btn btn-primary" type="submit" :disabled="loading">
                    {{ loading ? 'Signing in…' : 'Sign in' }}
                </button>
            </form>

            <p class="muted footer-link">
                No account?
                <RouterLink to="/register">Create one</RouterLink>
            </p>
        </div>
    </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const form = reactive({
    email: '',
    password: '',
});
const loading = ref(false);
const error = ref('');

async function onSubmit() {
    loading.value = true;
    error.value = '';

    try {
        await auth.login({ ...form });
        const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/workspaces';
        router.push(redirect);
    } catch (err) {
        error.value = err.response?.data?.message || 'Unable to sign in.';
    } finally {
        loading.value = false;
    }
}
</script>
