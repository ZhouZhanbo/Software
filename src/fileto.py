# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 19:25:03 2023

@author: 10467
"""
import tkinter
import filego
import chatGUI

# 接受文件
def refe(receiver, sender, file_name ,file_content):
    global t, user
    if sender == user:
        return
    else:tt = filego.Filego(user, sender, file_name, file_content)
   
    tt.close()
    print("已签收到" + sender + "的文件" )


# 发送文件
   