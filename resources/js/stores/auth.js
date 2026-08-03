import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import api from '../api/client';

export const useAuthStore = defineStore('auth', () => {
    const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));
    const token = ref(localStorage.getItem('token') || null);

    const isAuthenticated = computed(() => Boolean(token.value));

    function persist(nextUser, nextToken) {
        user.value = nextUser;
        token.value = nextToken;
        localStorage.setItem('user', JSON.stringify(nextUser));
        localStorage.setItem('token', nextToken);
    }

    function clear() {
        user.value = null;
        token.value = null;
        localStorage.removeItem('user');
        localStorage.removeItem('token');
    }

    async function register(payload) {
        const { data } = await api.post('/register', payload);
        persist(data.user, data.token);
        return data;
    }

    async function login(payload) {
        const { data } = await api.post('/login', payload);
        persist(data.user, data.token);
        return data;
    }

    async function logout() {
        try {
            await api.post('/logout');
        } catch {
            // Still clear local session if the token is already invalid.
        } finally {
            clear();
        }
    }

    return {
        user,
        token,
        isAuthenticated,
        register,
        login,
        logout,
        clear,
    };
});
