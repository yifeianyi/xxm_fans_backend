import sqlite3
import os

# 连接到数据库
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 获取main_songs表的结构
cursor.execute("PRAGMA table_info(main_songs)")
columns = cursor.fetchall()

print("main_songs表结构:")
for column in columns:
    print(f"  {column[1]} ({column[2]})")

conn.close()