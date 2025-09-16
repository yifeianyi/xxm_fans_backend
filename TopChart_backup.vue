<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const topSongs = ref([])
const loading = ref(false)
const timeRange = ref('all')
const timeOptions = [
  { label: '全部', value: 'all' },
  { label: '近1月', value: '1m' },
  { label: '近3月', value: '3m' },
  { label: '近1年', value: '1y' },
]

const router = useRouter()
function goToSongList(songName) {
  router.push({ path: '/songs', query: { tab: 'songs', q: songName } })
}

const fetchTopSongs = async () => {
  loading.value = true
  try {
    // 假设后端支持 /api/top_songs?range=xxx
    const res = await axios.get('/api/top_songs', { params: { range: timeRange.value, limit: 15 } })
    topSongs.value = res.data
  } catch (err) {
    topSongs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchTopSongs)

watch(timeRange, fetchTopSongs)

const minCount = computed(() => topSongs.value.length ? Math.min(...topSongs.value.map(s => s.perform_count)) : 0)
const maxCount = computed(() => topSongs.value.length ? Math.max(...topSongs.value.map(s => s.perform_count)) : 1)
</script>

<template>
  <div class="top-chart-container">
    <div class="top-bar">
      <span style="font-weight:bold;font-size:18px;">热歌榜</span>
      <div class="range-select">
        <label v-for="opt in timeOptions" :key="opt.value" class="range-btn">
          <input type="radio" v-model="timeRange" :value="opt.value" />
          {{ opt.label }}
        </label>
      </div>
    </div>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else>
      <div v-if="topSongs.length > 0" class="bar-list">
        <div v-for="(song, idx) in topSongs" :key="song.id" class="bar-item">
          <div class="bar-rank">{{ idx+1 }}</div>
          <div class="bar-label clickable" @click="goToSongList(song.song_name)">{{ song.song_name }}</div>
          <div class="bar-bar">
            <div class="bar-inner" :style="{ width: ((song.perform_count - minCount) / (maxCount - minCount || 1) * 90 + 10) + '%' }"></div>
            <span class="bar-count">{{ song.perform_count }} 次</span>
          </div>
        </div>
      </div>
      <div v-else class="no-data">暂无数据</div>
    </div>
  </div>
</template>

<style scoped>
.top-chart-container {
  max-width: 1200px;
  min-width: 800px;
  min-height: 420px;
  margin: 0 auto;
  padding: 32px;
  background: rgba(255,255,255,0.7) !important;
  border-radius: 18px;
  box-shadow: none;
}
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
}
.range-select {
  display: flex;
  gap: 10px;
}
.range-btn {
  font-size: 14px;
  color: #666;
  margin-right: 8px;
  cursor: pointer;
}
.range-btn input[type="radio"] {
  margin-right: 3px;
}
.bar-list {
  margin-top: 10px;
}
.bar-item {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
}
.bar-rank {
  width: 28px;
  font-size: 18px;
  font-weight: bold;
  color: #fda5c1;
  text-align: right;
  margin-right: 10px;
}
.bar-label {
  width: 120px;
  text-align: left;
  font-size: 15px;
  color: #333;
  margin-right: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bar-label.clickable {
  cursor: pointer;
  color: #409EFF;
  text-decoration: underline;
}
.bar-label.clickable:hover {
  color: #fda5c1;
}
.bar-bar {
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
}
.bar-inner {
  height: 18px;
  background: linear-gradient(90deg, #fda5c1 60%, #fbc2eb 100%);
  border-radius: 9px;
  transition: width 0.5s;
}
.bar-count {
  margin-left: 12px;
  font-size: 14px;
  color: #888;
  min-width: 40px;
}
.loading, .no-data {
  text-align: center;
  color: #888;
  margin: 40px 0;
  font-size: 16px;
}
</style>
