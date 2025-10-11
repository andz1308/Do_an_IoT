import logging, threading, json, smtplib
from email.message import EmailMessage
try:
    import paho.mqtt.client as mqtt; MQTT_AVAILABLE=True
except Exception:
    MQTT_AVAILABLE=False
try:
    from twilio.rest import Client as TwilioClient; TWILIO_AVAILABLE=True
except Exception:
    TWILIO_AVAILABLE=False
_mqtt_client=None; _twilio_client=None
def init_mqtt(cfg):
    global _mqtt_client
    if not cfg.get('mqtt_enabled'): logging.info('MQTT disabled'); return
    if not MQTT_AVAILABLE: logging.warning('paho-mqtt không cài'); return
    try: _mqtt_client=mqtt.Client(); _mqtt_client.connect(cfg['mqtt_broker'],cfg['mqtt_port'],60); _mqtt_client.loop_start(); logging.info('MQTT connected')
    except Exception as e: logging.exception('MQTT init failed: %s',e); _mqtt_client=None
def mqtt_publish(base_topic,suffix,payload):
    if _mqtt_client is None: return
    topic=f"{base_topic}/{suffix}"
    try: _mqtt_client.publish(topic,json.dumps(payload))
    except Exception as e: logging.exception('MQTT publish failed: %s',e)
def send_email_async(cfg,subject,body):
    if not cfg.get('email_enabled'): return
    def _send():
        try:
            msg=EmailMessage(); msg['From']=cfg['email_from']; msg['To']=','.join(cfg.get('email_to',[])); msg['Subject']=subject; msg.set_content(body)
            with smtplib.SMTP(cfg['smtp_host'],cfg['smtp_port'],timeout=10) as s:
                s.starttls(); s.login(cfg['smtp_user'],cfg['smtp_pass']); s.send_message(msg)
            logging.info('Email sent: %s',subject)
        except Exception as e:
            logging.exception('Email send failed: %s',e)
    threading.Thread(target=_send,daemon=True).start()
def init_twilio(cfg):
    global _twilio_client
    if not cfg.get('twilio_enabled'): logging.info('Twilio disabled'); return
    if not TWILIO_AVAILABLE: logging.warning('Twilio SDK không cài'); return
    try: _twilio_client=TwilioClient(cfg['twilio_account_sid'],cfg['twilio_auth_token'])
    except Exception as e: logging.exception('Twilio init failed: %s',e); _twilio_client=None
def send_sms_async(cfg,body):
    if not cfg.get('twilio_enabled') or _twilio_client is None: return
    def _send():
        for to in cfg.get('twilio_to_numbers',[]):
            try: _twilio_client.messages.create(body=body,from_=cfg['twilio_from_number'],to=to); logging.info('SMS sent to %s',to)
            except Exception as e: logging.exception('SMS failed for %s: %s',to,e)
    threading.Thread(target=_send,daemon=True).start()
