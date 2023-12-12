import tkinter as tk
from tkinter import scrolledtext
import chat
# 全局变量
user = "user"
root = []
listbox = []
listbox1 = []
a = []
entry = []
# 聊天界面创建
def create_chatGUI():
    global user, root, listbox, listbox1, a
    root = tk.Tk()
    root.title("hust网络聊天室")  # 窗口命名为用户名
    root['height'] = 450
    root['width'] = 580
    root.resizable(0, 0)  # 限制窗口大小
    # 更改logo
    root.iconphoto(False, tk.PhotoImage(file='icon/logo.png'))
    # 创建多行文本框
    listbox = scrolledtext.ScrolledText(root)
    listbox.place(x=5, y=0, width=570, height=320)
    # 文本框使用的字体颜色
    listbox.tag_config('red', foreground='red')
    listbox.tag_config('blue', foreground='blue')
    listbox.tag_config('green', foreground='green')
    listbox.tag_config('pink', foreground='pink')
    listbox.insert(tk.END, '欢迎加入聊天室(默认为群聊) ！', 'red')

    # 列表动，滚动条跟着动
    listbox1 = tk.Listbox(root)
    # 创建多行文本框, 显示在线用户
    listbox1.place(x=445, y=0, width=130, height=320)
    # 创建用户列表的滚动条
    sc1 = tk.Scrollbar(listbox1)
    sc1.pack(side=tk.RIGHT,  fill=tk.Y)
    # 滚动条动，列表跟着动
    sc1.config(command=listbox1.yview)

    # 创建输入文本框和关联变量
    a = tk.Text(root)
    a.delete("1.0", "end")
    a.place(x=5, y=350, width=570, height=100)

    # 关闭窗口按钮
    but1 = tk.Button(a, text='关闭', command=root.destroy, font=15)
    but1.place(x=445, y=60, width=50, height=30)
    # 传输文件按钮
    global pic2
    photo2 = tk.PhotoImage(file="icon/file.png")
    pic2 = photo2.subsample(5, 5)
    but2 = tk.Button(root, text="文件传输", command="", image=pic2, compound=tk.LEFT, height=18)
    but2.place(x=10, y=322)
    # 语音聊天按钮
    global pic3
    photo3 = tk.PhotoImage(file="icon/voice.png")
    pic3 = photo3.subsample(5, 5)
    but3 = tk.Button(root, text="语音聊天", command="", image=pic3, compound=tk.LEFT, height=18)
    but3.place(x=95, y=322)
    # 视频聊天按钮
    global pic4
    photo4 = tk.PhotoImage(file="icon/video.png")
    pic4 = photo4.subsample(5, 5)
    but4 = tk.Button(root, text="视频聊天", command="", image=pic4, compound=tk.LEFT, height=18)
    but4.place(x=180, y=322)
    # 用户属性按钮
    global pic5
    photo5 = tk.PhotoImage(file="icon/user.png")
    pic5 = photo5.subsample(5, 5)
    but4 = tk.Button(root, text="用户属性", command="", image=pic5, compound=tk.LEFT, height=18)
    but4.place(x=485, y=322)