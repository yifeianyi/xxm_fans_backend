import os
from PIL import Image

# 原始图片根目录
SRC_DIR = os.path.join("static", "covers")
# 压缩后图片根目录
DST_DIR = os.path.join("static", "covers_display")
# 压缩质量
QUALITY = 40

for root, dirs, files in os.walk(SRC_DIR):
    for file in files:
        if file.lower().endswith(".jpg"):
            src_path = os.path.join(root, file)
            # 构建目标路径
            rel_path = os.path.relpath(src_path, SRC_DIR)
            dst_path = os.path.join(DST_DIR, rel_path)
            dst_dir = os.path.dirname(dst_path)
            os.makedirs(dst_dir, exist_ok=True)
            try:
                img = Image.open(src_path)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(dst_path, "JPEG", quality=QUALITY, optimize=True)
                print(f"压缩完成: {dst_path}")
            except Exception as e:
                print(f"压缩失败: {src_path}，原因: {e}") 