<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold">知识问答</h1>
        <div class="flex items-center gap-4">
          <router-link to="/home" class="text-gray-600 hover:text-gray-800">返回主页</router-link>
          <button @click="handleLogout" class="text-gray-600 hover:text-gray-800">退出</button>
        </div>
      </div>
    </header>

    <!-- Chat Container -->
    <div class="max-w-3xl mx-auto px-4 py-8">
      <div class="bg-white rounded-lg shadow p-6">
        <!-- Messages -->
        <div class="space-y-4 mb-6 max-h-96 overflow-y-auto">
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            :class="msg.role === 'user' ? 'bg-blue-50 ml-auto' : 'bg-gray-50'"
            class="max-w-xs rounded-lg p-3"
          >
            <p class="text-sm">{{ msg.content }}</p>
            <p v-if="msg.sources?.length" class="text-xs text-gray-500 mt-1">
              来源: {{ msg.sources.join(', ') }}
            </p>
          </div>

          <div v-if="loading" class="bg-gray-50 max-w-xs rounded-lg p-3">
            <p class="text-sm text-gray-500">思考中...</p>
          </div>
        </div>

        <!-- Input -->
        <div class="flex gap-2">
          <input
            v-model="question"
            @keyup.enter="handleQuery"
            :disabled="loading"
            placeholder="输入你的问题..."
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            @click="handleQuery"
            :disabled="!question || loading"
            class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            提问
          </button>
        </div>
      </div>

      <!-- History -->
      <div class="mt-6 bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-bold mb-4">历史记录</h3>
        <div v-if="history.length === 0" class="text-gray-500">
          暂无历史记录
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="(item, idx) in history"
            :key="idx"
            class="border-b py-2 cursor-pointer hover:bg-gray-50"
            @click="loadHistoryItem(item)"
          >
            <p class="text-sm font-medium">{{ item.question }}</p>
            <p class="text-xs text-gray-500">{{ item.timestamp }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWikiStore } from '@/stores/wiki'

const router = useRouter()
const authStore = useAuthStore()
const wikiStore = useWikiStore()

const question = ref('')
const messages = ref([])
const loading = ref(false)
const history = ref([])

onMounted(async () => {
  await wikiStore.fetchQueryHistory()
  history.value = wikiStore.queryHistory
})

async function handleQuery() {
  if (!question.value || loading.value) return

  const q = question.value
  messages.value.push({ role: 'user', content: q })
  question.value = ''
  loading.value = true

  try {
    const result = await wikiStore.query(q)
    messages.value.push({
      role: 'assistant',
      content: result.answer,
      sources: result.sources
    })
    await wikiStore.fetchQueryHistory()
    history.value = wikiStore.queryHistory
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: '抱歉，发生了错误。'
    })
  } finally {
    loading.value = false
  }
}

function loadHistoryItem(item) {
  question.value = item.question
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
