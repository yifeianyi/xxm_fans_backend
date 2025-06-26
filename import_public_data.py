import os
import django
import json
from django.core import serializers

# 设置 Django 环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xxm_fans_home.settings")
django.setup()

from main.models import Songs, Style, SongRecord, ViewBaseMess, RealTimeInfo

def import_public_data():
    """导入公开数据"""
    
    input_file = 'sqlInit_data/public_data.json'
    
    if not os.path.exists(input_file):
        print(f"错误：找不到文件 {input_file}")
        print("请先运行 export_public_data.py 导出数据")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    # 按依赖关系排序模型（先导入被引用的模型）
    model_order = ['Style', 'Songs', 'SongRecord', 'ViewBaseMess', 'RealTimeInfo']
    
    for model_name in model_order:
        if model_name in all_data:
            print(f"正在导入 {model_name}...")
            
            # 获取对应的模型类
            model_map = {
                'Songs': Songs,
                'Style': Style,
                'SongRecord': SongRecord,
                'ViewBaseMess': ViewBaseMess,
                'RealTimeInfo': RealTimeInfo
            }
            
            model_class = model_map.get(model_name)
            if not model_class:
                print(f"警告：未知模型 {model_name}")
                continue
            
            # 清空现有数据（可选）
            # model_class.objects.all().delete()
            
            # 导入数据
            data = all_data[model_name]
            for item in data:
                try:
                    # 检查是否已存在
                    if model_class.objects.filter(pk=item['pk']).exists():
                        print(f"跳过已存在的记录: {model_name} pk={item['pk']}")
                        continue
                    
                    # 创建对象
                    obj = model_class(**item['fields'])
                    obj.pk = item['pk']  # 保持原始ID
                    obj.save()
                    
                except Exception as e:
                    print(f"导入失败 {model_name} pk={item['pk']}: {e}")
            
            print(f"已导入 {len(data)} 条 {model_name} 记录")
    
    print("\n数据导入完成！")

if __name__ == "__main__":
    import_public_data() 