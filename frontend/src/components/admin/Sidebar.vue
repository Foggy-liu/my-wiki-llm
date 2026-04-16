<template>
  <div class="w-64 bg-gray-800 text-white min-h-screen">
    <div class="p-4">
      <h1 class="text-xl font-bold">管理后台</h1>
    </div>
    <nav class="mt-4">
      <router-link
        to="/admin"
        class="block px-4 py-2 hover:bg-gray-700"
        :class="{ 'bg-gray-700': $route.path === '/admin' }"
      >
        概览
      </router-link>
      <router-link
        to="/admin/ingest"
        class="block px-4 py-2 hover:bg-gray-700"
        :class="{ 'bg-gray-700': $route.path === '/admin/ingest' }"
      >
        Ingest
      </router-link>
      <router-link
        to="/admin/lint"
        class="block px-4 py-2 hover:bg-gray-700"
        :class="{ 'bg-gray-700': $route.path === '/admin/lint' }"
      >
        Lint
      </router-link>
    </nav>
    <div class="absolute bottom-0 w-64 p-4">
      <button
        @click="handleLogout"
        class="w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700"
      >
        退出登录
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
