import zlib
import time
import chat
import chatGUI
import safelogin
import json
import threading
import tkinter as tk
import time
from safelogin import s
import cv2
import pickle
import struct

video_data = b""
vsendflag = 0
video_data_lock = threading.Lock()  # 添加一个锁对象用于同步访问video_data

class Video:
    def __init__(self, level):
        if level <= 3:
            self.interval = level
        else:
            self.interval = 3
        self.fx = 1/(self.interval + 1)
        if self.fx < 0.3:
            self.fx = 0.3
        self.cap = cv2.VideoCapture(0)

    def run_send(self):
        while self.cap.isOpened():
            global vsendflag
            vsendflag = 1
            ret, frame = self.cap.read()
            # 将帧序列化并发送
            data = pickle.dumps(frame)
            zdata = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
            try:
                s.sendall(struct.pack("L", len(zdata)) + zdata)
            except:
                break
            # 显示本地视频
            cv2.imshow("Local Video", frame)
            time.sleep(0.033)
            if cv2.waitKey(1) & 0xFF == 27:  # 按ESC键退出
                cv2.destroyWindow("Local Video")
                return

    def run_play(self, name):
        while True:
            global video_data
            try:
                frame = pickle.loads(video_data)

                # 在窗口中显示视频帧
                cv2.imshow(name, frame)
                if cv2.waitKey(1) & 0xFF == 27:  # 按ESC键退出
                    cv2.destroyWindow(name)
                    return
            except:
                print("video play error")
                return


# 接收消息
def recv():
    while True:
        # try:
            raw_data = s.recv(81920)
            try:
                data = raw_data.decode('utf-8')
                data = json.loads(data)
            except:
                data = raw_data
                pass
            finally:
                if type(data) != dict:  # 解包消息是视频数据
                    print("video detected")
                    payload_size = struct.calcsize("L")
                    if len(raw_data) < payload_size:
                        pass
                    else:
                        packed_size = raw_data[:payload_size]
                        data = raw_data[payload_size:]
                        msg_size = struct.unpack("L",packed_size)[0]
                        while len(data) < msg_size:
                            data += s.recv(81920)
                        zframe_data = data[:msg_size]
                        data = data[msg_size:]
                        frame_data = zlib.decompress(zframe_data)
                        global video_data
                        video_data = frame_data
                elif data["type"] == "user_list":  # 接收的消息是用户列表，则重新加载用户
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
                elif data["type"] == "video_return":  # 接收到服务器返回消息，建立视频连接
                    my_video = threading.Thread(target=video.run_send)  # 创建视频发送线程
                    my_video.start()
                elif data["type"] == "video":  # 接收到视频连接请求，启动视频播放
                    name = data["sender"]
                    if vsendflag == 0:
                        my_video = threading.Thread(target=video.run_send)  # 创建视频发送线程
                        my_video.start()
                    # my_video = threading.Thread(target=video.run_play, args=(name,))  # 创建视频播放线程
                    # my_video.start()
        # except:
        #     print("已经断开链接")
        #     break


# 发送消息
def send(*args):
    timestamp = time.time()
    data = {"type": "message", "sender": chat.user, "receiver": chat.chat,
            "message": chat.chatGUI.a.get("1.0", "end"), "time": time.ctime(timestamp)}
    chat.send(time.ctime(timestamp))
    print(data)
    data = json.dumps(data)
    s.send(data.encode('utf-8'))


def audio_chat():
    print("audio start")
    if chat.chat == "all_user":
        return
    data = {"type": "audio", "sender": chat.user, "receiver": chat.chat}
    s.send(json.dumps(data).encode('utf-8'))


def video_chat():
    print("video start")
    if chat.chat == "all_user":
        return
    data = {"type": "video", "sender": chat.user, "receiver": chat.chat}
    s.send(json.dumps(data).encode('utf-8'))


chat.user = safelogin.user
if chat.user != "":
    video = Video(3)
    chat.create_chat()  # 创建聊天界面
    chat.chatGUI.a.bind("<Return>", send)
    # 回车绑定发送功能
    but = tk.Button(chat.chatGUI.a, text='发送', command=send, font=15)
    but.place(x=500, y=60, width=50, height=30)
    # 语音聊天按钮
    global pic3
    photo3 = tk.PhotoImage(file="icon/voice.png")
    pic3 = photo3.subsample(5, 5)
    but3 = tk.Button(chat.chatGUI.root, text="语音聊天", command=audio_chat, image=pic3, compound=tk.LEFT, height=18)
    but3.place(x=95, y=322)
    # 视频聊天按钮
    global pic4
    photo4 = tk.PhotoImage(file="icon/video.png")
    pic4 = photo4.subsample(5, 5)
    but4 = tk.Button(chat.chatGUI.root, text="视频聊天", command=video_chat, image=pic4, compound=tk.LEFT, height=18)
    but4.place(x=180, y=322)
    r = threading.Thread(target=recv)  # 启动接受消息线程
    r.start()
    chat.tkinter.mainloop()
# 关闭链接，把缓存的消息放进文件a
s.close()
chat.t.close()

