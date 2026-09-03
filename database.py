import sqlite3
import datetime

conn = sqlite3.connect('monitor.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS metrics
             (timestamp TEXT, cpu REAL, ram REAL, disk REAL, network TEXT)''')
conn.commit()

def insert_data(cpu, ram, disk, network):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO metrics VALUES (?,?,?,?,?)", (timestamp, cpu, ram, disk, network))
    conn.commit()

def get_last_50_data():
    c.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 50")
    return c.fetchall()