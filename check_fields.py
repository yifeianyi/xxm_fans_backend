import sqlite3

# 连接到 SQLite 数据库
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 获取 main_songs 表的字段信息
cursor.execute('PRAGMA table_info(main_songs);')
columns = cursor.fetchall()

print('现有字段:')
for col in columns:
    print(col[1])

# 关闭连接
conn.close()