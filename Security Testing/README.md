# Python Client-Server 資安實作

> **基於 Python Socket 之遠端系統管理與安全測試工具**

本專案起源於「駭客攻防」課程，為了理解遠端控制工具背後的運作原理，我使用 **Python 建立 Client-Server 架構**，並於 **Kali Linux ↔ Windows 虛擬化靶機**環境進行測試。

##  我做了什麼？

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
```

##  核心技術

- **Python / TCP Socket**：建立 Client-Server 通訊
- **JSON / UTF-8 / Base64**：處理不同類型資料傳輸
- **subprocess**：執行 Windows 系統指令
- **mss**：螢幕擷取
- **pynput**：鍵盤事件測試
- **PyInstaller**：程式打包與部署

##  我解決了什麼問題？

實作過程中自行處理：

- 防止被刪掉增加註冊機碼的編寫
  <img width="1090" height="619" alt="image" src="https://github.com/user-attachments/assets/59452558-9299-463c-99e6-cbceeb503e72" />

  <img width="1028" height="422" alt="image" src="https://github.com/user-attachments/assets/97a894b8-16c6-4240-9fda-05a1746e984a" />
- PyInstaller 第三方函式庫的缺失問題
  <img width="597" height="193" alt="image" src="https://github.com/user-attachments/assets/8a578db9-7930-453a-ad8b-af152b3bf8dd" />
  <img width="565" height="331" alt="image" src="https://github.com/user-attachments/assets/68976d84-f647-4c2a-9676-91bbb75f80d9" />
  
  手動加註打包

- Client 連線失敗後的自動重新連線
- 文字、JSON、檔案、圖片等不同資料型態的傳輸

##  最大收穫

這次實作讓我從「**使用資安工具**」進一步做到「**理解並自行建立工具背後的運作方式**」。

透過實際撰寫 Socket、處理資料傳輸與除錯，我建立了 **Python 網路程式設計、Windows 系統操作、端點安全與資安攻防**的實作經驗。

> **測試環境：Kali Linux + Windows Virtual Machine**  
> **用途：資安學習、研究與授權測試**
