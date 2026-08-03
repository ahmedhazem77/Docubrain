<template>
    <span class="status-badge" :class="`status-${status}`">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
    status: {
        type: String,
        required: true,
    },
});

const label = computed(() => {
    const map = {
        pending: 'Pending',
        processed: 'Processed',
        failed: 'Failed',
    };
    return map[props.status] || props.status;
});
</script>
