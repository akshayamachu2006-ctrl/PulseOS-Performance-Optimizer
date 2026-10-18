
import sqlite3


def create_connection():
    conn = sqlite3.connect("os_metrics.db")
    return conn


def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu_usage REAL,
            memory_usage REAL,
            disk_usage REAL,
            net_sent REAL,
            net_recv REAL,
            label TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS optimization_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            action TEXT,
            result TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_metric(timestamp, cpu, memory, disk,
                  net_sent, net_recv, label):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO metrics
        (timestamp, cpu_usage, memory_usage, disk_usage,
         net_sent, net_recv, label)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, cpu, memory, disk,
          net_sent, net_recv, label))

    conn.commit()
    conn.close()


def fetch_all():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM metrics ORDER BY id")
    rows = cursor.fetchall()

    conn.close()
    return rows
