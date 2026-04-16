import { defineStore } from 'pinia'
import { ref } from 'vue'
import { wikiAPI } from '@/api/wiki'

export const useWikiStore = defineStore('wiki', () => {
  const pages = ref([])
  const ingestStatus = ref(null)
  const lintReport = ref(null)
  const queryHistory = ref([])

  async function uploadFile(file, category) {
    return await wikiAPI.uploadFile(file, category)
  }

  async function triggerIngest() {
    return await wikiAPI.triggerIngest()
  }

  async function checkIngestStatus() {
    const response = await wikiAPI.getIngestStatus()
    ingestStatus.value = response.data
    return response.data
  }

  async function triggerLint(autoFix = true) {
    const response = await wikiAPI.triggerLint(autoFix)
    lintReport.value = response.data
    return response.data
  }

  async function fetchLintReport() {
    const response = await wikiAPI.getLintReport()
    lintReport.value = response.data.report
    return response.data
  }

  async function query(question) {
    const response = await wikiAPI.query(question)
    return response.data
  }

  async function fetchQueryHistory() {
    const response = await wikiAPI.getQueryHistory()
    queryHistory.value = response.data.history
    return response.data
  }

  return {
    pages,
    ingestStatus,
    lintReport,
    queryHistory,
    uploadFile,
    triggerIngest,
    checkIngestStatus,
    triggerLint,
    fetchLintReport,
    query,
    fetchQueryHistory
  }
})