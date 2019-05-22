import sys
import os
import json
import uuid
import datetime
from Queue import *
import glob

class Chat:
	def __init__(self):
		self.sessions={}
		self.users = {}
		self.groups = {}
		self.users['messi']={ 'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'sby', 'incoming' : {}, 'outgoing': {}}
		self.users['henderson']={ 'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'sby', 'incoming': {}, 'outgoing': {}}
		self.users['lineker']={ 'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'sby','incoming': {}, 'outgoing':{}}
	def proses(self,data):
		j=data.strip().split(" ")
		try:
			command=j[0]
			if (command=='auth'):
				username=j[1]
				password=j[2]
                                print "auth {}" . format(username)
				return self.autentikasi_user(username,password)
			elif (command=='send'):
				sessionid = j[1]
				usernameto = j[2]
                                message=""
                                for w in j[3:]:
                                    message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
                                print "send message from {} to {}" . format(usernamefrom,usernameto)
				return self.send_message(sessionid,usernamefrom,usernameto,message)
			elif (command=='send_file'):
				sessionid = j[1]
				usernameto = j[2]
				filename = j[3]
				usernamefrom = self.sessions[sessionid]['username']
				print "send_file from {} to {}" . format(usernamefrom, usernameto)
				return self.send_file(sessionid, usernamefrom, usernameto, filename, connection)

			elif (command=='download_file'):
				sessionid = j[1]
				filename = j[2]
				usernamefrom = self.sessions[sessionid]['username']
				print "{} download_file {}" . format(usernamefrom, filename)
				return self.download_file(sessionid, filename, connection)
                       	elif (command=='inbox'):
                                sessionid = j[1]
                                username = self.sessions[sessionid]['username']
                                print "inbox {}" . format(username)
                                return self.get_inbox(username)
                        elif (command=='logout'):
				sessionid = j[1]
				username = self.sessions[sessionid]['username']
				print "try to logout {}" . format(username)
				return self.logout(sessionid)
			elif (command=='create_group'):
				sessionid = j[1]
				groupname = j[2]
				return self.create_group(sessionid, groupname)
			elif (command=='join_group'):
				sessionid = j[1]
				groupname = j[2]
				return self.join_group(sessionid, groupname)
			elif (command=='sendto_group'):
				sessionid = j[1]
				togroupname = j[2]
				sender = self.sessions[sessionid]['username']
				groupmessage=""
		                for w in j[3:]:
		                   groupmessage="{} {}" . format(groupmessage,w)
		        	print groupmessage
				return self.sendto_group(sender, togroupname, groupmessage)
			else:
				return {'status': 'ERROR', 'message': '**Protocol Tidak Benar'}
		except IndexError:
			return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}
	def autentikasi_user(self,username,password):
		if (username not in self.users):
			return { 'status': 'ERROR', 'message': 'User Tidak Ada' }
 		if (self.users[username]['password']!= password):
			return { 'status': 'ERROR', 'message': 'Password Salah' }
		tokenid = str(uuid.uuid4())
		self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
		return { 'status': 'OK', 'tokenid': tokenid }
	def get_user(self,username):
		if (username not in self.users):
			return False
		return self.users[username]
	def send_message(self,sessionid,username_from,username_dest,message):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)

		if (s_fr==False or s_to==False):
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

		message = {'Type': 'Personal', 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
		outqueue_sender = s_fr['outgoing']
		inqueue_receiver = s_to['incoming']
		try:
			outqueue_sender[username_from].put(message)
		except KeyError:
			outqueue_sender[username_from]=Queue()
			outqueue_sender[username_from].put(message)
		try:
			inqueue_receiver[username_from].put(message)
		except KeyError:
			inqueue_receiver[username_from]=Queue()
			inqueue_receiver[username_from].put(message)
		return {'status': 'OK', 'message': 'Message Sent'}

	def send_file(self, sessionid, username_from, username_dest, filename, connection):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)

		if (s_fr==False or s_to==False):
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

		try:
			if not os.path.exists(username_dest):
				os.makedirs(username_dest)
			with open(os.path.join(username_dest, filename), 'wb') as file:
				while True:
					data = connection.recv(1024)
					print data
					if(data[-4:] == 'DONE'):
						data = data[:-4]
						file.write(data)
						break
					file.write(data)
				file.close()
		except IOError:
			raise

		message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': 'sent/received {}' . format(filename) }
		outqueue_sender = s_fr['outgoing']
		inqueue_receiver = s_to['incoming']
		try:
			outqueue_sender[username_from].put(message)
		except KeyError:
			outqueue_sender[username_from]=Queue()
			outqueue_sender[username_from].put(message)
		try:
			inqueue_receiver[username_from].put(message)
		except KeyError:
			inqueue_receiver[username_from]=Queue()
			inqueue_receiver[username_from].put(message)

		return {'status': 'OK', 'message': 'File sent'}

	def download_file(self, sessionid, filename, connection):
		username = self.sessions[sessionid]['username']
		print "{} download {}" . format(username, filename)

		try:
			file = open(os.path.join(username, filename), 'rb')
		except IOError:
			return {'status': 'Err', 'message': 'File not found'}

		result = connection.sendall("OK")
		while True:
			data = file.read(1024)
			if not data:
				result = connection.sendall("DONE")
				break
			connection.sendall(data)
		file.close()
		return

	def get_inbox(self,username):
		s_fr = self.get_user(username)
		incoming = s_fr['incoming']
		msgs={}
		for users in incoming:
			msgs[users]=[]
			while not incoming[users].empty():
				msgs[users].append(s_fr['incoming'][users].get_nowait())

		return {'status': 'OK', 'messages': msgs}

	def logout(self,sessionid):
		if(sessionid in self.sessions):
			del self.sessions[sessionid]
		return {'status':'OK'}

	def create_group(self, sessionid, groupname):
		if(groupname in self.groups):
			return { 'status': 'ERROR', 'message': 'group sudah ada' }

		admin = self.sessions[sessionid]['username']
		self.groups[groupname] = {'admin':admin, 'users':[]}
		self.groups[groupname]['users'].append(admin)
		return {'status':'OK', 'message': '{} created'.format(groupname)}

	def join_group(self, sessionid, groupname):
		if (groupname not in self.groups):
			return { 'status': 'ERROR', 'message': 'Group tidak ada' }

		member = self.sessions[sessionid]['username']
		self.groups[groupname]['users'].append(member)
		print self.groups[groupname]['users']
		return {'status':'OK', 'message': '{} joined {}'.format(member, groupname)}

	def sendto_group(self, username, togroupname, groupmessage):
		if (togroupname not in self.groups):
			return { 'status': 'ERROR', 'message': 'Group tujuan tidak ada' }

		sender = self.get_user(username)
		if (sender==False):
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

		print groupmessage
		for tousername in self.groups[togroupname]['users']:
			reciever = self.get_user(tousername)
			message = {'Type': 'Group', 'msg_from': sender['nama'], 'msg_to': togroupname, 'msg': groupmessage }
			outqueue_sender = sender['outgoing']
			inqueue_receiver = reciever['incoming']
			try:
				outqueue_sender[username].put(message)
			except KeyError:
				outqueue_sender[username]=Queue()
				outqueue_sender[username].put(message)
			try:
				inqueue_receiver[username].put(message)
			except KeyError:
				inqueue_receiver[username]=Queue()

		return {'status': 'OK', 'message': 'Message Sent'}


if __name__=="__main__":
	j = Chat()
        sesi = j.proses("auth messi surabaya")
	print sesi
	#sesi = j.autentikasi_user('messi','surabaya')
	#print sesi
	tokenid = sesi['tokenid']
	print j.proses("send {} henderson hello gimana kabarnya son " . format(tokenid))
	#print j.send_message(tokenid,'messi','henderson','hello son')
	#print j.send_message(tokenid,'henderson','messi','hello si')
	#print j.send_message(tokenid,'lineker','messi','hello si dari lineker')


	print j.get_inbox('messi')
