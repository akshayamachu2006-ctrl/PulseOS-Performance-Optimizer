
import time
import psutil

from database import create_table
from collector import collect_metrics
from ml_model import train_model, predict_load
from optimizer import suggest_optimization


def main():
    create_table()

    print("========================================")
    print(" ML-DRIVEN OS PERFORMANCE OPTIMIZER")
    print("========================================")
    print("\nCollecting system performance data...\n")

    for i in range(30):
        print(f"Sample {i + 1}/30")
        collect_metrics()
        time.sleep(1)

    print("\nTraining Machine Learning Model...")

    model, features = train_model()

    if model is None:
        print(
            "\nNot enough variety in the collected data "
            "to train the model."
        )
        print("Run the program again later to collect more data.")
        return

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("C:\\" if psutil.WINDOWS else "/").percent

    net = psutil.net_io_counters()
    net_sent = round(net.bytes_sent / 1024, 2)
    net_recv = round(net.bytes_recv / 1024, 2)

    prediction = predict_load(
        model, cpu, memory, disk, net_sent, net_recv
    )

    print("\nCurrent System Status")
    print(f"CPU Usage: {cpu}%")
    print(f"RAM Usage: {memory}%")
    print(f"Disk Usage: {disk}%")

    suggest_optimization(prediction, cpu, memory, disk)


if __name__ == "__main__":
    main()
