# XXM Fans Home 后端重构任务清单

## 项目信息
- **项目名称**: XXM Fans Home 后端重构
- **开始日期**: 2026-01-08
- **预计完成**: 4周
- **负责人**: 待定

---

## 总体进度

- [x] 第一阶段：合并重复应用（1周）✅ 已完成
- [ ] 第二阶段：拆分main应用（2周）
- [ ] 第三阶段：优化和部署（1周）

---

## 第一阶段：合并重复应用（1周）

### 任务 1.1：创建新的songlist应用
- [x] 创建songlist应用
  ```bash
  python manage.py startapp songlist
  ```
- [x] 配置INSTALLED_APPS，添加songlist应用
- [x] 创建必要的目录结构（admin、management、migrations等）

### 任务 1.2：设计并实现统一的数据模型
- [x] 创建Song模型（统一的歌曲模型）
  - [x] 定义字段：song_name, singer, language, style, note
  - [x] 添加Meta配置（verbose_name, ordering等）
  - [x] 添加__str__方法
- [x] 创建SiteSetting模型（统一的网站设置模型）
  - [x] 定义字段：photo_url, position
  - [x] 添加position字段的选择项
  - [x] 添加Meta配置
  - [x] 添加__str__方法
- [x] 编写并执行迁移文件
  ```bash
  python manage.py makemigrations songlist
  python manage.py migrate
  ```

### 任务 1.3：数据迁移
- [x] 分析bingjie_SongList和youyou_SongList的数据结构
- [x] 编写数据迁移脚本
  - [x] 迁移bingjie_Songs数据到新的Song表
  - [x] 迁移you_Songs数据到新的Song表
  - [x] 迁移bingjie_site_setting数据到新的SiteSetting表
  - [x] 迁移you_site_setting数据到新的SiteSetting表
- [ ] 验证数据完整性
  - [ ] 检查数据数量是否一致
  - [ ] 检查数据内容是否正确
  - [ ] 检查是否有重复数据
- [ ] 备份原始数据

### 任务 1.4：实现视图和URL
- [x] 创建视图函数
  - [x] song_list（歌曲列表）
  - [x] language_list（语言列表）
  - [x] style_list（曲风列表）
  - [x] random_song（随机歌曲）
  - [x] site_settings（网站设置）
- [x] 配置URL路由
  - [x] 创建songlist/urls.py
  - [x] 配置所有API路由
- [x] 保持API兼容性
  - [x] 在xxm_fans_home/urls.py中配置/api/bingjie/路由
  - [x] 在xxm_fans_home/urls.py中配置/api/youyou/路由
  - [x] 确保两个路由指向同一个应用

### 任务 1.5：测试
- [x] 编写单元测试
  - [x] 测试Song模型
  - [x] 测试SiteSetting模型
  - [ ] 测试所有视图函数
- [x] 编写集成测试脚本
  - [x] 测试API兼容性
  - [x] 测试所有API端点
  - [x] 测试数据查询
- [ ] 执行测试
  - [ ] 测试/api/bingjie/songs/
  - [ ] 测试/api/youyou/songs/
  - [ ] 测试所有其他API端点

### 任务 1.6：删除旧应用
- [ ] 备份bingjie_SongList应用
- [ ] 备份youyou_SongList应用
- [ ] 从INSTALLED_APPS中移除bingjie_SongList
- [ ] 从INSTALLED_APPS中移除youyou_SongList
- [ ] 从xxm_fans_home/urls.py中移除旧的路由配置
- [ ] 删除bingjie_SongList目录
- [ ] 删除youyou_SongList目录
- [ ] 删除bingjie_SongList_frontend目录（如果存在）
- [ ] 删除youyou_SongList_frontend目录（如果存在）
- [ ] 更新相关文档

### 任务 1.7：验证阶段
- [ ] 执行数据库迁移
  - [ ] 创建songlist数据库
  - [ ] 执行迁移文件
  - [ ] 验证迁移状态
