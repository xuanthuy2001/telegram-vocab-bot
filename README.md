# 🤖 Bot Từ Vựng EPS Tiếng Hàn

Gửi **10 từ vựng ngẫu nhiên** mỗi ngày lúc **10:30 giờ Hàn Quốc** (08:30 giờ Việt Nam).

---

## 📁 Cấu trúc thư mục

```
telegram_vocab_bot/
├── bot.py           # Code chính của bot
├── config.py        # Cấu hình token và chat ID
├── vocab.json       # 1314 từ vựng EPS
├── requirements.txt # Thư viện cần cài
└── README.md
```

---

## ⚙️ Cài đặt

### Bước 1: Tạo bot Telegram
1. Mở Telegram, tìm **@BotFather**
2. Gõ `/newbot` → đặt tên → lấy **Bot Token**

### Bước 2: Lấy Chat ID của bạn
1. Tìm **@userinfobot** trên Telegram
2. Gõ `/start` → nó sẽ trả về **ID** của bạn
3. Nếu dùng group: thêm bot vào group, rồi gửi tin nhắn bất kỳ, sau đó truy cập:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
   Tìm trường `"chat": {"id": ...}`

### Bước 3: Điền thông tin vào `config.py`
```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"
CHAT_ID   = "123456789"   # hoặc "-100xxxxxxxxxx" nếu là group
```

### Bước 4: Cài thư viện
```bash
pip install -r requirements.txt
```

### Bước 5: Chạy bot
```bash
python bot.py
```

---

## 💬 Lệnh có sẵn

| Lệnh | Chức năng |
|------|-----------|
| `/start` | Giới thiệu bot |
| `/vocab` | Nhận 10 từ ngay lập tức |
| `/stats` | Xem thống kê từ điển |

---

## 🖥️ Chạy 24/7 trên server (tùy chọn)

### Dùng `screen` (Linux/VPS):
```bash
screen -S vocab_bot
python bot.py
# Nhấn Ctrl+A rồi D để thoát, bot vẫn chạy nền
```

### Dùng `systemd` service (ổn định hơn):
```ini
# /etc/systemd/system/vocab_bot.service
[Unit]
Description=Telegram Vocab Bot
After=network.target

[Service]
WorkingDirectory=/path/to/telegram_vocab_bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable vocab_bot
sudo systemctl start vocab_bot
```

---

## ⏰ Lịch gửi

| Múi giờ | Giờ gửi |
|---------|---------|
| 🇰🇷 Hàn Quốc (KST) | 10:30 |
| 🇻🇳 Việt Nam (ICT) | 08:30 |
| 🌐 UTC | 01:30 |

---

## 📊 Thông tin từ điển

- **Tổng số từ:** 1.314 từ vựng EPS
- **Nguồn:** Google Docs của bạn
- **Mỗi ngày:** 10 từ ngẫu nhiên không lặp lại trong ngày

---

*Made with ❤️ — Chúc bạn học tốt tiếng Hàn!*
