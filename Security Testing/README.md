# Python Client-Server 資安實作

> **基於 Python Socket 之遠端系統管理與安全測試工具**

本專案起源於「駭客攻防」課程，為了理解遠端控制工具背後的運作原理，我使用 **Python 建立 Client-Server 架構**，並於 **Kali Linux ↔ Windows 虛擬化靶機**環境進行測試。

##  簡易流程

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
  <img width="525" height="440" alt="image" src="https://github.com/user-attachments/assets/625607d8-1ee7-4c8d-a510-e410061d4aab" />
  <img width="503" height="472" alt="image" src="https://github.com/user-attachments/assets/bc56cb44-d79b-4891-b67b-3969a6daa095" />

- **JSON / UTF-8 / Base64**：處理不同類型資料傳輸
- **subprocess**：執行 Windows 系統指令
- **mss**：螢幕擷取
- **pynput**：鍵盤事件測試
- **PyInstaller**：程式打包與部署

##  問題與解決

- 防止被刪掉增加註冊機碼的編寫
  <img width="1090" height="619" alt="image" src="https://github.com/user-attachments/assets/59452558-9299-463c-99e6-cbceeb503e72" />

  <img width="1028" height="422" alt="image" src="https://github.com/user-attachments/assets/97a894b8-16c6-4240-9fda-05a1746e984a" />
- PyInstaller 第三方函式庫的缺失問題
  <img width="597" height="193" alt="image" src="https://github.com/user-attachments/assets/8a578db9-7930-453a-ad8b-af152b3bf8dd" />
  <img width="565" height="331" alt="image" src="https://github.com/user-attachments/assets/68976d84-f647-4c2a-9676-91bbb75f80d9" />
  
  手動加註打包

- Client 連線失敗後的自動重新連線
  <img width="956" height="550" alt="image" src="https://github.com/user-attachments/assets/399424c2-0f90-41cb-9a47-6c124d406854" />


- 文字、JSON、檔案、圖片等不同資料型態的傳輸
##  實際成果
遠端啟動
<img width="1090" height="289" alt="image" src="https://github.com/user-attachments/assets/5b3302dd-9936-4302-8e5d-d2f9a8a9fb7d" />
遠端截圖
<img width="618" height="581" alt="image" src="https://github.com/user-attachments/assets/a71108de-7176-40bb-ab7e-1772654b1e32" />
鍵盤紀錄
<img width="1089" height="317" alt="image" src="https://github.com/user-attachments/assets/35c68fff-726d-4ab8-b87f-c4469cacd0c9" />
功能清單
<img width="1090" height="628" alt="image" src="https://github.com/user-attachments/assets/71ca68c2-9dbd-4d38-83c4-d7ce2656ee8a" />
剪貼簿監控
<img width="536" height="277" alt="image" src="https://github.com/user-attachments/assets/1d79d080-fd8f-4f44-82b9-c2db7902d5e1" />
系統資訊蒐集
<img width="1090" height="564" alt="image" src="https://github.com/user-attachments/assets/03fc9a41-f415-4925-a2ff-a040a40fe0a2" />

##  收穫

這次實作讓我從「**使用資安工具**」進一步做到「**理解並建立工具背後的運作方式**」。

透過實際撰寫 Socket、處理資料傳輸與除錯，我建立了 **Python 網路程式設計、Windows 系統操作、端點安全與資安攻防**的實作經驗。

> **測試環境：Kali Linux + Windows Virtual Machine**  
> **用途：資安學習、研究與授權測試**
