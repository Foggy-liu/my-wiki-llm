<template>
  <div class="flex">
    <Sidebar />
    <div class="flex-1 p-8">
      <h2 class="text-2xl font-bold mb-6">Lint 健康检查</h2>

      <!-- Run Lint -->
      <div class="bg-white p-6 rounded-lg shadow mb-6">
        <h3 class="text-lg font-bold mb-4">运行检查</h3>

        <div class="flex items-center gap-4">
          <label class="flex items-center">
            <input type="checkbox" v-model="autoFix" class="mr-2" />
            自动修复问题
          </label>

          <button
            @click="handleLint"
            :disabled="running"
            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {{ running ? '检查中...' : '运行 Lint' }}
          </button>
        </div>
      </div>

      <!-- Report Summary -->
      <div v-if="report" class="bg-white p-6 rounded-lg shadow mb-6">
        <h3 class="text-lg font-bold mb-4">检查报告</h3>

        <div class="grid grid-cols-4 gap-4 mb-6">
          <div class="text-center">
            <p class="text-3xl font-bold">{{ report.total_issues }}</p>
            <p class="text-gray-500">总问题数</p>
          </div>
          <div class="text-center text-red-600">
            <p class="text-3xl font-bold">{{ report.errors }}</p>
            <p class="text-gray-500">错误</p>
          </div>
          <div class="text-center text-yellow-600">
            <p class="text-3xl font-bold">{{ report.warnings }}</p>
            <p class="text-gray-500">警告</p>
          </div>
          <div class="text-center text-green-600">
            <p class="text-3xl font-bold">{{ report.fixed?.length || 0 }}</p>
            <p class="text-gray-500">已修复</p>
          </div>
        </div>

        <div v-if="report.fixed?.length > 0" class="mb-4 p-3 bg-green-50 rounded text-green-700">
          <strong>已自动修复:</strong> {{ report.fixed.join(', ') }}
        </div>
      </div>

      <!-- Issues List -->
      <div v-if="report?.issues?.length > 0" class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-bold mb-4">问题列表</h3>

        <table class="w-full">
          <thead>
            <tr class="text-left text-gray-500 text-sm">
              <th class="pb-2">严重程度</th>
              <th class="pb-2">类型</th>
              <th class="pb-2">页面</th>
              <th class="pb-2">描述</th>
              <th class="pb-2">可自动修复</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(issue, idx) in report.issues" :key="idx" class="border-t">
              <td class="py-2">
                <span
                  :class="{
                    'text-red-600': issue.severity === 'error',
                    'text-yellow-600': issue.severity === 'warning',
                    'text-blue-600': issue.severity === 'info'
                  }"
                >
                  {{ issue.severity }}
                </span>
              </td>
              <td class="py-2">{{ issue.type }}</td>
              <td class="py-2">{{ issue.page }}</td>
              <td class="py-2 text-sm">{{ issue.description }}</td>
              <td class="py-2">{{ issue.auto_fix ? '是' : '否' }}</td>
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

const wikiStore = useWikiStore()

const running = ref(false)
const autoFix = ref(true)
const report = ref(null)

onMounted(async () => {
  await wikiStore.fetchLintReport()
  if (wikiStore.lintReport) {
    report.value = wikiStore.lintReport
  }
})

async function handleLint() {
  running.value = true
  try {
    report.value = await wikiStore.triggerLint(autoFix.value)
  } catch (e) {
    console.error(e)
  } finally {
    running.value = false
  }
}
</script>