- [ ] 执行数据迁移
  - [ ] 备份原始数据
  - [ ] 执行迁移脚本
  - [ ] 验证数据完整性
- [ ] 执行API测试
  - [ ] 启动Django服务
  - [ ] 执行测试脚本
  - [ ] 手动测试API端点
- [ ] 验证管理后台
  - [ ] 访问管理后台
  - [ ] 测试数据操作
  - [ ] 验证功能正常

### 注意事项

**执行指南：**
- 详细的执行步骤请参考：`test/phase1/EXECUTION_GUIDE.md`
- 测试脚本位于：`test/phase1/`
- 第一阶段完成报告：`doc/phase1_completion_report.md`

**重要提醒：**
- 执行任何迁移前务必备份数据库
- 建议先在测试环境验证
- 充分测试后再删除旧应用
- 保留回滚方案

---

## 第二阶段：拆分main应用（2周）

### 任务 2.1：创建新应用
- [ ] 创建song_management应用
  ```bash
  python manage.py startapp song_management
  ```
- [ ] 创建data_analytics应用
  ```bash
  python manage.py startapp data_analytics
  ```
- [ ] 创建site_settings应用
  ```bash
  python manage.py startapp site_settings
  ```
- [ ] 配置INSTALLED_APPS，添加所有新应用
- [ ] 创建必要的目录结构（admin、management、migrations等）

### 任务 2.2：迁移模型到song_management
- [ ] 创建Style模型
  - [ ] 定义字段：name, description
  - [ ] 添加unique_together约束
  - [ ] 添加Meta配置
  - [ ] 添加__str__方法
- [ ] 创建Tag模型
  - [ ] 定义字段：name, description
  - [ ] 添加unique_together约束
  - [ ] 添加Meta配置
  - [ ] 添加__str__方法
- [ ] 创建Song模型
  - [ ] 定义字段：song_name, singer, last_performed, perform_count, language
  - [ ] 添加Meta配置和索引
  - [ ] 添加__str__方法
  - [ ] 添加styles属性（property）
  - [ ] 添加tags属性（property）
- [ ] 创建SongRecord模型
  - [ ] 定义字段：song, performed_at, url, notes, cover_url
  - [ ] 添加外键关联到Song
  - [ ] 添加Meta配置
  - [ ] 添加__str__方法
- [ ] 创建SongStyle模型
  - [ ] 定义字段：song, style
  - [ ] 添加外键关联
  - [ ] 添加unique_together约束
  - [ ] 添加Meta配置
  - [ ] 添加__str__方法
- [ ] 创建SongTag模型
  - [ ] 定义字段：song, tag
  - [ ] 添加外键关联
  - [ ] 添加unique_together约束
  - [ ] 添加Meta配置
  - [ ] 添加__str__方法
- [ ] 编写并执行迁移文件

### 任务 2.3：迁移模型到data_analytics
- [ ] 创建WorkStatic模型
  - [ ] 定义字段：platform, work_id, title, author, publish_time, cover_url, is_valid
  - [ ] 添加外键关联到song_management.Song（related_song）
  - [ ] 添加unique_together约束
  - [ ] 添加Meta配置和索引
  - [ ] 添加__str__方法
- [ ] 创建WorkMetricsHour模型
  - [ ] 定义字段：work_static, crawl_time, view_count, like_count, coin_count, favorite_count, danmaku_count, comment_count, session_id, ingest_time
  - [ ] 添加外键关联到WorkStatic
  - [ ] 添加Meta配置和索引
  - [ ] 添加__str__方法
- [ ] 创建CrawlSession模型
  - [ ] 定义字段：source, node_id, start_time, end_time, total_work_count, success_count, fail_count, note
  - [ ] 添加Meta配置
  - [ ] 添加__str__方法
