<template>
  <div class="head-icon" v-if="url">
    <img :src="url" alt="Head Icon" @error="handleError" />
  </div>
</template>

<script>
export default {
  name: 'HeadIcon',
  props: {
    url: {
      type: String,
      required: true
    }
  },
  methods: {
    handleError(event) {
      // 如果图片加载失败，使用默认图片
      event.target.src = '/favicon.ico'
    }
  }
}
</script>

<style scoped>
.head-icon {
  position: relative;
  z-index: 1000;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background-color: white;
  padding: 5px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transition: transform 0.3s ease;
  border: 2px solid #409EFF;
  margin: 0 auto;
}

.head-icon:hover {
  transform: scale(1.05);
}

.head-icon img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}
</style>