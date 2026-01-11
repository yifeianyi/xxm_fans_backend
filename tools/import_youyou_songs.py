import os
import sys
import django
import pandas as pd

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from youyou_SongList.models import you_Songs

def import_songs_from_excel(file_path):
    """从Excel文件导入歌曲信息到youyou_SongList"""
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 打印列名以确认格式
        print("Excel文件列名:", df.columns.tolist())
        
        # 检查必要的列是否存在
        required_columns = ['歌名', '歌手', '语种', '曲风']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"缺少必要的列: {missing_columns}")
            return
        
        # 计数器
        success_count = 0
        skip_count = 0
        
        # 遍历每一行数据
        for index, row in df.iterrows():
            try:
                # 获取歌曲信息（根据实际的列名）
                song_name = row.get('歌名', '').strip() if pd.notna(row.get('歌名')) else ''
                language = row.get('语种', '').strip() if pd.notna(row.get('语种')) else ''
                singer = row.get('歌手', '').strip() if pd.notna(row.get('歌手')) else ''
                style = row.get('曲风', '').strip() if pd.notna(row.get('曲风')) else ''
                note = ''  # Excel中没有备注列，留空
                
                # 检查必要字段
                if not song_name:
                    print(f"跳过第{index+1}行：歌曲名称为空")
                    skip_count += 1
                    continue
                
                # 检查是否已存在相同歌曲
                if you_Songs.objects.filter(song_name=song_name, singer=singer).exists():
                    print(f"跳过第{index+1}行：歌曲 '{song_name}' 已存在")
                    skip_count += 1
                    continue
                
                # 创建新歌曲记录
                song = you_Songs(
                    song_name=song_name,
                    language=language,
                    singer=singer,
                    style=style,
                    note=note
                )
                song.save()
                success_count += 1
                print(f"成功导入歌曲: {song_name}")
                
            except Exception as e:
                print(f"处理第{index+1}行时出错: {e}")
                skip_count += 1
        
        print(f"\n导入完成！成功导入: {success_count} 首歌曲, 跳过: {skip_count} 条记录")
        
    except Exception as e:
        print(f"导入过程中发生错误: {e}")

if __name__ == "__main__":
    excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "由由歌单.xls")
    import_songs_from_excel(excel_file)