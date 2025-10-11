import sqlite3, logging
_db_conn=None
def init_db(path,enabled=True):
    global _db_conn
    if not enabled:
        logging.info('DB disabled'); return
    _db_conn=sqlite3.connect(path,check_same_thread=False)
    cur=_db_conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, time REAL, text TEXT)")
    _db_conn.commit()
    logging.info('DB initialized at %s',path)
def insert_alert(ts,text):
    if _db_conn is None: return
    try:
        cur=_db_conn.cursor(); cur.execute('INSERT INTO alerts (time,text) VALUES (?,?)',(ts,text)); _db_conn.commit()
    except Exception as e:
        logging.exception('DB insert failed: %s',e)
