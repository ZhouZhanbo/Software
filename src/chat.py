import tkinter
import interact
import chatGUI


# 发送消息，发送给服务器消息
def send(time):
    global t, user
    if not chatGUI.a.get("1.0", "end"):
        print("error")
        return

    t.add_information(user, chatGUI.a.get("1.0", "end"), time)
    chatGUI.a.delete("1.0", "end")
    chatGUI.listbox.insert(tkinter.END, "\n" + t.messages[-1][2], 'blue')
    chatGUI.listbox.insert(tkinter.END, "\n" + t.messages[-1][0] + ":" + t.messages[-1][1].replace("\n", ""), 'blue')
    if __name__ == '__main__':
        t.show()


# 接受消息，接受消息添加到对应的文件里，并显示
def revc(receiver, sender, message, time):
    if sender == user:
        return
    if (t.u2 == "all_user" and receiver == "all_user") or (t.u2 == sender and receiver != "all_user"):
        t.add_information(sender, message, time)
        chatGUI.listbox.insert(tkinter.END, "\n" + t.messages[-1][2], 'black')
        chatGUI.listbox.insert(tkinter.END, "\n" + sender + ":" + t.messages[-1][1].replace("\n", ""), 'black')
    else:
        if receiver == "all_user":
            tt = interact.Interact(user, "all_user")
        else:
            tt = interact.Interact(user, sender)
        tt.add_information(sender, message, time)
        tt.close()
    print("已接收到" + sender + "的消息")


# 创建聊天界面
def create_chat():
    global t
    t.close()
    chatGUI.user = user
    chatGUI.create_chatGUI()
    t = interact.Interact(user, "all_user")
    for lines in t.messages:
        if lines[0] == user:
            chatGUI.listbox.insert(tkinter.END, lines[2] + "\n", 'blue')
            chatGUI.listbox.insert(tkinter.END, lines[0] + ":" + lines[1] + "\n", 'blue')
        else:
            chatGUI.listbox.insert(tkinter.END, lines[2] + "\n", 'black')
            chatGUI.listbox.insert(tkinter.END, lines[0] + ":" + lines[1] + "\n", 'black')
    chatGUI.listbox1.bind("<ButtonRelease-1>", create_private_chat)


# 在主界面显示对应的聊天记录，在点击对应私聊用户后需要调用，在create_chat里已经关联
def create_private_chat(*args):
    global user, t, chat
    indexs = chatGUI.listbox1.curselection()
    print(indexs)
    index = -1
    if len(indexs) > 0:
        index = indexs[0]
    if index >= 0:
        chat = chatGUI.listbox1.get(index)
        print(chat)
        if t.u1 == user:
            t.close()   # 关闭上一个私聊
        t = interact.Interact(user, chat)
        chatGUI.listbox.delete(1.0, "end")
        for lines in t.messages:
            if lines[0] == user:
                chatGUI.listbox.insert(tkinter.END, lines[2] + "\n", 'blue')
                chatGUI.listbox.insert(tkinter.END, lines[0] + ":" + lines[1] + "\n", 'blue')
            else:
                chatGUI.listbox.insert(tkinter.END, lines[2] + "\n", 'black')
                chatGUI.listbox.insert(tkinter.END, lines[0] + ":" + lines[1] + "\n", 'black')
    chatGUI.listbox1.itemconfigure((chatGUI.listbox1.curselection()[0]), bg="white")

# 显示用户
def show_users(users):
    chatGUI.listbox1.delete(0, "end")
    chatGUI.listbox1.insert("end", "all_user")
    for use in users:
        if use != user:
            chatGUI.listbox1.insert("end", use)
    chatGUI.listbox1.select_set(0)

user = "user"
chat = "all_user"
t = interact.Interact(user, "all_user")
