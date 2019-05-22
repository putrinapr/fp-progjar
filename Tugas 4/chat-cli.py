import socket
import os
import json
import datetime

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8883


class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""
        self.username=""
    def proses(self,cmdline):
	j=cmdline.strip().split(" ")
	try:
	    command=j[0]
	    if (command=='auth'):
		username=j[1]
		password=j[2]
		return self.login(username,password)
	    elif (command=='send'):
		usernameto = j[1]
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
		return self.sendmessage(usernameto,message)
            elif (command=='inbox'):
                return self.inbox()
            elif (command == 'send_file'):
                usernameto = j[1]
                filename = j[2]
                return self.send_file(usernameto, filename)
            elif (command == 'download_file'):
                filename = j[1]
                return self.download_file(filename)
            elif (command=='logout'):
                return self.logout()
            elif (command=='create_group'):
                groupname = j[1]
                return self.create_group(groupname)
            elif (command=='join_group'):
                groupname = j[1]
                return self.join_group(groupname)
            elif (command=='sendto_group'):
                togroupname = j[1]
                groupmessage=""
                for w in j[2:]:
                   groupmessage="{} {}" . format(groupmessage,w)
                return self.sendto_group(togroupname, groupmessage)
	    else:
		return "*Maaf, command tidak benar"
	except IndexError:
	    return "-Maaf, command tidak benar"
    def sendstring(self,string):
        try:
            self.sock.sendall(string)
            receivemsg = ""
            while True:
                data = self.sock.recv(10)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data)
                    if receivemsg[-4:]=="\r\n\r\n":
                        return json.loads(receivemsg)
        except:
            self.sock.close()
    def login(self,username,password):
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            self.username = username
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])
    def send_file(self, usernameto, filename):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send_file {} {} {} \r\n" . format(self.tokenid, usernameto, filename)
        self.sock.sendall(string)

        try:
            with open(filename, 'rb') as file:
                while True:
                    bytes = file.read(1024)
                    if not bytes:
                        result = self.sendstring("DONE")
                        break
                    self.sock.sendall(bytes)
                file.close()
        except IOError:
            return "Error, file not found"

        if result['status']=='OK':
            return "file sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])

    def download_file(self, filename):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="download_file {} {} \r\n" . format(self.tokenid, filename)
        self.sock.sendall(string)

        data = self.sock.recv(1024)

        if data[:2]=='OK':
            print data
            now = datetime.datetime.now()
            seconds = (now - datetime.datetime(2019, 1, 1)).total_seconds()
            file =  open(str(int(seconds)) + filename, 'wb')
            if(file):
                file.write(data[2:])
                while True:
                    data = self.sock.recv(1024)
                    if(data[-4:] == 'DONE'):
                        data = data[:-4]
                        file.write(data)
                        break
                    file.write(data)
                file.close()
            else:
                return "Error, something happened"
        else:
            return "Error, file not found"


    def logout(self):
        if (self.tokenid==""):
            return "you're not login"
        string="logout {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=""
            self.username=""
            return "logout success"
        else:
            return "Error, {}" . format(result['message'])

    def create_group(self, groupname):
        if (self.tokenid==""):
            return "you're not login"
        string = "create_group {} {} \r\n" . format(self.tokenid, groupname)
        result = self.sendstring(string)

        if result['status']=='OK':
            return "{}" . format(result['message'])
        else:
            return "Error, {}" . format(json.dumps(result['message']))

    def join_group(self, groupname):
        if (self.tokenid==""):
            return "you're not login"
        string = "join_group {} {}\r\n" . format(self.tokenid, groupname)
        result = self.sendstring(string)

        if result['status']=='OK':
            return "{}" . format(result['message'])
        else:
            return "Error, {}" . format(json.dumps(result['message']))

    def sendto_group(self, togroupname, groupmessage):
        if (self.tokenid==""):
            return "you're not login"
        string = "sendto_group {} {} {}\r\n" . format(self.tokenid, togroupname, groupmessage)
        result = self.sendstring(string)

        if result['status']=='OK':
            return "{}" . format(result['message'])
        else:
            return "Error, {}" . format(json.dumps(result['message']))


if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = raw_input("Command {}:" . format(cc.username))
        print cc.proses(cmdline)

