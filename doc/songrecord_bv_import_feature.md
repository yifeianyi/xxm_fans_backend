# SongRecord BV号导入功能实现文档

**时间**: 2025年9月23日

**涉及的函数**:
1. `SongRecordAdmin.get_fields` - 修改字段显示逻辑
2. `SongRecordAdmin.save_model` - 添加BV号处理逻辑
3. `SongRecordForm` - 表单字段修改

## 功能说明

本次修改实现了在SongRecord后台管理页面添加BV号导入功能，具体包括：

1. 在"增加演唱记录"页面添加BV号输入文本框
2. 在保存时自动根据BV号获取视频信息并填充URL和封面

## 实现细节

### 1. 表单修改
在`SongRecordForm`中保留了`bv_id`字段用于输入BV号。

### 2. 字段显示控制
修改了`SongRecordAdmin.get_fields`方法，使得在添加页面显示BV号输入框。

### 3. BV号处理逻辑
在`SongRecordAdmin.save_model`方法中添加了BV号处理逻辑：
- 当添加新记录且提供了BV号时，调用`BilibiliImporter`解析BV号信息
- 自动填充URL字段
- 自动下载并保存视频封面到指定路径
- 封面路径格式为`/covers/{年}/{月}/{日期}.jpg`

## 使用方法

1. 进入Django管理后台的"增加演唱记录"页面
2. 在表单中找到"BV号"输入框
3. 输入有效的BV号（如：BV1xx411c7mu）
4. 填写其他必要信息后保存
5. 系统会自动根据BV号获取视频URL并下载封面

## 技术细节

- 封面下载使用了现有的`BilibiliImporter.download_and_save_cover`方法
- 封面保存路径遵循项目要求：`xxm_fans_frontend/public/covers/{年}/{月}/{日期}.jpg`
- 封面URL在数据库中保存为相对路径格式：`/covers/{年}/{月}/{日期}.jpg`