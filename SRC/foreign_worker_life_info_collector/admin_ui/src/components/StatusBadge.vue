<script setup>
import { computed } from 'vue'
import { statusMeta } from '../data/statusCodes'

const props = defineProps({
  code: {
    type: [String, Number],
    default: '',
  },
  variant: {
    type: String,
    default: 'compact',
  },
})

const meta = computed(() => statusMeta(props.code))
const title = computed(() => `${meta.value.label} (${meta.value.code}) - ${meta.value.description}`)
</script>

<template>
  <span
    v-if="variant === 'dot'"
    class="inline-flex h-5 w-5 items-center justify-center"
    :title="title"
    :aria-label="title"
  >
    <span class="block h-3.5 w-3.5 rounded-full ring-2 ring-white" :class="meta.dot"></span>
  </span>
  <span
    v-else
    class="inline-flex min-w-[72px] items-center justify-center gap-xs rounded-full border px-sm py-[2px] text-[10px] font-bold"
    :class="meta.chip"
    :title="title"
  >
    <span class="h-2.5 w-2.5 rounded-full" :class="meta.dot"></span>
    <span v-if="variant !== 'dot-label'" class="truncate">{{ meta.label }}</span>
  </span>
</template>
