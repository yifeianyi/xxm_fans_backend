#!/usr/bin/env python
"""
下载happy_data_list.json中的封面图片并更新JSON文件
将封面路径从B站链接改为本地路径格式：covers/year/month/year-month-day.jpg
"""

import json
import os
import requests
from datetime import datetime
import time
from urllib.parse import urlparse
import hashlib

def download_image(url, save_path):
    """下载图片到指定路径"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"❌ 下载失败 {url}: {e}")
        return False

def get_filename_from_url(url):
    """从URL中提取文件名"""
    parsed = urlparse(url)
    return os.path.basename(parsed.path)

def process_json_file(json_file_path, output_dir):
    """处理JSON文件，下载图片并更新路径"""
    
    # 读取JSON文件
    print(f"📖 读取JSON文件: {json_file_path}")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 总共 {len(data)} 条记录")
    
    # 统计信息
    total_items = len(data)
    downloaded_count = 0
    updated_count = 0
    failed_count = 0
    
    # 用于去重的字典，避免重复下载相同图片
    downloaded_images = {}
    
    for i, item in enumerate(data):
        if i % 100 == 0:
            print(f"⏳ 处理进度: {i}/{total_items}")
        
        # 获取时间信息
        time_str = item.get('时间', '')
        if not time_str:
            print(f"⚠️  第 {i+1} 条记录缺少时间信息，跳过")
            failed_count += 1
            continue
        
        try:
            # 解析时间
            date_obj = datetime.strptime(time_str, '%Y-%m-%d')
            year = date_obj.year
            month = date_obj.month
            day = date_obj.day
            
            # 构建新的封面路径
            new_cover_path = f"covers/{year:04d}/{month:02d}/{year:04d}-{month:02d}-{day:02d}.jpg"
            
            # 获取原始封面URL
            original_cover_url = item.get('封面', '')
            if not original_cover_url:
                print(f"⚠️  第 {i+1} 条记录缺少封面URL，跳过")
                failed_count += 1
                continue
            
            # 检查是否已经下载过相同的图片
            if original_cover_url in downloaded_images:
                # 使用已下载的图片路径
                item['封面'] = downloaded_images[original_cover_url]
                updated_count += 1
                continue
            
            # 构建保存路径
            save_path = os.path.join(output_dir, new_cover_path)
            
            # 如果文件已存在，跳过下载
            if os.path.exists(save_path):
                print(f"✅ 文件已存在，跳过: {new_cover_path}")
                downloaded_images[original_cover_url] = new_cover_path
                item['封面'] = new_cover_path
                updated_count += 1
                continue
            
            # 下载图片
            print(f"📥 下载图片: {original_cover_url} -> {new_cover_path}")
            if download_image(original_cover_url, save_path):
                downloaded_count += 1
                downloaded_images[original_cover_url] = new_cover_path
                item['封面'] = new_cover_path
                updated_count += 1
                
                # 添加延迟避免请求过快
                time.sleep(0.1)
            else:
                failed_count += 1
                
        except Exception as e:
            print(f"❌ 处理第 {i+1} 条记录时出错: {e}")
            failed_count += 1
    
    # 保存更新后的JSON文件
    output_json_path = json_file_path.replace('.json', '_updated.json')
    print(f"💾 保存更新后的JSON文件: {output_json_path}")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    # 打印统计信息
    print(f"\n📈 处理完成!")
    print(f"✅ 成功下载: {downloaded_count} 张图片")
    print(f"✅ 成功更新: {updated_count} 条记录")
    print(f"❌ 失败: {failed_count} 条记录")
    print(f"📁 图片保存目录: {output_dir}")
    print(f"📄 更新后的JSON文件: {output_json_path}")

def main():
    # 配置路径
    json_file_path = 'happy_data_list.json'
    output_dir = 'xxm_fans_frontend/public'
    
    # 检查输入文件是否存在
    if not os.path.exists(json_file_path):
        print(f"❌ 找不到文件: {json_file_path}")
        return
    
    # 检查输出目录是否存在
    if not os.path.exists(output_dir):
        print(f"❌ 找不到输出目录: {output_dir}")
        return
    
    print("🚀 开始处理封面图片下载和JSON更新...")
    process_json_file(json_file_path, output_dir)

if __name__ == '__main__':
    main() 