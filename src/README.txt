环境设置：
开发环境为PyCharm Community Edition 2023.2.2，

额外模块:pyaudio，numpy，cv2
在终端输入以下命令下载:
pyaudio:pip install pyaudio
numpy:pip install numpy
cv2:pip install opencv-python

运行步骤：
先Run ChatSever.py文件大家服务器进行监听等待客户端接入。
再Run client1.py和client2.py文件两个客户端（多开客户端用于单电脑测试）进入GUI图形界面，
测试群聊功能可复制出第三个client3.py进行测试

注意事项：
1)GUI图形界面中文件传输（未完成）和用户属性（摆设）为无功能按钮
2)若需测试不同设备之间的通信则需获取一个电脑的IP地址并将其作为服务器（在此电脑上也可以开客户端），然后将开客户端电脑上的safelogin.py文件中第八行s.connect(IP,PORT)中的IP地址替换为服务机的IP地址（默认为本地地址127.0.0.1），之后运行步骤为：
先在服务机上run ChatSever.py文件，后再其他电脑上run client1.py即可
3）视频通话和语音通话两个功能无法在window11中使用（或者是我电脑的问题，无法调用摄像头和麦克风）