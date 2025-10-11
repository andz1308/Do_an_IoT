import os
import time
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from threading import Lock
from app.controller import shared_state

# --- Tạo Flask app
app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "smarthome-secret")

# --- SocketIO realtime
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
thread_lock = Lock()

# --- Hàm nền để phát dữ liệu định kỳ tới client
def background_broadcast():
    while True:
        socketio.sleep(2)  # mỗi 2s gửi cập nhật 1 lần
        data = {
            "last_update": shared_state.get("last_update"),
            "sensors": shared_state.get("sensors"),
            "actuators": shared_state.get("actuators"),
            "alerts": shared_state.get("alerts", [])[:5],
        }
        socketio.emit("update_state", data)


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/status")
def status_json():
    """Trả dữ liệu JSON (cho API hoặc debug)"""
    return jsonify(shared_state)


@socketio.on("connect")
def handle_connect():
    """Khi client kết nối, gửi ngay dữ liệu hiện tại"""
    print("🔌 Client đã kết nối")
    socketio.emit("update_state", {
        "sensors": shared_state.get("sensors"),
        "actuators": shared_state.get("actuators"),
        "alerts": shared_state.get("alerts", [])
    })


def run_http_server():
    """Khởi chạy Flask server realtime"""
    with thread_lock:
        socketio.start_background_task(background_broadcast)
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
    return app
