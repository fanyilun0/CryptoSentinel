<script setup>
import { ref, computed, onMounted } from 'vue'
import { inject } from '@vercel/analytics'
import MarkdownViewer from './components/MarkdownViewer.vue'

// 注入 Vercel Analytics
inject()

const files = ref([])
const currentFile = ref('')
const currentContent = ref('')
const searchQuery = ref('')
const isDarkMode = ref(false)
const isLoading = ref(false)

// 搜索过滤
const filteredFiles = computed(() => {
  if (!searchQuery.value) return files.value
  const query = searchQuery.value.toLowerCase()
  return files.value.filter(file => 
    file.title.toLowerCase().includes(query)
  )
})

const selectFile = async (file) => {
  if (currentFile.value === file.name) return
  currentFile.value = file.name
  isLoading.value = true
  try {
    const response = await fetch(`/advices/${file.name}`)
    currentContent.value = await response.text()
  } catch (error) {
    console.error('Error loading file:', error)
    currentContent.value = '加载文件时出错'
  } finally {
    isLoading.value = false
  }
}

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.classList.toggle('dark-mode')
}

onMounted(async () => {
  try {
    const response = await fetch('/advices/list.json')
    const data = await response.json()
    files.value = data.files.sort((a, b) => b.name.localeCompare(a.name))
    // 默认选中第一个文件（最新的）
    if (files.value.length > 0) {
      selectFile(files.value[0])
    }
  } catch (error) {
    console.error('Error fetching files:', error)
  }
})
</script>

<template>
  <div class="app-container" :class="{ 'dark': isDarkMode }">
    <div class="sidebar">
      <div class="sidebar-header">
        <div class="header-top">
          <h2>BTC AI 投资建议</h2>

        </div>
        <div class="author-links">
          <a href="https://twitter.com/fanyilun0" target="_blank" rel="noopener noreferrer" title="Twitter">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
            </svg>
          </a>
          <a href="https://github.com/fanyilun0/CryptoSentinel" target="_blank" rel="noopener noreferrer" title="GitHub">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                             <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
          </a>
        </div>
      </div>
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="搜索文档..."
        >
      </div>
      <ul class="file-list">
        <li 
          v-for="file in filteredFiles" 
          :key="file.name"
          :class="{ active: currentFile === file.name }"
          @click="selectFile(file)"
        >
          {{ file.name.replace('.md', '') }}
        </li>
      </ul>
    </div>
    <div class="content">
      <div v-if="isLoading" class="loading">
        加载中...
      </div>
      <MarkdownViewer 
        v-else-if="currentContent" 
        :content="currentContent"
      />
      <div v-else class="no-content">
        请选择要查看的文档
      </div>
    </div>
  </div>
</template>

<style>
:root {
  --bg-color: #ffffff;
  --text-color: #24292e;
  --sidebar-bg: #f5f5f5;
  --border-color: #ddd;
  --hover-color: #e0e0e0;
  --active-color: #e0e0e0;
}

.dark-mode {
  --bg-color: #1a1a1a;
  --text-color: #e0e0e0;
  --sidebar-bg: #2d2d2d;
  --border-color: #404040;
  --hover-color: #404040;
  --active-color: #505050;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.app-container {
  display: flex;
  height: 100vh;
  background-color: var(--bg-color);
  color: var(--text-color);
  overflow: hidden;
}

.sidebar {
  width: 260px;
  background-color: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  overflow: hidden;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.author-links {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.author-links a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  padding: 6px;
  border-radius: 4px;
  transition: background-color 0.2s, transform 0.2s, opacity 0.2s;
  cursor: pointer;
  color: var(--text-color);
  opacity: 0.7;
}

.author-links a:hover {
  background-color: var(--hover-color);
  transform: scale(1.1);
  opacity: 1;
}

.author-links a svg {
  width: 16px;
  height: 16px;
  transition: inherit;
}

.sidebar h2 {
  margin: 0;
  color: var(--text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.theme-toggle {
  background: none;
  border: none;
  font-size: 1.5em;
  cursor: pointer;
  padding: 5px;
  border-radius: 5px;
  transition: background-color 0.2s;
}

.theme-toggle:hover {
  background-color: var(--hover-color);
}

.search-box {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.search-box input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--bg-color);
  color: var(--text-color);
  box-sizing: border-box;
}

.file-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.file-list li {
  padding: 12px 20px;
  text-align: left;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.2s, color 0.2s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
  position: relative;
}

.file-list li:hover {
  background-color: var(--hover-color);
}

.file-list li.active {
  background-color: var(--active-color);
  color: #1976d2;
}

.file-list li.active::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 4px;
  background: #1976d2;
  border-radius: 0 2px 2px 0;
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  position: relative;
  background-color: var(--bg-color);
  width: 1200px;
  min-width: 1200px;
  max-width: 1200px;
  margin: 0 auto;
}

.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.2em;
  color: var(--text-color);
  white-space: nowrap;
}

.no-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--text-color);
  font-size: 1.2em;
  padding: 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .sidebar {
    width: 250px;
    min-width: 250px;
  }
}

@media (max-width: 480px) {
  .app-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    min-width: 100%;
    height: auto;
    max-height: 40vh;
  }
  
  .content {
    height: 60vh;
  }
}
</style>
