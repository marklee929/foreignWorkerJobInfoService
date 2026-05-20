<script setup>
defineProps({
  title: {
    type: String,
    default: '',
  },
  rows: {
    type: Array,
    required: true,
  },
  type: {
    type: String,
    default: 'candidate',
  },
})
</script>

<template>
  <section class="control-card overflow-hidden">
    <div v-if="title" class="flex items-center border-b border-outline-variant bg-surface-container-low px-md py-sm">
      <h2 class="text-headline">{{ title }}</h2>
      <div class="ml-auto flex gap-xs">
        <button class="rounded bg-primary-container px-md py-xs text-body-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-50" disabled>대기 항목 실행</button>
        <button class="rounded border border-outline-variant px-md py-xs text-body-sm disabled:cursor-not-allowed disabled:opacity-50" disabled>로그</button>
      </div>
    </div>

    <table class="w-full border-collapse text-left text-body-sm">
      <thead class="sticky top-0 bg-white text-label-caps text-on-surface-variant">
        <tr v-if="type === 'module'">
          <th class="px-md py-sm">모듈</th>
          <th class="px-md py-sm">그룹</th>
          <th class="px-md py-sm">상태</th>
          <th class="px-md py-sm">역할</th>
          <th class="px-md py-sm">실행</th>
          <th class="px-md py-sm">필수</th>
          <th class="px-md py-sm">실패</th>
          <th class="px-md py-sm">제어</th>
        </tr>
        <tr v-else>
          <th class="px-md py-sm">카테고리</th>
          <th class="px-md py-sm">지역</th>
          <th class="px-md py-sm">제목</th>
          <th class="px-md py-sm">출처</th>
          <th class="px-md py-sm">점수</th>
          <th class="px-md py-sm">상태</th>
          <th class="px-md py-sm">위험</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="rows.length === 0" class="h-14 border-t border-outline-variant">
          <td class="px-md text-center text-on-surface-variant" :colspan="type === 'module' ? 8 : 7">
            데이터 없음
          </td>
        </tr>
        <tr v-for="row in rows" :key="row.name || row.title" class="h-10 border-t border-outline-variant hover:bg-surface-container-low">
          <template v-if="type === 'module'">
            <td class="px-md font-bold text-primary">{{ row.name }}</td>
            <td class="px-md"><span class="rounded bg-surface-container px-xs py-[1px] text-[11px]">{{ row.domain }}</span></td>
            <td class="px-md"><span class="inline-block h-2 w-2 rounded-full" :class="row.enabled ? 'bg-success' : 'bg-outline'"></span> {{ row.status }}</td>
            <td class="px-md italic">{{ row.job }}</td>
            <td class="px-md font-mono">{{ row.count }}</td>
            <td class="px-md font-mono" :class="row.required ? 'text-error' : 'text-on-surface-variant'">{{ row.success }}</td>
            <td class="px-md font-mono text-success">{{ row.fail }}</td>
            <td class="px-md"><button class="rounded border border-outline-variant px-xs py-[1px] text-[11px]" disabled>{{ row.enabled ? '준비됨' : '잠김' }}</button></td>
          </template>
          <template v-else>
            <td class="px-md">{{ row.category }}</td>
            <td class="px-md">{{ row.region }}</td>
            <td class="px-md font-bold">{{ row.title }}</td>
            <td class="px-md text-on-surface-variant">{{ row.source }}</td>
            <td class="px-md font-mono font-bold text-success">{{ row.score }}</td>
            <td class="px-md text-on-surface-variant">{{ row.duplicate }}</td>
            <td class="px-md"><span class="rounded bg-primary-fixed px-xs py-[1px] text-[10px] text-primary">{{ row.llama }}</span></td>
          </template>
        </tr>
      </tbody>
    </table>
  </section>
</template>