- [ ] 编写并执行迁移文件
- [ ] 删除video_info相关模型（ViewBaseMess, ViewRealTimeInformation）
  - [ ] 确认这些模型与WorkStatic功能重复
  - [ ] 编写迁移脚本删除这些模型
  - [ ] 执行迁移

### 任务 2.4：迁移模型到site_settings
- [ ] 创建SiteSettings模型
  - [ ] 定义字段：favicon, site_title, site_description
  - [ ] 添加时间戳字段（created_at, updated_at）
  - [ ] 添加favicon_url方法
  - [ ] 添加Meta配置
  - [ ] 添加__str__方法
- [ ] 创建Recommendation模型
  - [ ] 定义字段：content, display_order, is_active
  - [ ] 添加多对多字段到song_management.Song（recommended_songs）
  - [ ] 添加时间戳字段（created_at, updated_at）
  - [ ] 添加Meta配置
  - [ ] 添加__str__方法
- [ ] 编写并执行迁移文件

### 任务 2.5：迁移数据
- [ ] 编写数据迁移脚本
  - [ ] 迁移main.Songs数据到song_management.Song
  - [ ] 迁移main.SongRecord数据到song_management.SongRecord
  - [ ] 迁移main.Style数据到song_management.Style
  - [ ] 迁移main.Tag数据到song_management.Tag
  - [ ] 迁移main.SongStyle数据到song_management.SongStyle
  - [ ] 迁移main.SongTag数据到song_management.SongTag
  - [ ] 迁移main.WorkStatic数据到data_analytics.WorkStatic
  - [ ] 迁移main.WorkMetricsHour数据到data_analytics.WorkMetricsHour
  - [ ] 迁移main.CrawlSession数据到data_analytics.CrawlSession
  - [ ] 迁移main.SiteSettings数据到site_settings.SiteSettings
  - [ ] 迁移main.Recommendation数据到site_settings.Recommendation
- [ ] 验证数据完整性
  - [ ] 检查所有表的数据数量
  - [ ] 检查外键关联是否正确
  - [ ] 检查跨应用关联是否正确
  - [ ] 验证WorkStatic与Song的关联

### 任务 2.6：迁移视图到song_management
- [ ] 创建song_management/views.py
  - [ ] 迁移歌曲相关视图（song_list_api, song_detail_api等）
  - [ ] 迁移演唱记录相关视图（song_record_list_api等）
  - [ ] 迁移曲风相关视图（style_list_api等）
  - [ ] 迁移标签相关视图（tag_list_api等）
  - [ ] 迁移排行榜相关视图（top_songs_api等）
  - [ ] 使用DRF的ViewSets或Generic Views重构
- [ ] 创建song_management/urls.py
  - [ ] 配置所有API路由
- [ ] 创建song_management/serializers.py
  - [ ] 创建所有模型的序列化器
  - [ ] 添加验证逻辑
  - [ ] 添加嵌套序列化器（如Song的styles和tags）

### 任务 2.7：迁移视图到data_analytics
- [ ] 创建data_analytics/views.py
  - [ ] 迁移作品相关视图
  - [ ] 迁移指标相关视图
  - [ ] 迁移爬取会话相关视图
  - [ ] 使用DRF的ViewSets或Generic Views重构
- [ ] 创建data_analytics/urls.py
  - [ ] 配置所有API路由
- [ ] 创建data_analytics/serializers.py
  - [ ] 创建所有模型的序列化器
  - [ ] 添加验证逻辑
  - [ ] 添加嵌套序列化器（如WorkStatic的related_song）

### 任务 2.8：迁移视图到site_settings
- [ ] 创建site_settings/views.py
  - [ ] 迁移网站设置相关视图
  - [ ] 迁移推荐语相关视图
  - [ ] 使用DRF的ViewSets或Generic Views重构
- [ ] 创建site_settings/urls.py
  - [ ] 配置所有API路由
- [ ] 创建site_settings/serializers.py
  - [ ] 创建所有模型的序列化器
  - [ ] 添加验证逻辑
  - [ ] 添加嵌套序列化器（如Recommendation的recommended_songs）

