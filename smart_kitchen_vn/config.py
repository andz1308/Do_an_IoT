import os
from dotenv import load_dotenv
load_dotenv()
def _env_bool(k,d=False):
    v=os.getenv(k); return d if v is None else v.lower() in ('1','true','yes','on')
CONFIG_EXT = {
    'mqtt_enabled': _env_bool('MQTT_ENABLED', False),
    'mqtt_broker': os.getenv('MQTT_BROKER','localhost'),
    'mqtt_port': int(os.getenv('MQTT_PORT','1883')),
    'mqtt_base_topic': os.getenv('MQTT_BASE_TOPIC','smartkitchen'),
    'socketio_enabled': _env_bool('SOCKETIO_ENABLED', True),
    'http_host': os.getenv('HTTP_HOST','0.0.0.0'),
    'http_port': int(os.getenv('HTTP_PORT','5000')),
    'db_enabled': _env_bool('DB_ENABLED', True),
    'db_path': os.getenv('DB_PATH','smart_kitchen.db'),
    'file_log_enabled': _env_bool('FILE_LOG_ENABLED', True),
    'log_file_path': os.getenv('LOG_FILE_PATH','smart_kitchen.log'),
}
CONFIG = {
    'mq2_threshold_ppm': int(os.getenv('MQ2_THRESHOLD_PPM','200')),
    'mq5_threshold_ppm': int(os.getenv('MQ5_THRESHOLD_PPM','150')),
    'smoke_threshold': int(os.getenv('SMOKE_THRESHOLD','70')),
    'fire_temp_threshold_c': int(os.getenv('FIRE_TEMP_THRESHOLD_C','80')),
    'temp_monitor_min_c': int(os.getenv('TEMP_MONITOR_MIN_C','2')),
    'temp_monitor_max_c': int(os.getenv('TEMP_MONITOR_MAX_C','10')),
    'humidity_min': int(os.getenv('HUMIDITY_MIN','30')),
    'humidity_max': int(os.getenv('HUMIDITY_MAX','70')),
    'light_lux_threshold': int(os.getenv('LIGHT_LUX_THRESHOLD','100')),
    'light_off_delay_s': int(os.getenv('LIGHT_OFF_DELAY_S','15')),
    'water_flow_leak_threshold_lpm': float(os.getenv('WATER_FLOW_LEAK_THRESHOLD_LPM','0.5')),
}
