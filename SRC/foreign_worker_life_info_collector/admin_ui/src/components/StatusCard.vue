<script setup>
defineProps({
  card: {
    type: Object,
    required: true,
  },
})

const valueClass = {
  primary: 'text-primary-container',
  secondary: 'text-secondary-container',
  tertiary: 'text-tertiary',
  error: 'text-error',
  ai: 'text-primary',
  neutral: 'text-on-surface',
}
</script>

<template>
  <section class="control-card p-md" :class="card.tone === 'ai' ? 'border-primary/30 bg-primary-container/5' : ''">
    <p class="mb-xs text-label-caps text-on-surface-variant" :class="card.tone === 'ai' ? 'text-primary' : ''">
      {{ card.label }}
    </p>
    <div class="flex items-baseline gap-xs">
      <span class="text-display" :class="valueClass[card.tone]">{{ card.value }}</span>
      <span class="text-[10px] font-bold" :class="card.tone === 'error' || card.tone === 'tertiary' ? 'text-error' : 'text-success'">
        {{ card.delta }}
      </span>
    </div>
  </section>
</template>
