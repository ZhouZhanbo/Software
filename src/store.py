import sqlite3
import hashlib


def create_database():
    conn = sqlite3.connect('user_data.db')  # 创建一个名为user_data.db的数据库
    c = conn.cursor()

    # 创建一个名为users的表，如果它不存在的话
    c.execute('''  
              CREATE TABLE IF NOT EXISTS users(  
              username TEXT NOT NULL,  
              password TEXT NOT NULL);  
              ''')
    conn.commit()
    conn.close()


def user_zhuce(username, password, againpassword):    # 注册用户
    print("ok")
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # 在users表中查找用户名
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()

    if user is None:    # 用户名不重复
        if password == againpassword:   # 注册并返回3
            password = password_md5(password)
            c.execute("INSERT INTO users VALUES (?,?)", (username, password))
            conn.commit()
            return 3
        else:   # 密码和确认密码不一样，返回2
            return 2
    else:    # 用户名重复，返回1
        return 1


def check_user(username, password): #查找密码
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # 在users表中查找用户名
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()

    if user is None:                # 未注册
        return 1
    else:
        # 如果找到用户，判断收到的密码与储存的密码是否相同，相同则返回2，不相同则返回3
        password = password_md5(password)  # 将密码加密
        if user[1] == password:
            return 2
        else:
            return 3


def password_md5(password):      # 密码加密
    # 创建一个md5对象
    md5 = hashlib.md5()

    # 给md5对象提供要加密的数据，需要先将其转换为字节
    md5.update(password.encode('utf-8'))

    # 获取哈希值并以16进制字符串的形式返回
    result = md5.hexdigest()
    return result


def shuchu():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    results = c.fetchall()
    for row in results:
        print(row)
    conn.close()


def user_change(username,oldpassword,newpassword,agaginnewpassword):
    print("hhh")
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # 在users表中查找用户名
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()

    if user is None:     # 用户不存在，返回1
        return 1
    else:
        oldpassword = password_md5(oldpassword)
        if user[1] == oldpassword:
            if newpassword == agaginnewpassword:
                newpassword = password_md5(newpassword)
                delete_query = "DELETE FROM users WHERE username = ?"
                c.execute(delete_query, (user[0],))
                conn.commit()
                c.execute("INSERT INTO users VALUES (?,?)", (user[0], newpassword))
                conn.commit()
                return 4    # 条件全满足，修改密码，返回4
            else:
                return 3    # 旧密码正确但输入的新密码和确认密码不一致，返回3
        else:
            return 2    # 用户存在但旧密码错误，返回2



create_database()
shuchu()