# Python Client-Server 資安實作

> **基於 Python Socket 之遠端系統管理與安全測試工具**

本專案起源於「駭客攻防」課程，為了理解遠端控制工具背後的運作原理，我使用 **Python 自行建立 Client-Server 架構**，並於 **Kali Linux ↔ Windows 虛擬化靶機**環境進行測試。

## 🏗️ 我做了什麼？

```text
Kali Linux
Python Server
      │
      │ TCP Socket
      ▼
Windows Client
      │
      ├─ 遠端指令執行
      ├─ 系統資訊蒐集
      ├─ 檔案 Upload / Download
      ├─ 遠端螢幕截圖
      ├─ Clipboard 測試
      └─ Keyboard Event 測試
