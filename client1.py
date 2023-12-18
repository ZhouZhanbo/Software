import chat
import chatGUI
import safelogin
import json
import threading
import tkinter as tk
import time
import easygui as eg
import os
from safelogin import client

# 接收消息
def recv():
    while True:
        try:
            data = client.recv(1024)
            data = data.decode()
            data = json.loads(data)
            if data["type"] == "user_list":  # 接收的消息是用户列表，则重新加载用户
                chat.show_users(data["user_list"])
            elif data["type"] == "message":  # 接收的消息是文本消息
                chat.revc(data["receiver"], data["sender"], data["message"], data["time"])
            elif data["type"] == "file":
                # 解码文件名,文件大小
                filename = data["filename"]
                filesize = client.recv(1024)
                filesize = int.from_bytes(filesize, byteorder='big')
                '''接收文件'''
                try:
                    if not os.path.exists("files" + "\\" + chat.user):  # 看是否有该文件夹，没有则创建文件夹
                        os.mkdir("files" + "\\" + chat.user)
                    f = open("files" + "\\" + chat.user + "\\" +filename, 'wb')
                    size = 0
                    start_time = time.time()
                    while True:
                        # 接收数据
                        f_data = client.recv(1024)
                        # 数据长度不为零，接收继续
                        if f_data:
                            f.write(f_data)
                            size += len(f_data)
                            if time.time() - start_time == 0:
                                time.sleep(0.5)
                            speed = (size) / (time.time() - start_time)
                            print('\r' + '【下载进度】:%s%.2f%%, Speed: %.2fMB/s' % (
                            '>' * int(size * 50 / filesize), float(size / filesize * 100), float(speed / 1024 / 1024)),
                                  end=' ')
                            # 数据长度为零接收完成
                            if size == filesize:
                              break
                except Exception as e:
                    print(f'接收异常', e)
                else:
                    f.flush()
                    print(f'{filename},{float(filesize / 1024 / 1024):.2f}MB, 接收完成')
                    f.close()

            # 来消息提示
            if data["receiver"] != "all_user":
                for i in range(-1,chatGUI.listbox1.size()):  # 消息发送方背景变红
                    if chatGUI.listbox1.get(i) == data["sender"] \
                            and chatGUI.listbox1.curselection()[0] != i:  # 当已经选中该发方则不变红
                        chatGUI.listbox1.itemconfigure((i,), bg="red")
            elif data["receiver"] == "all_user" and data["type"] != "user_list":  # 如果收方为all_user,则不能将sender标红，而是把all_user标红
                for i in range(-1,chatGUI.listbox1.size()):  # 消息发送方背景变红
                    if chatGUI.listbox1.get(i) == "all_user" \
                            and chatGUI.listbox1.curselection()[0] != i:  # 当已经选中该发方则不变红
                        chatGUI.listbox1.itemconfigure((i,), bg="red")
        except:
            print("已经断开链接")
            break


# 发送消息
def send(*args):
    timestamp = time.time()
    data = {"type": "message", "sender": chat.user, "receiver": chat.chat,
            "message": chat.chatGUI.a.get("1.0", "end"), "time": time.ctime(timestamp)}
    chat.send(time.ctime(timestamp))
    data = json.dumps(data)
    client.send(data.encode())

def sendfile():
    # 选择发送的文件
    try:
        filepath = eg.fileopenbox(title='选择文件')
        '''获取文件名,文件大小'''
        filename = filepath.split("\\")[-1]
        filesize = os.path.getsize(filepath)
        # 先把类型、通信双方以及文件名传过去
        data = {"type": "file", "sender": chat.user, "receiver": chat.chat,
                "filename": filename}
        data = json.dumps(data)
        client.send(data.encode())
        time.sleep(0.5)
        # 再将将文件大小传过去
        # 编码文件大小
        client.send(filesize.to_bytes(filesize.bit_length(), byteorder='big'))
    except AttributeError:
        print("未选择文件")
    try:
        '''传输文件'''
        start_time = time.time()
        with open(filepath, 'rb') as f:
            size = 0
            while True:
                # 读取文件数据，每次1024KB
                f_data = f.read(1024)
                # 数据长度不为零，传输继续
                if f_data:
                    client.send(f_data)
                    size += len(f_data)
                    if time.time() - start_time == 0:
                        time.sleep(0.5)
                    speed = (size) / (time.time() - start_time)
                    print('\r' + '【上传进度】:%s%.2f%%, Speed: %.2fMB/s' % (
                        '>' * int(size * 50 / filesize), float(size / filesize * 100), float(speed / 1024 / 1024)),
                            end=' ')
                # 数据长度为零传输完成
                else:
                    print(f'{filename},{float(filesize / 1024 / 1024):.2f}MB, 传输完成')
                    break
    except Exception as e:
        print(f'传输异常', e)

def audio_chat():
    if chat.chat == "all_user":
        return
    data = {"type": "audio", "sender": chat.user, "receiver": chat.chat}
    client.send(json.dumps(data).encode('utf-8'))


def video_chat():
    if chat.chat == "all_user":
        return
    data = {"type": "video", "sender": chat.user, "receiver": chat.chat}
    client.send(json.dumps(data).encode('utf-8'))


chat.user = safelogin.user
if chat.user != "":
    chat.create_chat()  # 创建聊天界面
    chat.chatGUI.a.bind("<Return>", send)
    # 回车绑定发送功能
    but = tk.Button(chat.chatGUI.a, text='发送', command=send, font=15)
    but.place(x=500, y=60, width=50, height=30)
    # 传输文件按钮
    global pic2
    photo2 = tk.PhotoImage(file="icon/file.png")
    pic2 = photo2.subsample(5, 5)
    but2 = tk.Button(chatGUI.root, text="文件传输", command=sendfile, image=pic2, compound=tk.LEFT, height=18)
    but2.place(x=10, y=322)
    # 语音聊天按钮
    global pic3
    photo3 = tk.PhotoImage(file="icon/voice.png")
    pic3 = photo3.subsample(5, 5)
    but3 = tk.Button(chatGUI.root, text="语音聊天", command="", image=pic3, compound=tk.LEFT, height=18)
    but3.place(x=95, y=322)
    # 视频聊天按钮
    global pic4
    photo4 = tk.PhotoImage(file="icon/video.png")
    pic4 = photo4.subsample(5, 5)
    but4 = tk.Button(chatGUI.root, text="视频聊天", command="", image=pic4, compound=tk.LEFT, height=18)
    but4.place(x=180, y=322)
    # 用户属性按钮
    global pic5
    photo5 = tk.PhotoImage(file="icon/user.png")
    pic5 = photo5.subsample(5, 5)
    but4 = tk.Button(chatGUI.root, text="用户属性", command="", image=pic5, compound=tk.LEFT, height=18)
    but4.place(x=485, y=322)
    r = threading.Thread(target=recv)  # 启动接受消息线程
    r.start()
    chat.tkinter.mainloop()
# 关闭链接，把缓存的消息放进文件a
client.close()
chat.t.close()

