<template>
  <div id="app">
    <div class="background" :style="{ backgroundImage: backgroundUrl ? `url(${backgroundUrl})` : 'none' }"></div>
    <div class="content">
      <div class="header">
        <HeadIcon v-if="headIconUrl" :url="headIconUrl" />
        <h1>冰洁的歌单</h1>
      </div>
      <div class="filters-container">
        <div class="filters-wrapper">
          <div class="filters">
            <el-select 
              v-model="selectedLanguage" 
              placeholder="请选择语言" 
              clearable 
              @change="filterSongs"
              class="filter-select"
            >
              <el-option
                v-for="language in languages"
                :key="language"
                :label="language"
                :value="language">
              </el-option>
            </el-select>
            
            <el-select 
              v-model="selectedStyle" 
              placeholder="请选择曲风" 
              clearable 
              @change="filterSongs"
              class="filter-select"
            >
              <el-option
                v-for="style in styles"
                :key="style"
                :label="style"
                :value="style">
              </el-option>
            </el-select>
            
            <div class="search-container">
              <el-input
                v-model="searchText"
                placeholder="搜索歌名或歌手"
                clearable
                @clear="searchSongs"
                @keyup.enter="searchSongs"
                class="search-input"
              >
                <template #append>
                  <el-button icon="Search" @click="searchSongs" />
                </template>
              </el-input>
            </div>
            
            <div class="button-container">
              <el-button @click="resetFilters" type="warning" class="reset-button">重置</el-button>
              <el-button @click="getRandomSong" type="success" class="random-button">盲盒</el-button>
            </div>
          </div>
        </div>
      </div>
      <div class="table-container">
        <el-table 
          :data="filteredSongs" 
          style="width: 100%" 
          :stripe="true"
          :border="true"
          class="songs-table"
        >
          <el-table-column prop="song_name" label="歌曲名称" :width="isMobile ? 120 : 200" />
          <el-table-column prop="language" label="语言" :width="isMobile ? 80 : 120" />
          <el-table-column prop="singer" label="歌手" :width="isMobile ? 120 : 180" />
          <el-table-column prop="style" label="曲风" :width="isMobile ? 80 : 120" />
          <el-table-column prop="note" label="备注" />
        </el-table>
      </div>
    </div>
    
    <!-- 盲盒歌曲弹窗 -->
    <el-dialog
      v-model="showRandomSongDialog"
      title="盲盒歌曲"
      width="500px"
      custom-class="random-song-dialog"
    >
      <div v-if="randomSong" class="random-song-content">
        <h3>{{ randomSong.song_name }}</h3>
        <p>歌手: {{ randomSong.singer }}</p>
        <p>语言: {{ randomSong.language }}</p>
        <p>曲风: {{ randomSong.style }}</p>
        <p v-if="randomSong.note">备注: {{ randomSong.note }}</p>
      </div>
      <div v-else>
        <p>暂无符合条件的歌曲</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRandomSongDialog = false">关闭</el-button>
          <el-button type="primary" @click="getRandomSong">再抽一次</el-button>
        </span>
      </template>
    </el-dialog>
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
    const filteredSongs = ref([])
    const languages = ref([])
    const styles = ref([])
    const selectedLanguage = ref('')
    const selectedStyle = ref('')
    const searchText = ref('')
    const headIconUrl = ref('/favicon.ico')
    const backgroundUrl = ref('')
    const isMobile = ref(window.innerWidth <= 768)
    
    // 盲盒相关
    const showRandomSongDialog = ref(false)
    const randomSong = ref(null)

    // 获取所有语言列表
    const fetchLanguages = async () => {
      try {
        const response = await fetch('/api/bingjie/languages/')
        if (response.ok) {
          const data = await response.json()
          languages.value = data
        } else {
          console.error('获取语言列表失败，HTTP状态:', response.status)
        }
      } catch (error) {
        console.error('获取语言列表失败:', error)
      }
    }

    // 获取所有曲风列表
    const fetchStyles = async () => {
      try {
        const response = await fetch('/api/bingjie/styles/')
        if (response.ok) {
          const data = await response.json()
          styles.value = data
        } else {
          console.error('获取曲风列表失败，HTTP状态:', response.status)
        }
      } catch (error) {
        console.error('获取曲风列表失败:', error)
      }
    }

    const fetchSongs = async () => {
      try {
        const response = await fetch('/api/bingjie/songs/')
        if (response.ok) {
          const data = await response.json()
          songs.value = data
          filteredSongs.value = data
        } else {
          console.error('获取歌曲列表失败，HTTP状态:', response.status)
        }
      } catch (error) {
        console.error('获取歌曲列表失败:', error)
      }
    }

    // 语言筛选和搜索功能
    const filterSongs = async () => {
      try {
        const params = new URLSearchParams()
        if (selectedLanguage.value) {
          params.append('language', selectedLanguage.value)
        }
        if (selectedStyle.value) {
          params.append('style', selectedStyle.value)
        }
        if (searchText.value) {
          params.append('search', searchText.value)
        }
        
        const response = await fetch(`/api/bingjie/songs/?${params.toString()}`)
        if (response.ok) {
          const data = await response.json()
          filteredSongs.value = data
        } else {
          console.error('筛选歌曲列表失败，HTTP状态:', response.status)
        }
      } catch (error) {
        console.error('筛选歌曲列表失败:', error)
      }
    }

    // 搜索功能（与筛选功能合并）
    const searchSongs = async () => {
      filterSongs()
    }

    // 重置筛选条件
    const resetFilters = () => {
      selectedLanguage.value = ''
      selectedStyle.value = ''
      searchText.value = ''
      fetchSongs() // 重新获取所有歌曲
    }
    
    // 获取随机歌曲（盲盒功能）
    const getRandomSong = async () => {
      try {
        const params = new URLSearchParams()
        // 应用当前的筛选条件
        if (selectedLanguage.value) {
          params.append('language', selectedLanguage.value)
        }
        if (selectedStyle.value) {
          params.append('style', selectedStyle.value)
        }
        if (searchText.value) {
          params.append('search', searchText.value)
        }
        
        const response = await fetch(`/api/bingjie/random-song/?${params.toString()}`)
        if (response.ok) {
          const data = await response.json()
          randomSong.value = data
          showRandomSongDialog.value = true
        } else if (response.status === 404) {
          randomSong.value = null
          showRandomSongDialog.value = true
        } else {
          console.error('获取随机歌曲失败，HTTP状态:', response.status)
          randomSong.value = null
          showRandomSongDialog.value = true
        }
      } catch (error) {
        console.error('获取随机歌曲失败:', error)
        randomSong.value = null
        showRandomSongDialog.value = true
      }
    }

    const fetchSiteSettings = async () => {
      try {
        const response = await fetch('/api/bingjie/site-settings/')
        if (response.ok) {
          const data = await response.json()
          console.log('网站设置数据:', data)
          
          // 重置默认值
          headIconUrl.value = '/favicon.ico'
          backgroundUrl.value = ''
          
          // 根据position设置headIcon和background
          data.forEach(setting => {
            if (setting.position === 1) {
              // 统一使用/photos/前缀
              headIconUrl.value = setting.photoURL ? `/photos/${setting.photoURL}` : '/favicon.ico'
              console.log('设置headIconUrl为:', headIconUrl.value)
            } else if (setting.position === 2) {
              // 统一使用/photos/前缀
              backgroundUrl.value = setting.photoURL ? `/photos/${setting.photoURL}` : ''
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

    // 判断是否为移动端设备
    const checkIsMobile = () => {
      return window.innerWidth <= 768
    }
    
    onMounted(() => {
      // 初始化isMobile值
      isMobile.value = checkIsMobile()
      
      fetchSongs()
      fetchLanguages()
      fetchStyles()
      fetchSiteSettings()
      
      // 监听窗口大小变化以更新isMobile值
      window.addEventListener('resize', () => {
        isMobile.value = checkIsMobile()
      })
    })

    return {
      filteredSongs,
      languages,
      styles,
      selectedLanguage,
      selectedStyle,
      searchText,
      headIconUrl,
      backgroundUrl,
      isMobile,
      filterSongs,
      searchSongs,
      resetFilters,
      getRandomSong,
      showRandomSongDialog,
      randomSong
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
  width: 100%;
  overflow-x: hidden;
  margin: 0;
  padding: 0;
}

.background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: -1;
}

.content {
  padding: 0;
  margin: 0;
  width: 100%;
  box-sizing: border-box;
  position: relative;
  z-index: 1;
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

.filters-container {
  max-width: 1200px;
  margin: 0 auto 20px;
  padding: 0 20px;
  width: 100%;
  box-sizing: border-box;
}

.filters-wrapper {
  width: 100%;
  box-sizing: border-box;
}

.filters {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: nowrap;
  background-color: rgba(255, 255, 255, 0.85);
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  width: 100%;
  box-sizing: border-box;
}

.filter-select {
  flex-shrink: 1;
  width: 200px;
  max-width: 30%;
}

.search-container {
  display: flex;
  flex: 1;
  gap: 10px;
  min-width: 0;
  align-items: center;
}

.search-input {
  flex: 1;
  min-width: 0;
}

.reset-button {
  flex-shrink: 0;
  min-width: 80px;
}

.random-button {
  flex-shrink: 0;
  min-width: 80px;
  margin-left: 10px;
}

.table-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  width: 100%;
  box-sizing: border-box;
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

.search-input ::v-deep .el-input-group__append {
  background-color: #409EFF;
  color: white;
  border-color: #409EFF;
}

.random-song-content h3 {
  font-size: 24px;
  margin-bottom: 15px;
  color: #333;
}

.random-song-content p {
  font-size: 16px;
  margin: 8px 0;
  color: #666;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
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
  
  .filters {
    flex-direction: column;
    align-items: stretch;
    flex-wrap: nowrap;
    gap: 10px;
  }
  
  .filter-select {
    width: 100%;
    max-width: none;
    flex-shrink: 1;
  }
  
  .search-container {
    width: 100%;
    flex-direction: column;
    min-width: 0;
    align-items: stretch;
    box-sizing: border-box;
  }
  
  .search-input {
    flex: 1;
    min-width: 0;
    width: 100%;
  }
  
  .reset-button, .random-button {
    width: 48%;
    flex-shrink: 0;
    margin: 10px 0 0 0;
  }
  
  .reset-button {
    margin-right: 2%;
  }
  
  .filters-container {
    padding: 0 10px;
  }
  
  /* 添加按钮容器确保按钮在同一行 */
  .button-container {
    display: flex;
    justify-content: space-between;
    width: 100%;
    gap: 2%;
    box-sizing: border-box;
  }
  
  /* 调整表格列宽使其在移动端更紧凑 */
  .songs-table ::v-deep .el-table__body td {
    padding: 3px 0;
  }
  
  /* 移动端表格列宽调整 */
  .songs-table ::v-deep .el-table__header th:nth-child(1),
  .songs-table ::v-deep .el-table__body td:nth-child(1) {
    width: 100px !important;
    min-width: 100px !important;
  }
  
  .songs-table ::v-deep .el-table__header th:nth-child(2),
  .songs-table ::v-deep .el-table__body td:nth-child(2) {
    width: 60px !important;
    min-width: 60px !important;
  }
  
  .songs-table ::v-deep .el-table__header th:nth-child(3),
  .songs-table ::v-deep .el-table__body td:nth-child(3) {
    width: 100px !important;
    min-width: 100px !important;
  }
  
  .songs-table ::v-deep .el-table__header th:nth-child(4),
  .songs-table ::v-deep .el-table__body td:nth-child(4) {
    width: 60px !important;
    min-width: 60px !important;
  }
}

@media (min-width: 769px) and (max-width: 992px) {
  .filter-select {
    width: 150px;
    max-width: 40%;
    flex-shrink: 1;
  }
  
  .search-container {
    flex: 1;
    min-width: 0;
    align-items: center;
  }
}

@media (min-width: 993px) and (max-width: 1200px) {
  .filter-select {
    width: 180px;
    max-width: 35%;
    flex-shrink: 1;
  }
  
  .search-container {
    flex: 1;
    min-width: 0;
    align-items: center;
  }
}

@media (min-width: 1201px) {
  .filter-select {
    width: 200px;
    max-width: 30%;
    flex-shrink: 1;
  }
  
  .search-container {
    flex: 1;
    min-width: 0;
    align-items: center;
  }
}
</style>