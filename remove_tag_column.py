import sqlite3

# 连接到 SQLite 数据库
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 移除 main_songs 表中的 tag 字段
cursor.execute("ALTER TABLE main_songs DROP COLUMN tag;")

# 提交更改并关闭连接
conn.commit()
conn.close()

print('成功移除 tag 字段')