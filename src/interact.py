import os


# 下面这个类，以两个人之间的聊天为对象，其中u1,u2,指的是两个用户的用户名，message则是聊天记录
class Interact(object):
    def __init__(self, a1, a2):
        self.u1 = a1
        self.u2 = a2
        self.messages = []
        if not os.path.exists("./messages"):
            os.mkdir("./messages")
        else:
            if os.path.exists("./messages/"+self.u1+"__"+self.u2+".txt"):
                doc = open("./messages/"+self.u1+"__"+self.u2+".txt", "r")
                news = doc.readlines()
                for line in news:
                    if "\0" in line:
                        sender, information, time = line.split("\0")
                        self.add_information(sender, information, time[:-1])
                doc.close()
# 生成存放消息的文件夹

    def add_information(self, sender, information, time):
        if len(self.messages) >= 100:
            self.messages.pop(0)
        self.messages.append([sender, information, time])
# 添加聊天记录，可设置一个记录消息的上限，超过上限的部分可以删除

    def del_information(self, sender, information):
        self.messages.remove([sender, information])
# 删除聊天记录，为暂定方案，还未完善

    def show(self):
        n = 0
        while n != len(self.messages):
            print(self.messages[n][0], ':', self.messages[n][1])
            n += 1
# 显示聊天记录，暂时用于程序测试

    def close(self):
        doc = open(file="./messages/" + self.u1 + "__" + self.u2 + ".txt", mode="w")
        while len(self.messages):
            doc.write(self.messages[0][0] + "\0" + self.messages[0][1].replace("\n", "") + "\0" + self.messages[0][2] + "\n")
            self.messages.pop(0)
        doc.close()
        del self


if __name__ == "__main__":
    Try = Interact("user1", "user2")
    Try.show()
    first = input()
    while first != '0':
        Try.add_information(Try.u1, first)
        first = input()
    Try.show()
    Try.close()