### 任务 2.9：迁移Admin配置
- [ ] 创建song_management/admin目录
  - [ ] 创建song_management/admin/__init__.py
  - [ ] 创建song_management/admin/song_admin.py
    - [ ] 创建SongAdmin类
    - [ ] 创建SongRecordAdmin类
    - [ ] 添加批量操作
  - [ ] 创建song_management/admin/style_admin.py
    - [ ] 创建StyleAdmin类
  - [ ] 创建song_management/admin/tag_admin.py
    - [ ] 创建TagAdmin类
  - [ ] 创建song_management/admin/actions.py
    - [ ] 实现批量添加曲风
    - [ ] 实现批量添加标签
    - [ ] 实现其他批量操作
- [ ] 创建data_analytics/admin目录
  - [ ] 创建data_analytics/admin/__init__.py
  - [ ] 创建data_analytics/admin/work_admin.py
    - [ ] 创建WorkStaticAdmin类
    - [ ] 创建WorkMetricsHourAdmin类
  - [ ] 创建data_analytics/admin/crawl_admin.py
    - [ ] 创建CrawlSessionAdmin类
- [ ] 创建site_settings/admin目录
  - [ ] 创建site_settings/admin/__init__.py
  - [ ] 创建site_settings/admin/settings_admin.py
    - [ ] 创建SiteSettingsAdmin类
  - [ ] 创建site_settings/admin/recommendation_admin.py
    - [ ] 创建RecommendationAdmin类
- [ ] 验证Admin配置
  - [ ] 检查所有Admin类是否正确注册
  - [ ] 检查批量操作是否正常工作
  - [ ] 检查Admin界面是否正常显示

### 任务 2.10：更新配置文件
- [ ] 更新xxm_fans_home/settings.py
  - [ ] 清理重复配置（如DEFAULT_CHARSET）
  - [ ] 删除多数据库配置（view_data_db）
  - [ ] 更新INSTALLED_APPS（移除main，添加新应用）
  - [ ] 清理注释与实际配置不符的问题
  - [ ] 优化缓存配置
  - [ ] 添加日志配置
  - [ ] 添加REST_FRAMEWORK配置
- [ ] 更新xxm_fans_home/urls.py
  - [ ] 移除main的路由配置
  - [ ] 添加song_management的路由配置
  - [ ] 添加data_analytics的路由配置
  - [ ] 添加site_settings的路由配置
  - [ ] 保留songlist的路由配置
  - [ ] 保留fansDIY的路由配置
- [ ] 删除main/db_router.py（如果存在）
- [ ] 验证配置文件
  - [ ] 检查所有配置是否正确
  - [ ] 测试数据库连接
  - [ ] 测试缓存配置

### 任务 2.11：测试
- [ ] 编写单元测试
  - [ ] song_management应用的测试
    - [ ] 测试所有模型
    - [ ] 测试所有视图
    - [ ] 测试所有序列化器
    - [ ] 测试Admin配置
  - [ ] data_analytics应用的测试
    - [ ] 测试所有模型
    - [ ] 测试所有视图
    - [ ] 测试所有序列化器
    - [ ] 测试Admin配置
  - [ ] site_settings应用的测试
    - [ ] 测试所有模型
    - [ ] 测试所有视图
    - [ ] 测试所有序列化器
    - [ ] 测试Admin配置
- [ ] 进行集成测试
  - [ ] 测试所有API端点
  - [ ] 测试跨应用关联查询
  - [ ] 测试数据联动（WorkStatic与Song的关联）
  - [ ] 测试Admin功能
  - [ ] 测试批量操作
- [ ] 性能测试
  - [ ] 测试数据库查询性能
  - [ ] 测试API响应时间
  - [ ] 识别性能瓶颈
- [ ] 验证所有功能
  - [ ] 歌曲管理功能
  - [ ] 数据分析功能
  - [ ] 网站设置功能
  - [ ] 推荐语功能

