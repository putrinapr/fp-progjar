import socket
import os
import json
import base64

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889


class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP, TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid = ""
        self.username = ""

    def proses(self, cmdline):
        j = cmdline.strip().split(" ")
        try:
            command = j[0]
            if (command == 'auth'):
                username = j[1]
                password = j[2]
                return self.login(username, password)
            elif (command == 'send'):
                usernameto = j[1]
                message = ""
                for w in j[2:]:
                    message = "{} {}" . format(message, w)
                return self.sendmessage(usernameto, message)
            elif (command == 'inbox'):
                return self.inbox()
            elif (command == 'logout'):
                return self.logout()
            elif (command == 'create_group'):
                groupname = j[1]
                return self.create_group(groupname)
            elif (command == 'join_group'):
                groupname = j[1]
                return self.join_group(groupname)
            elif (command == 'sendto_group'):
                togroupname = j[1]
                groupmessage = ""
                for w in j[2:]:
                    groupmessage = "{} {}" . format(groupmessage, w)
                return self.sendto_group(togroupname, groupmessage)
            elif (command == 'sendimgto_group'):
                togroupname = j[1]
                filename = j[2]
                return self.send_img_to_group(togroupname, filename)
            elif (command == 'send_img'):
                usernameto = j[1]
                filename = j[2]
                return self.send_img(usernameto, filename)
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
            return "-Maaf, command tidak benar"

    def sendstring(self, string):
        try:
            self.sock.sendall(string)
            receivemsg = ""
            while True:
                data = self.sock.recv(10)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg, data)
                    if receivemsg[-4:] == "\r\n\r\n":
                        return json.loads(receivemsg)
        except:
            self.sock.close()

    def login(self, username, password):
        string = "auth {} {} \r\n" . format(username, password)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            self.tokenid = result['tokenid']
            self.username = username
            return "username {} logged in, token {} " .format(username, self.tokenid)
        else:
            return "Error, {}" . format(result['message'])

    def sendmessage(self, usernameto="xxx", message="xxx"):
        if (self.tokenid == ""):
            return "Error, not authorized"
        string = "send {} {} {} \r\n" . format(
            self.tokenid, usernameto, message)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])

    def inbox(self):
        if (self.tokenid == ""):
            return "Error, not authorized"
        string = "inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            for msg in result['messages']:
                if (msg['Type'] == "Personal_Image"):
                    self.store_file(msg['filename'], msg['file'])
                elif (msg['Type'] == "Group_Image"):
                    self.store_file(msg['filename'], msg['file'])
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])

    def logout(self):
        if (self.tokenid == ""):
            return "you're not login"
        string = "logout {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            self.tokenid = ""
            self.username = ""
            return "logout success"
        else:
            return "Error, {}" . format(result['message'])

    def create_group(self, groupname):
        if (self.tokenid == ""):
            return "you're not login"
        string = "create_group {} {} \r\n" . format(self.tokenid, groupname)
        result = self.sendstring(string)

        if result['status'] == 'OK':
            return "{}" . format(result['message'])
        else:
            return "Error, {}" . format(json.dumps(result['message']))

    def join_group(self, groupname):
        if (self.tokenid == ""):
            return "you're not login"
        string = "join_group {} {}\r\n" . format(self.tokenid, groupname)
        result = self.sendstring(string)

        if result['status'] == 'OK':
            return "{}" . format(result['message'])
        else:
            return "Error, {}" . format(json.dumps(result['message']))

    def sendto_group(self, togroupname, groupmessage):
        if (self.tokenid == ""):
            return "you're not login"
        string = "sendto_group {} {} {}\r\n" . format(
            self.tokenid, togroupname, groupmessage)
        result = self.sendstring(string)

        if result['status'] == 'OK':
            return "{}" . format(result['message'])
        else:
            return "Error, {}" . format(json.dumps(result['message']))

    def send_img(self, usernameto, filename):
        if (self.tokenid == ""):
            return "you're not login"
        string = "sendimg {} {} {} {}\r\n" . format(
            self.tokenid, usernameto, filename, self.file_to_b64(filename))
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])

    def send_img_to_group(self, togroupname, filename):
        if (self.tokenid == ""):
            return "you're not login"
        string = "sendimgto_group {} {} {} {}\r\n" . format(
            self.tokenid, togroupname, filename, self.file_to_b64(filename))
        result = self.sendstring(string)

        if result['status'] == 'OK':
            return "{}" . format(result['message'])
        else:
            return "Error, {}" . format(json.dumps(result['message']))

    def store_file(self, filename, b64):
        fh = open(filename, "wb")
        fh.write(b64.decode('base64'))
        fh.close()

    def file_to_b64(self, filename):
        with open(filename, "rb") as imageFile:
            strs = base64.b64encode(imageFile.read())
            return strs


if __name__ == "__main__":
    cc = ChatClient()
    while True:
        cmdline = raw_input("Command {}:" . format(cc.username))
        print cc.proses(cmdline)
