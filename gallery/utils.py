"""
图集缩略图生成工具模块
"""
from core.thumbnail_generator import ThumbnailGenerator as CoreThumbnailGenerator

# 创建别名以保持向后兼容
ThumbnailGenerator = CoreThumbnailGenerator