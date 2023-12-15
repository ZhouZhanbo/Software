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
import pyaudio

p = pyaudio.PyAudio()
CHUNK = 1024
FORMAT = pyaudio.paInt16    # 格式
CHANNELS = 2    # 输入/输出通道数
RATE = 44100    # 音频数据的采样频率
RECORD_SECONDS = 0.5    # 记录秒

video_data_lock = threading.Lock()  # 添加一个锁对象用于同步访问video_data

video_data = b""
vsendflag = 0
asendflag = 0


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
                frame_data = zlib.decompress(video_data)
                frame = pickle.loads(frame_data)
                cv2.imshow(name, frame)
                print("playing")
                # 在窗口中显示视频帧
                if cv2.waitKey(1) & 0xFF == 27:  # 按ESC键退出
                    cv2.destroyWindow(name)
                    return
            except:
                print("video play error")
                pass


class Audio:
    def __init__(self):
        self.stream_input = None
        self.stream_output = None

    def audio_send(self):
        self.stream_input = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        while self.stream_input.is_active():
            global asendflag
            asendflag = 1
            frames = []
            data = self.stream_input.read(CHUNK)
            senddata = pickle.dumps(data)
            try:
                s.sendall(struct.pack("L", len(senddata)) + senddata)
            except:
                break

    def audio_play(self):
        self.stream_output = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
        while True:
            # try:
                global video_data
                with video_data_lock:
                    frame_data = video_data
                # frames = pickle.loads(frame_data)
                self.stream_output.write(frame_data)
                print("audio working")
            # except:
            #     print("audio play error")
            #     pass

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
                if type(data) != dict:  # 解包消息是音视频数据
                    print("video detected")
                    payload_size = struct.calcsize("L")
                    while len(raw_data) < payload_size:
                        raw_data += s.recv(81920)
                    else:
                        packed_size = raw_data[:payload_size]
                        data = raw_data[payload_size:]
                        msg_size = struct.unpack("L",packed_size)[0]
                        start_time = time.time()
                        while len(data) < msg_size:
                            timeout = 1.0
                            current_time = time.time()
                            elapsed_time = current_time - start_time  # 计算已经过去的时间
                            if elapsed_time >= timeout:
                                print("time out")
                                break
                            else:
                                data += s.recv(81920)
                        zframe_data = data[:msg_size]
                        data = data[msg_size:]
                        global video_data
                        with video_data_lock:
                            video_data = zframe_data
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
                    # my_video = threading.Thread(target=video.run_send)  # 创建视频发送线程
                    # my_video.start()
                    pass
                elif data["type"] == "video":  # 接收到视频连接请求，启动视频播放
                    name = data["sender"]
                    if vsendflag == 0:
                        # my_video = threading.Thread(target=video.run_send)  # 创建视频发送线程
                        # my_video.start()
                        pass
                    my_video = threading.Thread(target=video.run_play, args=(name,))  # 创建视频播放线程
                    my_video.start()
                elif data["type"] == "audio_return":  # 接收到服务器返回消息，建立视频连接
                    # my_audio = threading.Thread(target=audio.audio_send)  # 创建音频发送线程
                    # my_audio.start()
                    pass
                elif data["type"] == "audio":  # 接收到视频连接请求，启动视频播放
                    if asendflag == 0:
                        # my_audio = threading.Thread(target=audio.audio_send)  # 创建音频发送线程
                        # my_audio.start()
                        pass
                    my_audio = threading.Thread(target=audio.audio_play)  # 创建音频播放线程
                    my_audio.start()
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
    audio = Audio()
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
    r.daemon = True
    r.start()
    chat.tkinter.mainloop()
# 关闭链接，把缓存的消息放进文件a
s.close()
chat.t.close()

