# SongRecord 后台管理页面 BV 号封面下载功能实现文档

**时间**: 2025年9月23日

## 涉及的函数

1. `main.forms.SongRecordForm` - 添加 BV 号输入框
2. `main.admin.SongRecordAdmin.download_bv_cover_view` - 处理 BV 号封面下载的视图函数
3. `tools.cover_downloader.CoverDownloader.download_and_save_cover` - 封面下载和保存函数
4. `templates/admin/main/songrecord/change_form.html` - 自定义模板添加下载功能

## 功能说明

本功能在 SongRecord 后台管理页面的"增加演唱记录"页面中添加了 BV 号输入和封面下载功能，具体包括：

1. 在表单中增加一个 BV 号输入框
2. 在输入框旁边添加"下载"按钮
3. 用户输入 BV 号并填写演唱日期后，点击下载按钮可自动下载对应视频的封面图
4. 封面图保存在 `xxm_fans_frontend/public/covers/YYYY/MM/` 目录下，文件名为 `YYYY-MM-DD.jpg`
5. 下载完成后弹出提示信息，显示图片保存路径，并自动填充封面 URL 字段

## 实现细节

### 1. 表单修改 (main/forms.py)

在 `SongRecordForm` 中添加了 `bv_id` 字段：

```python
bv_id = forms.CharField(label="BV号", max_length=20, required=False, 
                       help_text="输入BV号后点击下载按钮可下载封面图")
```

### 2. 后台管理视图修改 (main/admin.py)

添加了 `download_bv_cover_view` 视图函数，用于处理 BV 号封面下载请求：

- 验证 BV 号格式和演唱日期
- 调用 B站 API 获取视频封面 URL
- 使用现有的 `CoverDownloader` 类下载并保存封面
- 返回 JSON 格式的响应，包含下载结果和保存路径

### 3. 模板修改 (templates/admin/main/songrecord/change_form.html)

添加 JavaScript 代码实现前端交互：

- 在 BV 号输入框旁边添加"下载"按钮
- 点击按钮时收集 BV 号和演唱日期信息
- 发送 AJAX 请求到后台下载接口
- 下载成功后更新封面 URL 字段并显示提示信息

## 技术要点

1. 复用现有的 `CoverDownloader` 类，确保与项目其他部分的封面下载逻辑一致
2. 使用 AJAX 实现无刷新下载，提升用户体验
3. 严格按照项目要求的目录结构保存封面图片
4. 提供清晰的用户反馈，包括错误提示和成功信息