<template>
  <div id="app">
    <div class="content" :style="{ backgroundImage: backgroundUrl ? `url(${backgroundUrl})` : 'none' }">
      <div class="header">
        <HeadIcon v-if="headIconUrl" :url="headIconUrl" />
        <h1>由由的歌单</h1>
      </div>
      <div class="table-container">
        <el-table 
          :data="songs" 
          style="width: 100%" 
          :stripe="true"
          :border="true"
          class="songs-table"
        >
          <el-table-column prop="song_name" label="歌曲名称" width="200" />
          <el-table-column prop="language" label="语言" width="120" />
          <el-table-column prop="singer" label="歌手" width="180" />
          <el-table-column prop="style" label="曲风" width="120" />
          <el-table-column prop="note" label="备注" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import HeadIcon from './components/HeadIcon.vue'

export default {
  name: 'App',
  components: {
    HeadIcon
  },
  setup() {
    const songs = ref([])
    const headIconUrl = ref('/favicon.ico')
    const backgroundUrl = ref('')

    const fetchSongs = async () => {
      try {
        const response = await fetch('/api/youyou/songs/')
        if (response.ok) {
          const data = await response.json()
          songs.value = data
        } else {
          console.error('获取歌曲列表失败，HTTP状态:', response.status)
        }
      } catch (error) {
        console.error('获取歌曲列表失败:', error)
      }
    }

    const fetchSiteSettings = async () => {
      try {
        const response = await fetch('/api/youyou/site-settings/')
        if (response.ok) {
          const data = await response.json()
          console.log('网站设置数据:', data)
          
          // 重置默认值
          headIconUrl.value = '/favicon.ico'
          backgroundUrl.value = ''
          
          // 根据position设置headIcon和background
          data.forEach(setting => {
            if (setting.position === 1) {
              // 在开发环境中使用/public目录下的图片
              // 在生产环境中使用完整的路径
              headIconUrl.value = process.env.NODE_ENV === 'development' ? 
                `/${setting.position}.png` : 
                setting.photoURL || '/favicon.ico'
              console.log('设置headIconUrl为:', headIconUrl.value)
            } else if (setting.position === 2) {
              // 在开发环境中使用/public目录下的图片
              // 在生产环境中使用完整的路径
              backgroundUrl.value = process.env.NODE_ENV === 'development' ? 
                `/${setting.position}.png` : 
                setting.photoURL
              console.log('设置backgroundUrl为:', backgroundUrl.value)
            }
          })
          
          console.log('最终headIconUrl:', headIconUrl.value)
          console.log('最终backgroundUrl:', backgroundUrl.value)
        } else {
          console.error('获取网站设置失败，HTTP状态:', response.status)
          // 设置默认图片
          headIconUrl.value = '/favicon.ico'
        }
      } catch (error) {
        console.error('获取网站设置失败:', error)
        // 设置默认图片
        headIconUrl.value = '/favicon.ico'
      }
    }

    onMounted(() => {
      fetchSongs()
      fetchSiteSettings()
    })

    return {
      songs,
      headIconUrl,
      backgroundUrl
    }
  }
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  min-height: 100vh;
  position: relative;
}

.content {
  padding: 20px;
  background-size: cover;
  background-position: center;
  min-height: 100vh;
  background-color: rgba(255, 255, 255, 0.9);
  background-blend-mode: overlay;
}

.header {
  margin-bottom: 30px;
  padding-top: 30px;
  position: relative;
  text-align: center;
}

.header h1 {
  font-size: 2.5rem;
  color: #333;
  margin: 0;
  text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
  padding-top: 20px;
}

.table-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.songs-table {
  border-radius: 8px;
  overflow: hidden;
}

.songs-table ::v-deep .el-table__header th {
  background-color: #409EFF !important;
  color: white !important;
  font-weight: bold;
  font-size: 16px;
  padding: 12px 0;
}

.songs-table ::v-deep .el-table__row:hover {
  background-color: #f5f7fa;
}

.songs-table ::v-deep .el-table__cell {
  font-size: 14px;
  padding: 8px 0;
}

.songs-table ::v-deep .el-table__header-wrapper {
  border-radius: 8px 8px 0 0;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 2rem;
    padding-top: 120px;
  }
  
  .table-container {
    padding: 10px;
    margin: 0 10px;
  }
  
  .songs-table ::v-deep .el-table__header th {
    font-size: 14px;
  }
}
</style>