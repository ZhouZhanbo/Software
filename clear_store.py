import sqlite3
import store
"""
运行该文件可以将已经注册的信息及数据中的内容清除
"""
# 连接到数据库
conn = sqlite3.connect('user_data.db')
c = conn.cursor()
c.execute("DELETE FROM users")
conn.commit()
conn.close()
store.shuchu()
