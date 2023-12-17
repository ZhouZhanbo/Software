from socket import *
import threading
import pyaudio
import wave
import sys
import zlib
import struct
import pickle
import time
import numpy as np

# 定义音频流参数
CHUNK = 1024  # 每次读取的音频帧大小
FORMAT = pyaudio.paInt16  # 音频格式
CHANNELS = 2  # 声道数
RATE = 44100  # 采样率
RECORD_SECONDS = 0.5  # 每次录制的音频时长

# 服务器端处理音频的线程
class Audio_Server(threading.Thread):
    def __init__(self, port, version) :
        threading.Thread.__init__(self)
        self.setDaemon(True) # 将线程设置为守护线程，随主程序退出而退出
        self.ADDR = ('', port) # 定义服务器地址和端口
        if version == 4:
            self.sock = socket(AF_INET ,SOCK_STREAM) # 创建IPv4套接字
        else:
            self.sock = socket(AF_INET6 ,SOCK_STREAM) # 创建IPv6套接字
        self.p = pyaudio.PyAudio() # 创建PyAudio对象，用于音频处理
        self.stream = None # 初始化音频流为None
    def __del__(self):
        self.sock.close() # 关闭套接字
        if self.stream is not None:
            self.stream.stop_stream() # 停止音频流
            self.stream.close() # 关闭音频流
        self.p.terminate() # 终止PyAudio
    def run(self):
        print("AUDIO server starts...")
        self.sock.bind(self.ADDR) # 绑定服务器地址和端口
        self.sock.listen(1) # 开始监听连接请求，允许一个连接
        conn, addr = self.sock.accept() # 接受客户端连接请求
        print("remote AUDIO client success connected...")
        data = "".encode("utf-8") # 初始化数据为空字节串
        payload_size = struct.calcsize("L") # 计算数据包大小
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True,
                                  frames_per_buffer = CHUNK
                                  ) # 打开音频输出流
        while True:
            while len(data) < payload_size:
                data += conn.recv(81920) # 接收数据，直到达到数据包大小
            packed_size = data[:payload_size] # 提取数据包大小
            data = data[payload_size:] # 剩余数据
            msg_size = struct.unpack("L", packed_size)[0] # 解包数据包大小
            while len(data) < msg_size:
                data += conn.recv(81920) # 接收数据，直到达到消息大小
            frame_data = data[:msg_size] # 提取音频数据
            data = data[msg_size:] # 剩余数据
            frames = pickle.loads(frame_data) # 解压音频数据并加载为帧
            for frame in frames:
                self.stream.write(frame, CHUNK) # 写入音频帧到音频输出流

# 客户端发送音频的线程
class Audio_Client(threading.Thread):
    def __init__(self ,ip, port, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)  # 将线程设置为守护线程，随主程序退出而退出
        self.ADDR = (ip, port)  # 定义服务器地址和端口
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)  # 创建IPv4套接字
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)  # 创建IPv6套接字
        self.p = pyaudio.PyAudio()  # 创建PyAudio对象，用于音频处理
        self.stream = None  # 初始化音频流为None
        print("AUDIO client starts...")
    def __del__(self) :
        self.sock.close()  # 关闭套接字
        if self.stream is not None:
            self.stream.stop_stream()  # 停止音频流
            self.stream.close()  # 关闭音频流
        self.p.terminate()  # 终止PyAudio
    def run(self):
        while True:
            try:
                self.sock.connect(self.ADDR)  # 尝试连接服务器
                break
            except:
                time.sleep(3)  # 连接失败后休眠3秒再重试
                continue
        print("AUDIO client connected...")
        self.stream = self.p.open(format=FORMAT,
                             channels=CHANNELS,
                             rate=RATE,
                             input=True,
                             frames_per_buffer=CHUNK)  # 打开音频输入流
        while self.stream.is_active():
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = self.stream.read(CHUNK)  # 从音频输入流读取音频数据
                frames.append(data)  # 将音频数据添加到帧列表中
            senddata = pickle.dumps(frames)  # 压缩并打包音频帧数据
            try:
                self.sock.sendall(struct.pack("L", len(senddata)) + senddata)  # 发送音频数据到服务器
            except:
                break  # 发送失败时退出循环
