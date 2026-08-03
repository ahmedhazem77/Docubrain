import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import WorkspacesView from '../views/WorkspacesView.vue';
import WorkspaceDetailView from '../views/WorkspaceDetailView.vue';
import DocumentDetailView from '../views/DocumentDetailView.vue';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            redirect: '/workspaces',
        },
        {
            path: '/login',
            name: 'login',
            component: LoginView,
            meta: { guest: true },
        },
        {
            path: '/register',
            name: 'register',
            component: RegisterView,
            meta: { guest: true },
        },
        {
            path: '/workspaces',
            name: 'workspaces',
            component: WorkspacesView,
            meta: { requiresAuth: true },
        },
        {
            path: '/workspaces/:id',
            name: 'workspace-detail',
            component: WorkspaceDetailView,
            meta: { requiresAuth: true },
        },
        {
            path: '/documents/:id',
            name: 'document-detail',
            component: DocumentDetailView,
            meta: { requiresAuth: true },
        },
    ],
});
router.beforeEach((to) => {
    const auth = useAuthStore();

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
        return { name: 'login', query: { redirect: to.fullPath } };
    }

    if (to.meta.guest && auth.isAuthenticated) {
        return { name: 'workspaces' };
    }

    return true;
});

export default router;
