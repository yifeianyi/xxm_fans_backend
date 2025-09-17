import sqlite3
import os

# 连接到数据库
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 检查一些歌曲的标签数据
cursor.execute("SELECT id, song_name, tag FROM main_songs WHERE tag IS NOT NULL LIMIT 10")
songs = cursor.fetchall()

print("前10首有标签的歌曲:")
for song in songs:
    print(f"  ID: {song[0]}, 歌名: {song[1]}, 标签: {song[2]}")

conn.close()