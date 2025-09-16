import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

# 初始化Django
django.setup()

from main.models import Style

def check_styles():
    """检查曲风数据"""
    print("检查曲风数据...")
    styles = Style.objects.all()
    for style in styles:
        print(f"ID: {style.id}, Name: {style.name}")
    print("检查完成")

if __name__ == '__main__':
    check_styles()