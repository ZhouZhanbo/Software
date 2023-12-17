import chat
import chatGUI
import safelogin
import json
import threading
import tkinter as tk
import time
from safelogin import s
import main

# 接收消息
def recv():
    while True:
        try:
            data = s.recv(1024)
            data = data.decode()
            data = json.loads(data)
            print(data)
            if data["type"] == "user_list":  # 接收的消息是用户列表，则重新加载用户
                chat.show_users(data["user_list"])
            elif data["type"] == "message":  # 接收的消息是文本消息
                chat.revc(data["receiver"], data["sender"], data["message"], data["time"])
                if data["receiver"] != "all_user":
                    for i in range(-1,chatGUI.listbox1.size()):  # 消息发送方背景变红
                        if chatGUI.listbox1.get(i) == data["sender"] \
                                and chatGUI.listbox1.curselection()[0] != i:  # 当已经选中该发方则不变红
                            chatGUI.listbox1.itemconfigure((i,), bg="red")
                else:  # 如果收方为all_user,则不能将sender标红，而是把all_user标红
                    for i in range(-1,chatGUI.listbox1.size()):  # 消息发送方背景变红
                        if chatGUI.listbox1.get(i) == "all_user" \
                                and chatGUI.listbox1.curselection()[0] != i:  # 当已经选中该发方则不变红
                            chatGUI.listbox1.itemconfigure((i,), bg="red")
            elif data["type"] == "audio":
                # 调用xx函数
                print("语音")
                main.audio_call(data["IP"])
                pass
            elif data["type"] == "video":
                main.vedio_call(data["IP"])
                pass

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
    s.send(data.encode())


def audio_chat():
    if chat.chat == "all_user":
        return
    data = {"type": "audio", "sender": chat.user, "receiver": chat.chat}
    s.send(json.dumps(data).encode('utf-8'))


def video_chat():
    if chat.chat == "all_user":
        return
    data = {"type": "video", "sender": chat.user, "receiver": chat.chat}
    s.send(json.dumps(data).encode('utf-8'))


chat.user = safelogin.user
if chat.user != "":
    chat.create_chat()  # 创建聊天界面
    chat.chatGUI.a.bind("<Return>", send)
    photo3 = tk.PhotoImage(file="icon/voice.png")
    pic3 = photo3.subsample(5, 5)
    but3 = tk.Button(chat.chatGUI.root, text="语音聊天", command=audio_chat, image=pic3, compound=tk.LEFT, height=18)
    but3.place(x=95, y=322)
    photo4 = tk.PhotoImage(file="icon/video.png")
    pic4 = photo4.subsample(5, 5)
    but4 = tk.Button(chat.chatGUI.root, text="视频聊天", command=video_chat, image=pic4, compound=tk.LEFT, height=18)
    but4.place(x=180, y=322)
    # 回车绑定发送功能
    but = tk.Button(chat.chatGUI.a, text='发送', command=send, font=15)
    but.place(x=500, y=60, width=50, height=30)
    r = threading.Thread(target=recv)  # 启动接受消息线程
    r.start()
    chat.tkinter.mainloop()
# 关闭链接，把缓存的消息放进文件a
s.close()
chat.t.close()

