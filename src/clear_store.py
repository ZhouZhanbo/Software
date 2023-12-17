import sqlite3
import store

# 连接到数据库
conn = sqlite3.connect('user_data.db')
c = conn.cursor()
c.execute("DELETE FROM users")
conn.commit()
conn.close()
store.shuchu()
