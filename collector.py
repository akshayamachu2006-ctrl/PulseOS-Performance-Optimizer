
import psutil
import datetime
from database import insert_metric


def auto_label(cpu, memory):
    if cpu > 80 or memory > 85:
        return "High Load"
    elif cpu > 50 or memory > 60:
        return "Medium Load"
    else:
        return "Normal"


def collect_metrics():
    timestamp = str(datetime.datetime.now())

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage(
        "C:\\" if psutil.WINDOWS else "/"
    ).percent

    net = psutil.net_io_counters()
    net_sent = round(net.bytes_sent / 1024, 2)
    net_recv = round(net.bytes_recv / 1024, 2)

    label = auto_label(cpu, memory)

    insert_metric(
        timestamp, cpu, memory, disk,
        net_sent, net_recv, label
    )

    print(
        f"CPU: {cpu}% | RAM: {memory}% | "
        f"Disk: {disk}% | Network Sent: {net_sent} KB | "
        f"Network Received: {net_recv} KB | {label}"
    )
