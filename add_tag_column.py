import sqlite3
import os

# 连接到数据库
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 添加tag字段
try:
    cursor.execute("ALTER TABLE main_songs ADD COLUMN tag varchar(100)")
    print("成功添加tag字段")
except sqlite3.OperationalError as e:
    print(f"添加字段时出错: {e}")

conn.commit()
conn.close()