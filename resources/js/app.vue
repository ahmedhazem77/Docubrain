<template>
    <div class="app-shell">
        <AppNav />
        <main>
            <RouterView />
        </main>
    </div>
</template>

<script setup>
import AppNav from './components/AppNav.vue';
</script>