### 任务 2.12：删除main应用
- [ ] 备份main应用
- [ ] 从INSTALLED_APPS中移除main
- [ ] 从xxm_fans_home/urls.py中移除main的路由配置
- [ ] 删除main目录
- [ ] 删除main相关的模板文件
- [ ] 更新相关文档

---

## 第三阶段：优化和部署（1周）

### 任务 3.1：性能优化
- [ ] 添加数据库索引
  - [ ] 检查所有模型的索引配置
  - [ ] 添加必要的索引
  - [ ] 优化复合索引
- [ ] 优化数据库查询
  - [ ] 使用select_related优化外键查询
  - [ ] 使用prefetch_related优化多对多查询
  - [ ] 减少N+1查询问题
- [ ] 实现缓存策略
  - [ ] 缓存常用数据（曲风列表、标签列表）
  - [ ] 缓存排行榜数据
  - [ ] 缓存网站设置
  - [ ] 配置缓存过期时间
- [ ] 添加查询优化
  - [ ] 使用only()和defer()优化字段查询
  - [ ] 使用分页减少数据传输
  - [ ] 优化复杂查询

### 任务 3.2：代码质量提升
- [ ] 添加文档注释
  - [ ] 为所有模型添加docstring
  - [ ] 为所有视图添加docstring
  - [ ] 为所有序列化器添加docstring
  - [ ] 为所有Admin类添加docstring
- [ ] 规范命名
  - [ ] 检查所有类名是否符合PEP8规范
  - [ ] 检查所有函数名是否符合PEP8规范
  - [ ] 检查所有变量名是否符合PEP8规范
- [ ] 整合工具脚本
  - [ ] 合并图片下载脚本
    - [ ] 创建tools/image_downloader.py
    - [ ] 实现统一的ImageDownloader类
    - [ ] 删除download_img.py
    - [ ] 删除download_covers.py
    - [ ] 删除download_covers_and_update_json.py
    - [ ] 删除cover_downloader.py
  - [ ] 整合其他工具脚本
  - [ ] 更新工具脚本文档
- [ ] 代码审查
  - [ ] 检查代码重复
  - [ ] 检查代码复杂度
  - [ ] 检查代码风格
  - [ ] 修复发现的问题

### 任务 3.3：文档完善
- [ ] 更新API文档
  - [ ] 确保API文档完整
  - [ ] 添加API示例
  - [ ] 添加错误码说明
  - [ ] 添加性能优化建议
- [ ] 编写部署文档
  - [ ] 环境配置说明
  - [ ] 数据库迁移步骤
  - [ ] 静态文件收集
  - [ ] 生产环境配置
  - [ ] 监控和日志配置
- [ ] 更新开发文档
  - [ ] 项目结构说明
  - [ ] 开发环境搭建
  - [ ] 代码规范说明
  - [ ] 测试指南
  - [ ] 常见问题FAQ
- [ ] 创建架构文档
  - [ ] 应用架构图
  - [ ] 数据模型关系图
  - [ ] API架构图
  - [ ] 技术栈说明

### 任务 3.4：部署准备
- [ ] 配置生产环境
  - [ ] 设置DEBUG = False
  - [ ] 配置ALLOWED_HOSTS
  - [ ] 配置SECRET_KEY
  - [ ] 配置数据库（PostgreSQL/MySQL）
  - [ ] 配置Redis缓存
  - [ ] 配置静态文件服务
  - [ ] 配置媒体文件服务
- [ ] 数据库备份
  - [ ] 备份开发数据库
  - [ ] 准备生产数据库迁移脚本
  - [ ] 测试数据库迁移
- [ ] 静态文件处理
  ```bash
  python manage.py collectstatic
  ```
- [ ] 性能测试
  - [ ] 使用Locust进行压力测试
  - [ ] 测试并发用户访问
  - [ ] 测试API响应时间
  - [ ] 优化性能瓶颈

