#!/usr/bin/env python
import json
import os
import requests
from datetime import datetime
import time

def download_image(url, save_path):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return False

def process_json():
    json_file = 'happy_data_list.json'
    output_dir = 'xxm_fans_frontend/public'
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"总共 {len(data)} 条记录")
    
    downloaded_images = {}
    updated_count = 0
    
    for i, item in enumerate(data):
        if i % 100 == 0:
            print(f"进度: {i}/{len(data)}")
        
        time_str = item.get('时间', '')
        if not time_str:
            continue
        
        try:
            date_obj = datetime.strptime(time_str, '%Y-%m-%d')
            year = date_obj.year
            month = date_obj.month
            day = date_obj.day
            
            new_cover_path = f"covers/{year:04d}/{month:02d}/{year:04d}-{month:02d}-{day:02d}.jpg"
            
            original_url = item.get('封面', '')
            if not original_url:
                continue
            
            if original_url in downloaded_images:
                item['封面'] = downloaded_images[original_url]
                updated_count += 1
                continue
            
            save_path = os.path.join(output_dir, new_cover_path)
            
            if os.path.exists(save_path):
                downloaded_images[original_url] = new_cover_path
                item['封面'] = new_cover_path
                updated_count += 1
                continue
            
            if download_image(original_url, save_path):
                downloaded_images[original_url] = new_cover_path
                item['封面'] = new_cover_path
                updated_count += 1
                time.sleep(0.1)
                
        except Exception as e:
            print(f"处理第 {i+1} 条记录时出错: {e}")
    
    output_json = json_file.replace('.json', '_updated.json')
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"完成! 更新了 {updated_count} 条记录")
    print(f"输出文件: {output_json}")

if __name__ == '__main__':
    process_json() 