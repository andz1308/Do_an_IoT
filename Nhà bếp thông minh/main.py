import asyncio
import threading
import logging
from config import CONFIG_EXT
from app.sensors import (
    GasSensorMQ2,
    GasSensorMQ5,
    SmokeTempSensor,
    TempHumiditySensor,
    MotionLightSensor,
    WaterFlowSensor,
)
from app.controller import processor
from app.db import init_db
from app.integrations import init_mqtt, init_twilio
from app.web import run_http_server, socketio  # <— thêm socketio nếu bạn dùng Flask-SocketIO

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")


if __name__ == "__main__":
    # --- 1. Khởi tạo cơ sở dữ liệu & tích hợp ngoài
    init_db(CONFIG_EXT.get("db_path", "smart_kitchen.db"), CONFIG_EXT.get("db_enabled", True))
    init_mqtt(CONFIG_EXT)
    init_twilio(CONFIG_EXT)

    # --- 2. Chạy Flask server trong luồng riêng
    t = threading.Thread(target=lambda: socketio.run(run_http_server(), host="0.0.0.0", port=5000), daemon=True)
    t.start()

    # --- 3. Hàm chính chạy các cảm biến
    async def main_loop():
        q = asyncio.Queue()

        sensors = [
            GasSensorMQ2("mq2", 1.0),
            GasSensorMQ5("mq5", 1.2),
            SmokeTempSensor("smoke_temp", 1.0),
            TempHumiditySensor("temp_humidity", 3.0),
            MotionLightSensor("motion_light", 0.8),
            WaterFlowSensor("water_flow", 1.0),
        ]

        tasks = [asyncio.create_task(s.run(q)) for s in sensors]
        tasks.append(asyncio.create_task(processor(q)))

        await asyncio.gather(*tasks)

    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logging.info("🛑 Dừng bởi người dùng")
