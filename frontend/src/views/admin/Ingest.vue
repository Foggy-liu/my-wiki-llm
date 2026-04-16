<template>
  <div class="flex">
    <Sidebar />
    <div class="flex-1 p-8">
      <h2 class="text-2xl font-bold mb-6">Ingest 管理</h2>

      <!-- Upload Section -->
      <div class="bg-white p-6 rounded-lg shadow mb-6">
        <h3 class="text-lg font-bold mb-4">上传文件</h3>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">选择分类</label>
          <select
            v-model="uploadCategory"
            class="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="papers">学术论文</option>
            <option value="articles">网络文章</option>
            <option value="transcripts">会议记录</option>
            <option value="docs">官方文档</option>
            <option value="assets">图片资源</option>
          </select>
        </div>

        <div class="mb-4">
          <input
            type="file"
            @change="handleFileSelect"
            class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>

        <button
          @click="handleUpload"
          :disabled="!selectedFile || uploading"
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {{ uploading ? '上传中...' : '上传' }}
        </button>

        <p v-if="uploadMessage" :class="uploadSuccess ? 'text-green-600' : 'text-red-600'" class="mt-2">
          {{ uploadMessage }}
        </p>
      </div>

      <!-- Pending Files -->
      <div class="bg-white p-6 rounded-lg shadow mb-6">
        <h3 class="text-lg font-bold mb-4">待处理文件 ({{ pendingFiles.length }})</h3>

        <div v-if="pendingFiles.length === 0" class="text-gray-500">
          没有待处理的文件
        </div>
        <ul v-else class="space-y-2">
          <li v-for="file in pendingFiles" :key="file" class="flex justify-between items-center py-2 border-b">
            <span class="text-sm">{{ file }}</span>
          </li>
        </ul>
      </div>

      <!-- Trigger Ingest -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-bold mb-4">触发 Ingest</h3>

        <button
          @click="handleIngest"
          :disabled="pendingFiles.length === 0 || ingesting"
          class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
        >
          {{ ingesting ? '处理中...' : '开始处理' }}
        </button>

        <div v-if="ingestResults.length > 0" class="mt-4">
          <h4 class="font-medium mb-2">处理结果</h4>
          <div v-for="(result, idx) in ingestResults" :key="idx" class="text-sm mb-2 p-2 bg-gray-50 rounded">
            <p><strong>文件:</strong> {{ result.file }}</p>
            <p><strong>状态:</strong> {{ result.status }}</p>
            <p v-if="result.entities_created.length"><strong>创建页面:</strong> {{ result.entities_created.join(', ') }}</p>
            <p v-if="result.error" class="text-red-600">{{ result.error }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '@/components/admin/Sidebar.vue'
import { useWikiStore } from '@/stores/wiki'

const wikiStore = useWikiStore()

const uploadCategory = ref('articles')
const selectedFile = ref(null)
const uploading = ref(false)
const uploadMessage = ref('')
const uploadSuccess = ref(false)

const pendingFiles = ref([])
const ingesting = ref(false)
const ingestResults = ref([])

onMounted(async () => {
  await refreshStatus()
})

async function refreshStatus() {
  const status = await wikiStore.checkIngestStatus()
  pendingFiles.value = status.pending_files || []
}

function handleFileSelect(e) {
  selectedFile.value = e.target.files[0]
}

async function handleUpload() {
  if (!selectedFile.value) return

  uploading.value = true
  uploadMessage.value = ''

  try {
    await wikiStore.uploadFile(selectedFile.value, uploadCategory.value)
    uploadMessage.value = '文件上传成功'
    uploadSuccess.value = true
    selectedFile.value = null
    await refreshStatus()
  } catch (e) {
    uploadMessage.value = e.response?.data?.detail || '上传失败'
    uploadSuccess.value = false
  } finally {
    uploading.value = false
  }
}

async function handleIngest() {
  ingesting.value = true
  ingestResults.value = []

  try {
    const response = await wikiStore.triggerIngest()
    ingestResults.value = response.results || []
    await refreshStatus()
  } catch (e) {
    console.error(e)
  } finally {
    ingesting.value = false
  }
}
</script>
