<template>
  <div class="flex">
    <Sidebar />
    <div class="flex-1 p-8">
      <h2 class="text-2xl font-bold mb-6">系统概览</h2>

      <div class="grid grid-cols-3 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-gray-500 text-sm">Wiki 页面</h3>
          <p class="text-3xl font-bold">{{ stats.totalPages }}</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-gray-500 text-sm">待处理文件</h3>
          <p class="text-3xl font-bold">{{ stats.pendingFiles }}</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-gray-500 text-sm">Lint 问题</h3>
          <p class="text-3xl font-bold text-red-500">{{ stats.lintIssues }}</p>
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-bold mb-4">最近操作</h3>
        <div v-if="recentOps.length === 0" class="text-gray-500">
          暂无操作记录
        </div>
        <table v-else class="w-full">
          <thead>
            <tr class="text-left text-gray-500 text-sm">
              <th class="pb-2">时间</th>
              <th class="pb-2">操作</th>
              <th class="pb-2">状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="op in recentOps" :key="op.id" class="border-t">
              <td class="py-2">{{ formatTime(op.created_at) }}</td>
              <td class="py-2">{{ op.operation }}</td>
              <td class="py-2">
                <span
                  :class="{
                    'text-green-600': op.status === 'success',
                    'text-red-600': op.status === 'failed'
                  }"
                >
                  {{ op.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '@/components/admin/Sidebar.vue'
import { useWikiStore } from '@/stores/wiki'
import api from '@/api'

const wikiStore = useWikiStore()

const stats = ref({
  totalPages: 0,
  pendingFiles: 0,
  lintIssues: 0
})
const recentOps = ref([])

onMounted(async () => {
  await wikiStore.checkIngestStatus()
  stats.value.pendingFiles = wikiStore.ingestStatus?.pending_count || 0

  try {
    const response = await api.get('/admin/wiki/pages')
    stats.value.totalPages = response.data.length
  } catch (e) {
    console.error(e)
  }

  try {
    await wikiStore.fetchLintReport()
    stats.value.lintIssues = wikiStore.lintReport?.total_issues || 0
  } catch (e) {
    console.error(e)
  }

  try {
    const response = await api.get('/admin/operations/recent')
    recentOps.value = response.data.slice(0, 10)
  } catch (e) {
    console.error(e)
  }
})

function formatTime(time) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}
</script>