### 任务 3.5：监控和维护
- [ ] 配置日志监控
  - [ ] 配置日志级别
  - [ ] 配置日志文件路径
  - [ ] 配置日志格式
  - [ ] 配置日志轮转
- [ ] 设置告警
  - [ ] 配置错误告警
  - [ ] 配置性能告警
  - [ ] 配置磁盘空间告警
  - [ ] 配置数据库连接告警
- [ ] 定期维护计划
  - [ ] 数据库备份计划
  - [ ] 日志清理计划
  - [ ] 缓存清理计划
  - [ ] 系统更新计划

### 任务 3.6：最终验证
- [ ] 功能验证
  - [ ] 验证所有API端点
  - [ ] 验证Admin功能
  - [ ] 验证数据关联
  - [ ] 验证缓存功能
- [ ] 性能验证
  - [ ] 验证API响应时间
  - [ ] 验证数据库查询性能
  - [ ] 验证缓存命中率
- [ ] 安全验证
  - [ ] 验证认证和授权
  - [ ] 验证输入验证
  - [ ] 验证SQL注入防护
  - [ ] 验证XSS防护
- [ ] 部署测试
  - [ ] 在测试环境部署
  - [ ] 进行冒烟测试
  - [ ] 进行回归测试
  - [ ] 修复发现的问题

---

## 附录

### A. 风险管理

| 风险 | 概率 | 影响 | 缓解措施 | 状态 |
|------|------|------|----------|------|
| 数据迁移失败 | 中 | 高 | 完整备份数据，分步迁移，充分测试 | 待处理 |
| API兼容性问题 | 高 | 中 | 保持旧API兼容，逐步迁移 | 待处理 |
| 功能缺失 | 中 | 高 | 功能对比测试，确保功能完整 | 待处理 |
| 性能下降 | 低 | 高 | 性能测试，优化查询和缓存 | 待处理 |
| 重构延期 | 中 | 中 | 合理规划，分阶段实施 | 待处理 |

### B. 里程碑

- [ ] **里程碑1**: 完成songlist应用创建和数据迁移（第1周结束）
- [ ] **里程碑2**: 完成所有新应用创建（第2周结束）
- [ ] **里程碑3**: 完成所有数据迁移和视图迁移（第3周结束）
- [ ] **里程碑4**: 完成所有Admin配置和测试（第4周中）
- [ ] **里程碑5**: 完成性能优化和文档完善（第4周结束）
- [ ] **里程碑6**: 完成部署上线（第4周结束）

### C. 验收标准

#### 第一阶段验收标准
- [ ] songlist应用创建成功
- [ ] 所有数据迁移完成且验证通过
- [ ] API兼容性测试通过
- [ ] 旧应用删除完成
- [ ] 测试覆盖率 > 60%

#### 第二阶段验收标准
- [ ] 所有新应用创建成功
- [ ] 所有模型迁移完成
- [ ] 所有视图迁移完成
- [ ] 所有Admin配置完成
- [ ] 跨应用关联正常工作
- [ ] 测试覆盖率 > 60%

#### 第三阶段验收标准
- [ ] 性能优化完成
- [ ] 代码质量提升完成
- [ ] 文档完善
- [ ] 部署配置完成
- [ ] 监控配置完成
- [ ] 所有测试通过

### D. 备注

1. **数据备份**: 在执行任何数据迁移操作前，必须完整备份数据库
2. **测试优先**: 每个任务完成后必须进行测试，确保功能正常
3. **向后兼容**: 重构过程中必须保持API向后兼容性
4. **文档同步**: 代码修改后必须同步更新文档
5. **代码审查**: 重要代码修改必须进行代码审查
6. **性能监控**: 重构过程中持续监控性能指标

### E. 联系方式

- **项目负责人**: 待定
- **技术支持**: 待定
- **紧急联系**: 待定

---

**最后更新**: 2026-01-12
**文档版本**: 2.0