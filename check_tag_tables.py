import sqlite3
import os

# 连接到数据库
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 检查main_tag表
try:
    cursor.execute("SELECT COUNT(*) FROM main_tag")
    count = cursor.fetchone()[0]
    print(f"main_tag表中有 {count} 条记录")
    
    if count > 0:
        cursor.execute("SELECT id, name FROM main_tag LIMIT 10")
        tags = cursor.fetchall()
        print("前10个标签:")
        for tag in tags:
            print(f"  {tag[0]}: {tag[1]}")
except sqlite3.OperationalError as e:
    print(f"查询main_tag表时出错: {e}")

# 检查main_songtag表
try:
    cursor.execute("SELECT COUNT(*) FROM main_songtag")
    count = cursor.fetchone()[0]
    print(f"main_songtag表中有 {count} 条记录")
    
    if count > 0:
        cursor.execute("SELECT id, song_id, tag_id FROM main_songtag LIMIT 10")
        songtags = cursor.fetchall()
        print("前10个歌曲标签关联:")
        for songtag in songtags:
            print(f"  {songtag[0]}: 歌曲{songtag[1]} - 标签{songtag[2]}")
except sqlite3.OperationalError as e:
    print(f"查询main_songtag表时出错: {e}")

conn.close()