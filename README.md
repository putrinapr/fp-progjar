# Final Project Pemrograman Jaringan F

Anggota Kelompok :
* Ivanda Zevi Amalia - 05111640000041
* Putri Nurul Aprilliandini - 05111640000090
* Falah Nurli Filano - 05111640000122

## To Do List :
* Membuat spesifikasi protocol
* Menambahkan protocol untuk aktifitas tambahan
	* Logout
	* Group Messaging
	* Send/Receive File/Image
* Impelementasi dengan GUI (opsional)

## Spesifikasi Protocol
Login
```sh
auth [username] [password]
```

Send Message
```sh
send [username] [message]
```

Check Inbox
```sh
inbox
```

Logout
```sh
logout
```

Create Group
```sh
create_group [groupname]
```

Join Group
```sh
join_group [groupname]
```

Send Group Message
```sh
sendto_group [groupname] [message]
```

Send File
```sh
send_file [username] [filename]
```
