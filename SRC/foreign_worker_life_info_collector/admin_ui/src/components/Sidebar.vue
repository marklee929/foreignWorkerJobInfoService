<script setup>
import { RouterLink, useRoute } from 'vue-router'
import logoUrl from '../assets/workconnect_logo_fit.png'

const route = useRoute()

defineProps({
  navItems: {
    type: Array,
    required: true,
  },
})

function isNavActive(item) {
  if (item.path === '/') {
    return route.path === '/'
  }
  return route.path === item.path || Boolean(item.children?.some((child) => route.path === child.path))
}

function isChildActive(item) {
  return route.path === item.path
}
</script>

<template>
  <aside class="fixed left-0 top-0 z-50 flex h-screen w-[240px] flex-col border-r border-outline-variant bg-surface">
    <RouterLink class="flex h-[120px] items-center justify-center border-b border-outline-variant px-xs" to="/" aria-label="대시보드">
      <img class="block h-full w-full object-contain object-center" :src="logoUrl" alt="WorkConnect" />
    </RouterLink>

    <nav class="flex-1 px-sm py-md">
      <ul class="space-y-xs">
        <li v-for="item in navItems" :key="item.label">
          <RouterLink
            :to="item.path"
            class="flex items-center gap-sm rounded-lg px-md py-sm text-label-caps transition"
            :class="isNavActive(item) ? 'bg-secondary-container text-white' : 'text-on-surface-variant hover:bg-surface-container-high'"
          >
            <component :is="item.icon" :size="18" />
            <span>{{ item.label }}</span>
          </RouterLink>
          <ul v-if="item.children?.length && isNavActive(item)" class="mt-xs space-y-xxs pl-lg">
            <li v-for="child in item.children" :key="child.label">
              <RouterLink
                :to="child.path"
                class="flex items-center gap-xs rounded-md px-sm py-xs text-label-sm transition"
                :class="isChildActive(child) ? 'bg-primary-container text-white' : 'text-on-surface-variant hover:bg-surface-container-high'"
              >
                <component :is="child.icon" :size="14" />
                <span>{{ child.label }}</span>
              </RouterLink>
            </li>
          </ul>
        </li>
      </ul>
    </nav>

    <div class="border-t border-outline-variant p-md">
      <div class="flex items-center gap-sm">
        <div class="flex h-8 w-8 items-center justify-center rounded-full bg-primary-container text-xs font-bold text-white">A</div>
        <div>
          <p class="text-label-caps">관리자</p>
          <p class="text-[10px] text-on-surface-variant">시스템 관리자</p>
        </div>
      </div>
    </div>
  </aside>
</template>
