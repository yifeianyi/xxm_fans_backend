# API请求优化文档

## 问题描述

在访问歌单页面时，发现以下问题：

1. 发送了`/api/songs?limit=1000`请求，给服务器带来巨大带宽压力
2. 发送了两次GET /api/styles/请求，造成不必要的重复请求
3. 发送了两次GET /covers/favicon.ico请求，造成不必要的重复请求

## 问题分析与解决方案

### 问题1: 大量数据请求(limit=1000)

#### 问题分析
通过分析代码和网络请求，发现前端在某些情况下会发送limit=1000的请求，导致服务器返回大量数据，给带宽造成压力。虽然在正常的SongList.vue组件中设置了pageSize为50，但在某些特定条件下可能会发送limit=1000的请求。

#### 解决方案
1. **后端保护**: 在后端API中添加最大limit值限制，防止任何过大的limit值请求
   - 在`main/views.py`的`SongListView`中限制page_size最大为100
   - 在`fansDIY/views.py`的API中同样限制page_size最大为100

2. **前端保护**: 在前端也添加限制，确保不会发送超过100的limit值
   - 在`SongList.vue`的`fetchSongsWithParams`函数中添加limit限制

3. **日志诊断**: 添加日志来诊断重定向问题
   - 在`SongListView`中添加dispatch方法记录请求信息
   - 在Vite配置中添加代理日志

### 问题2: 重复的GET /api/styles/请求

#### 问题分析
在打开歌单页面时，会发送两次GET /api/styles/请求。经过深入分析，这是由于以下原因：
1. 组件在标签切换时可能被重新加载
2. 没有防止重复请求的机制
3. 两个独立的API调用可能在某些情况下被重复触发

#### 解决方案
1. **添加加载状态检查**: 在SongList.vue组件中添加`optionsLoaded`变量来防止重复请求
2. **合并API调用**: 创建`loadOptions`函数使用`Promise.all`同时加载样式和标签数据
3. **简化缓存逻辑**: 使用简单的加载状态检查而不是复杂的缓存机制
4. **保持组件状态**: 保持原有的组件加载逻辑，只添加必要的保护措施

#### 实施细节
1. 添加`optionsLoaded`变量防止重复请求
2. 创建`loadOptions`函数统一处理样式和标签的加载
3. 使用`Promise.all`并行加载样式和标签数据
4. 在`onMounted`钩子中调用`loadOptions`函数

### 问题3: 重复的GET /covers/favicon.ico请求

#### 问题分析
favicon.ico文件被请求了两次，这是由于以下原因：
1. 浏览器默认会请求`/favicon.ico`路径的favicon
2. HTML中明确指定了`/covers/favicon.ico`路径的favicon
3. 两个不同的路径导致了两次请求

#### 解决方案
1. **统一favicon路径**: 将HTML中的favicon引用路径改为`/favicon.ico`
2. **复制favicon文件**: 将favicon.ico文件复制到前端项目的public目录中
3. **添加Django路由**: 添加路由将`/favicon.ico`重定向到`/covers/favicon.ico`
4. **配置Vite**: 确保Vite能正确处理public目录中的favicon.ico文件

## 实施效果

通过以上优化措施：

1. **带宽优化**: 限制了最大limit值，防止过大的数据响应，显著减少了服务器带宽使用
2. **请求优化**: 通过缓存机制消除了重复的API请求，减少了不必要的网络通信
3. **favicon优化**: 统一了favicon路径，消除了重复请求
4. **性能提升**: 减少了服务器负载和前端渲染时间，提升了用户体验

## 后续建议

1. 定期监控API请求，确保优化效果持续有效
2. 考虑实现更完善的缓存策略，如使用localStorage或sessionStorage
3. 在网络条件较差时，可以考虑增加错误重试机制