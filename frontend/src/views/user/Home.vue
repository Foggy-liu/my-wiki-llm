<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold">文物 IP 知识库</h1>
        <div class="flex items-center gap-4">
          <router-link to="/chat" class="text-blue-600 hover:underline">知识问答</router-link>
          <button @click="handleLogout" class="text-gray-600 hover:text-gray-800">退出</button>
        </div>
      </div>
    </header>

    <!-- Content -->
    <div class="max-w-7xl mx-auto px-4 py-8">
      <h2 class="text-2xl font-bold mb-6">Wiki 目录</h2>

      <div class="grid grid-cols-3 gap-6">
        <div
          v-for="cat in categories"
          :key="cat.name"
          class="bg-white p-6 rounded-lg shadow"
        >
          <h3 class="text-lg font-bold mb-2">{{ cat.label }}</h3>
          <p class="text-gray-500 text-sm mb-4">{{ cat.description }}</p>
          <p class="text-2xl font-bold text-blue-600">{{ cat.count }}</p>
          <p class="text-gray-400 text-sm">个页面</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const categories = ref([
  { name: 'entities', label: '实体', description: '具体的历史文物和遗址', count: 0 },
  { name: 'concepts', label: '概念', description: '文化理解和技术方法', count: 0 },
  { name: 'summaries', label: '摘要', description: '文档消化后的摘要', count: 0 },
  { name: 'comparisons', label: '对比', description: '对比分析', count: 0 },
  { name: 'synthesis', label: '综合', description: '综合洞察和创作指南', count: 0 }
])

onMounted(async () => {
  // Could load actual counts from API
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
