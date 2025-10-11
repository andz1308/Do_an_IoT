import asyncio
import time, logging, random
from app.integrations import mqtt_publish, send_email_async, send_sms_async
from app.db import insert_alert
from config import CONFIG, CONFIG_EXT

# Import socketio để phát realtime
try:
    from app.web import socketio
except Exception:
    socketio = None

shared_state = {
    'sensors': {},
    'actuators': {
        'kitchen_light': False,
        'water_valve_open': False,
        'alarm_buzzer': False,
    },
    'alerts': [],
    'last_update': None,
}

def emit_state_update():
    """Phát dữ liệu realtime lên giao diện"""
    if socketio:
        socketio.emit('state_update', shared_state)

def emit_alert(alert):
    """Phát cảnh báo realtime"""
    if socketio:
        socketio.emit('alert', alert)

def trigger_alert(text):
    ts = time.time()
    logging.warning(text)
    alert = {'time': ts, 'text': text}
    shared_state['alerts'].insert(0, alert)
    if len(shared_state['alerts']) > 200:
        shared_state['alerts'].pop()
    insert_alert(ts, text)
    mqtt_publish(CONFIG_EXT.get('mqtt_base_topic', 'smartkitchen'), 'alerts', alert)
    send_email_async(CONFIG_EXT, 'SmartKitchen - CẢNH BÁO', f"{text}\nThời gian: {time.ctime(ts)}")
    send_sms_async(CONFIG_EXT, f"SmartKitchen - CẢNH BÁO: {text}")

    emit_alert(alert)        # 👉 gửi realtime đến web
    emit_state_update()      # 👉 cập nhật trạng thái tổng thể

def trigger_action(text):
    ts = time.time()
    logging.info(text)
    alert = {'time': ts, 'text': 'HÀNH ĐỘNG: ' + text}
    shared_state['alerts'].insert(0, alert)
    insert_alert(ts, alert['text'])
    mqtt_publish(CONFIG_EXT.get('mqtt_base_topic', 'smartkitchen'), 'actions', alert)

    emit_alert(alert)        # 👉 gửi realtime
    emit_state_update()

async def processor(in_queue: 'asyncio.Queue'):
    last_motion_time = 0
    leak_window = []
    leak_window_maxlen = 10

    while True:
        msg = await in_queue.get()
        sensor = msg['sensor']
        data = msg['data']
        ts = msg['time']
        shared_state['last_update'] = ts
        shared_state['sensors'][sensor] = {'time': ts, 'data': data}

        mqtt_publish(CONFIG_EXT.get('mqtt_base_topic', 'smartkitchen'),
                     f'sensors/{sensor}', {'time': ts, 'sensor': sensor, 'data': data})

        # === Xử lý cảm biến MQ-2 ===
        if sensor == 'mq2':
            ppm = data['ppm']
            if ppm >= CONFIG['mq2_threshold_ppm']:
                trigger_alert(f"CẢNH BÁO: Rò rỉ khí (MQ-2) - mức {ppm} ppm")
                shared_state['actuators']['alarm_buzzer'] = True
            else:
                shared_state['actuators']['alarm_buzzer'] = False

        # === MQ-5 ===
        elif sensor == 'mq5':
            ppm = data['ppm']
            if ppm >= CONFIG['mq5_threshold_ppm']:
                trigger_alert(f"CẢNH BÁO: Rò rỉ khí (MQ-5) - mức {ppm} ppm")
                shared_state['actuators']['alarm_buzzer'] = True
            else:
                shared_state['actuators']['alarm_buzzer'] = False

        # === Cảm biến khói & nhiệt độ ===
        elif sensor == 'smoke_temp':
            smoke = data['smoke']
            temp = data['temp_c']
            if smoke >= CONFIG['smoke_threshold'] or temp >= CONFIG['fire_temp_threshold_c']:
                trigger_alert(f"CẢNH BÁO CHÁY: khói={smoke}, nhiệt độ={temp}°C")
                shared_state['actuators']['alarm_buzzer'] = True
            else:
                mq2_ppm = shared_state['sensors'].get('mq2', {}).get('data', {}).get('ppm', 0)
                mq5_ppm = shared_state['sensors'].get('mq5', {}).get('data', {}).get('ppm', 0)
                if mq2_ppm < CONFIG['mq2_threshold_ppm'] and mq5_ppm < CONFIG['mq5_threshold_ppm']:
                    shared_state['actuators']['alarm_buzzer'] = False

        # === Nhiệt độ / Độ ẩm ===
        elif sensor == 'temp_humidity':
            t = data['temp_c']
            h = data['humidity']
            if t < CONFIG['temp_monitor_min_c'] or t > CONFIG['temp_monitor_max_c']:
                trigger_alert(f"Cảnh báo bảo quản: Nhiệt độ {t}°C (ngưỡng {CONFIG['temp_monitor_min_c']}-{CONFIG['temp_monitor_max_c']}°C)")
            if h < CONFIG['humidity_min'] or h > CONFIG['humidity_max']:
                trigger_alert(f"Cảnh báo bảo quản: Độ ẩm {h}% (ngưỡng {CONFIG['humidity_min']}-{CONFIG['humidity_max']}%)")

        # === Chuyển động / Ánh sáng ===
        elif sensor == 'motion_light':
            motion = data['motion']
            lux = data['lux']
            now = ts
            if motion:
                last_motion_time = now
                if lux < CONFIG['light_lux_threshold'] or motion:
                    if not shared_state['actuators']['kitchen_light']:
                        shared_state['actuators']['kitchen_light'] = True
                        trigger_action('Bật đèn bếp (phát hiện chuyển động hoặc trời tối)')
            else:
                if shared_state['actuators']['kitchen_light']:
                    if now - last_motion_time > CONFIG['light_off_delay_s']:
                        shared_state['actuators']['kitchen_light'] = False
                        trigger_action('Tắt đèn bếp (hết chuyển động)')

        # === Nước / Rò rỉ ===
        elif sensor == 'water_flow':
            lpm = data['lpm']
            leak_window.append(lpm)
            if len(leak_window) > leak_window_maxlen:
                leak_window.pop(0)
            avg = sum(leak_window) / len(leak_window)
            if avg > CONFIG['water_flow_leak_threshold_lpm'] and avg < 1.0:
                trigger_alert(f"Nghi ngờ rò rỉ nước: lưu lượng trung bình {avg:.2f} LPM")
            if lpm >= 1.0:
                if not shared_state['actuators']['water_valve_open']:
                    shared_state['actuators']['water_valve_open'] = True
                    trigger_action('Mở van nước (vòi đang dùng)')
            else:
                if shared_state['actuators']['water_valve_open']:
                    shared_state['actuators']['water_valve_open'] = False
                    trigger_action('Đóng van nước (không có dòng chảy)')

        # Phát realtime trạng thái tổng thể
        emit_state_update()

        # Gửi MQTT trạng thái
        mqtt_publish(CONFIG_EXT.get('mqtt_base_topic', 'smartkitchen'), 'state', {
            'last_update': shared_state['last_update'],
            'actuators': shared_state['actuators'],
            'sensors': shared_state['sensors']
        })

        if random.random() < 0.15:
            logging.info('Tóm tắt trạng thái: %s', {k: v['data'] for k, v in shared_state['sensors'].items() if 'data' in v})
