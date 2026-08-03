<template>
    <div class="auth-page">
        <div class="auth-panel">
            <p class="brand-mark">DocuBrain</p>
            <h1>Create account</h1>
            <p class="muted">Start organizing PDFs into workspaces.</p>

            <form class="stack" @submit.prevent="onSubmit">
                <label>
                    Name
                    <input v-model="form.name" type="text" required maxlength="255" autocomplete="name" />
                </label>
                <label>
                    Email
                    <input v-model="form.email" type="email" required autocomplete="email" />
                </label>
                <label>
                    Password
                    <input
                        v-model="form.password"
                        type="password"
                        required
                        minlength="8"
                        autocomplete="new-password"
                    />
                </label>

                <p v-if="error" class="error">{{ error }}</p>

                <button class="btn btn-primary" type="submit" :disabled="loading">
                    {{ loading ? 'Creating…' : 'Create account' }}
                </button>
            </form>

            <p class="muted footer-link">
                Already registered?
                <RouterLink to="/login">Sign in</RouterLink>
            </p>
        </div>
    </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const router = useRouter();

const form = reactive({
    name: '',
    email: '',
    password: '',
});
const loading = ref(false);
const error = ref('');

function formatErrors(data) {
    if (data?.errors) {
        return Object.values(data.errors).flat().join(' ');
    }
    return data?.message || 'Unable to create account.';
}

async function onSubmit() {
    loading.value = true;
    error.value = '';

    try {
        await auth.register({ ...form });
        router.push({ name: 'workspaces' });
    } catch (err) {
        error.value = formatErrors(err.response?.data);
    } finally {
        loading.value = false;
    }
}
</script>
