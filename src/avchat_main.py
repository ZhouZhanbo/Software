import sys
import time
import argparse
from vchat import Video_Server, Video_Client
from achat import Audio_Server, Audio_Client
# 主函数的逻辑是控制服务端和客户端分别启动，判断是否断开，总共有两个服务端，分别控制视频流和音频流，具体的逻辑在achat.py(音频流)和vchat.py(视频流)中


def vedio_call(IP):
    PORT = 10087
    SHOWME = True
    LEVEL = 1
    VERSION = 4
    # 创建视频客户端和服务器对象
    vclient = Video_Client(IP, PORT, SHOWME, LEVEL, VERSION)
    vserver = Video_Server(PORT, VERSION)
    # 创建音频客户端和服务器对象
    aclient = Audio_Client(IP, PORT + 1, VERSION)
    aserver = Audio_Server(PORT + 1, VERSION)
    # 启动视频客户端、视频服务器、音频客户端和音频服务器
    vclient.start()
    vserver.start()
    aclient.start()
    aserver.start()
    while True:
        time.sleep(1)
        # 如果视频服务器或客户端连接断开，打印错误消息并退出
        if not vserver.is_alive() or not vclient.is_alive():
            print("Video connection lost...")
            sys.exit(0)
        # 如果音频服务器或客户端连接断开，打印错误消息并退出
        if not aserver.is_alive() or not aclient.is_alive():
            print("Audio connection lost...")
            sys.exit(0)


def audio_call(IP):
    PORT = 10087
    VERSION = 4
    # 创建音频客户端和服务器对象
    aclient = Audio_Client(IP, PORT + 1, VERSION)
    aserver = Audio_Server(PORT + 1, VERSION)
    # 启动音频客户端和音频服务器
    aserver.start()
    aclient.start()
    while True:
        time.sleep(1)
        # 如果音频服务器或客户端连接断开，打印错误消息并退出
        if not aserver.is_alive() or not aclient.is_alive():
            print("Audio connection lost...")
            sys.exit(0)


if __name__ == '__main__':
    # vclient = Video_Client(IP, PORT, SHOWME, LEVEL, VERSION)
    # vserver = Video_Server(PORT, VERSION)
    aclient = Audio_Client(IP, PORT+1, VERSION)
    aserver = Audio_Server(PORT+1, VERSION)
    # vclient.start()
    # vserver.start()
    aclient.start()
    aserver.start()
    while True:
        time.sleep(1)
        # if not vserver.is_alive() or not vclient.is_alive():
        #    print("Video connection lost...")
        #    sys.exit(0)
        if not aserver.is_alive() or not aclient.is_alive():
            print("Audio connection lost...")
            sys.exit(0)
