---

## 🧠 Smart Kitchen Simulation (Realtime Dashboard + MQTT + Flask-SocketIO)

### 🚀 Giới thiệu

**Smart Kitchen Simulation** là một dự án mô phỏng hệ thống bếp thông minh, nơi các **cảm biến (sensor)** gửi dữ liệu realtime (ví dụ: nhiệt độ, khói, gas, chuyển động, dòng nước...) đến một **dashboard web động**.
Dữ liệu được truyền qua **Flask-SocketIO**, hiển thị trực tiếp mà **không cần reload trang**.
Hệ thống cũng tích hợp **MQTT** để giao tiếp IoT và **Twilio** để gửi cảnh báo khi phát hiện nguy hiểm.

---

## ⚙️ Tính năng chính

| Tính năng                      | Mô tả                                                                              |
| ------------------------------ | ---------------------------------------------------------------------------------- |
| 🔥 **Mô phỏng cảm biến**       | Gas MQ2, Gas MQ5, Smoke + Temperature, Temp + Humidity, Motion + Light, Water Flow |
| ⚡ **Realtime Dashboard**       | Hiển thị dữ liệu cảm biến theo thời gian thực (không cần F5)                       |
| 🌐 **SocketIO + Flask**        | Dùng WebSocket để gửi dữ liệu từ backend ra frontend                               |
| 📡 **MQTT Broker Integration** | Kết nối và publish dữ liệu cảm biến                                                |
| 📞 **Twilio Alert**            | Gửi SMS cảnh báo khi phát hiện sự cố (gas, khói, v.v.)                             |
| 💾 **SQLite Database**         | Lưu log dữ liệu và trạng thái hệ thống                                             |
| 🧩 **Modular Design**          | Code chia module rõ ràng: `sensors/`, `controller/`, `integrations/`, `web/`       |

---

## 🧩 Cấu trúc thư mục

```
smart_kitchen_sim/
│
├── app/
│   ├── __init__.py
│   ├── controller.py          # Bộ xử lý dữ liệu cảm biến
│   ├── sensors.py             # Các lớp mô phỏng cảm biến
│   ├── db.py                  # Khởi tạo & thao tác SQLite
│   ├── integrations.py        # MQTT + Twilio
│   ├── web.py                 # Flask-SocketIO + dashboard server
│   └── ...
│
├── templates/
│   └── dashboard.html         # Giao diện realtime dashboard
│
│
├── config.py                  # Cấu hình hệ thống (MQTT, DB, Twilio,...)
├── main.py                    # File chạy chính
├── requirements.txt           # Các thư viện cần cài
└── README.md                  # File mô tả dự án
```

---

## ⚡ Cài đặt & chạy dự án

### 1️⃣ Clone dự án

```bash
git clone https://github.com/<your-username>/smart_kitchen_sim.git
cd smart_kitchen_sim
```

### 2️⃣ Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# hoặc
source venv/bin/activate  # Linux/macOS
```

### 3️⃣ Cài thư viện

```bash
pip install -r requirements.txt
```

**requirements.txt** nên có:

```
flask
flask-socketio
eventlet
paho-mqtt
twilio
```

---

## ⚙️ 4️⃣ Cấu hình

Mở file **`config.py`** và chỉnh các thông tin phù hợp:

```python
CONFIG_EXT = {
    'db_enabled': True,
    'db_path': 'smart_kitchen.db',
    'mqtt_broker': 'localhost',
    'mqtt_port': 1883,
    'mqtt_topic': 'smart_kitchen/data',
    'twilio_sid': '<TWILIO_SID>',
    'twilio_token': '<TWILIO_TOKEN>',
    'twilio_from': '<YOUR_TWILIO_PHONE>',
    'twilio_to': '<YOUR_PHONE>'
}
```

---

## ▶️ 5️⃣ Chạy dự án

```bash
python main.py
```

Mở trình duyệt:
👉 **[http://localhost:5000/](http://localhost:5000/)**

Bạn sẽ thấy **Dashboard realtime**, nơi dữ liệu cảm biến được cập nhật liên tục (tự động thay đổi mà không cần reload).

---

## 🧠 Luồng hoạt động

1. `main.py` khởi động:

   * Database (`init_db`)
   * MQTT (`init_mqtt`)
   * Twilio (`init_twilio`)
   * Flask web server (`run_http_server`)
2. Các **sensor** chạy vòng lặp bất đồng bộ → gửi dữ liệu vào **queue**
3. `processor()` xử lý dữ liệu và gửi ra MQTT + SocketIO
4. Frontend (HTML) lắng nghe **SocketIO event** để cập nhật giao diện realtime

---

## 📊 Giao diện Dashboard

Dashboard được tạo bằng **Bootstrap + SocketIO JS client**.
Các thông số cảm biến sẽ cập nhật ngay lập tức mỗi khi có dữ liệu mới từ server.

```html
<!-- templates/dashboard.html -->
<h2>Smart Kitchen Dashboard</h2>
<div id="data"></div>

<script src="/socket.io/socket.io.js"></script>
<script>
  const socket = io();
  socket.on('sensor_update', data => {
    document.getElementById('data').innerText = JSON.stringify(data, null, 2);
  });
</script>
```

---

## 🧪 Kiểm tra hoạt động

Bạn có thể mở nhiều trình duyệt khác nhau → tất cả đều thấy dữ liệu **realtime đồng bộ** khi cảm biến thay đổi.

---

## 🧰 Troubleshooting

| Vấn đề                   | Cách khắc phục                                                                                     |
| ------------------------ | -------------------------------------------------------------------------------------------------- |
| Flask không nhận HTML    | Kiểm tra `template_folder="../templates"` trong `app/web.py`                                       |
| Dashboard không realtime | Cài đúng `eventlet` và chạy server bằng `socketio.run(app, host='0.0.0.0', port=5000, debug=True)` |
| MQTT không nhận dữ liệu  | Kiểm tra `mqtt_broker` và topic trong `config.py`                                                  |
| Twilio không gửi SMS     | Kiểm tra `SID`, `token`, và `phone number` hợp lệ                                                  |

---

## 📚 Công nghệ sử dụng

* **Python 3.10+**
* **Flask** – Web Framework
* **Flask-SocketIO** – Realtime communication
* **Eventlet** – Async server engine
* **MQTT (paho-mqtt)** – IoT messaging
* **Twilio API** – SMS alerts
* **SQLite** – Local database

---

## 👨‍💻 Tác giả

**Duy Ân Nguyễn**
📧 Email: (thêm nếu bạn muốn)
📅 Cập nhật: Tháng 10/2025


