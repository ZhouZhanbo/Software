from socket import *
import threading
import cv2
import sys
import struct
import pickle
import time
import zlib
import numpy as np

# 定义视频服务器的类，继承自线程类
class Video_Server(threading.Thread):
    def __init__(self, port, version) :
        threading.Thread.__init__(self)
        self.setDaemon(True)  # 将线程设置为守护线程，随主程序退出而退出
        self.ADDR = ('', port)  # 定义服务器地址和端口
        if version == 4:
            self.sock = socket(AF_INET ,SOCK_STREAM)  # 创建IPv4套接字
        else:
            self.sock = socket(AF_INET6 ,SOCK_STREAM)  # 创建IPv6套接字
    def __del__(self):
        self.sock.close()  # 关闭套接字
        try:
            cv2.destroyAllWindows()  # 尝试关闭OpenCV窗口
        except:
            pass
    def run(self):
        print("VEDIO server starts...")
        self.sock.bind(self.ADDR)  # 绑定服务器地址和端口
        self.sock.listen(1)  # 开始监听连接请求，允许一个连接
        conn, addr = self.sock.accept()  # 接受客户端连接请求
        print("remote VEDIO client success connected...")
        data = "".encode("utf-8")  # 初始化数据为空字节串
        payload_size = struct.calcsize("L")  # 计算数据包大小
        cv2.namedWindow('Remote', cv2.WINDOW_NORMAL)  # 创建OpenCV窗口
        while True:
            while len(data) < payload_size:
                data += conn.recv(81920)  # 接收数据，直到达到数据包大小
            packed_size = data[:payload_size]  # 提取数据包大小
            data = data[payload_size:]  # 剩余数据
            msg_size = struct.unpack("L", packed_size)[0]  # 解包数据包大小
            while len(data) < msg_size:
                data += conn.recv(81920)  # 接收数据，直到达到消息大小
            zframe_data = data[:msg_size]  # 提取压缩后的视频帧数据
            data = data[msg_size:]  # 剩余数据
            frame_data = zlib.decompress(zframe_data)  # 解压视频帧数据
            frame = pickle.loads(frame_data)  # 加载视频帧数据
            cv2.imshow('Remote', frame)  # 显示视频帧
            if cv2.waitKey(1) & 0xFF == 27:
                break  # 检测是否按下Esc键，如果是则退出循环

# 定义视频客户端的类，继承自线程类
class Video_Client(threading.Thread):
    def __init__(self ,ip, port, showme, level, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)  # 将线程设置为守护线程，随主程序退出而退出
        self.ADDR = (ip, port)  # 定义服务器地址和端口
        self.showme = showme  # 是否显示本地视频流
        if level == 0:
            self.interval = 0
        elif level == 1:
            self.interval = 1
        elif level == 2:
            self.interval = 2
        else:
            self.interval = 3
        self.fx = 1 / (self.interval + 1)  # 视频帧缩放比例，控制帧的数量
        if self.fx < 0.3:
            self.fx = 0.3
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)  # 创建IPv4套接字
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)  # 创建IPv6套接字
        self.cap = cv2.VideoCapture(0)  # 打开本地摄像头
        print("VEDIO client starts...")
    def __del__(self) :
        self.sock.close()  # 关闭套接字
        self.cap.release()  # 释放摄像头资源
        if self.showme:
            try:
                cv2.destroyAllWindows()  # 尝试关闭OpenCV窗口
            except:
                pass
    def run(self):
        while True:
            try:
                self.sock.connect(self.ADDR)  # 尝试连接服务器
                break
            except:
                time.sleep(3)  # 连接失败后休眠3秒再重试
                continue
        if self.showme:
            cv2.namedWindow('You', cv2.WINDOW_NORMAL)  # 创建OpenCV窗口用于显示本地视频
        print("VEDIO client connected...")
        while self.cap.isOpened():
            ret, frame = self.cap.read()  # 读取本地摄像头帧
            if self.showme:
                cv2.imshow('You', frame)  # 显示本地视频帧
                if cv2.waitKey(1) & 0xFF == 27:  # 检测是否按下Esc键，如果是则关闭本地视频窗口
                    self.showme = False
                    cv2.destroyWindow('You')
            sframe = cv2.resize(frame, (0,0), fx=self.fx, fy=self.fx)  # 调整帧的大小
            data = pickle.dumps(sframe)  # 序列化帧数据
            zdata = zlib.compress(data, zlib.Z_BEST_COMPRESSION)  # 压缩帧数据
            try:
                self.sock.sendall(struct.pack("L", len(zdata)) + zdata)  # 发送压缩后的帧数据到服务器
            except:
                break
            for i in range(self.interval):
                self.cap.read()  # 丢弃指定数量的帧以降低传输频率
