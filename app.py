
from flask import Flask, render_template, jsonify, send_file
import psutil
import datetime
import io
import os

from database import create_table, insert_metric, fetch_all
from ml_model import train_model, predict_load
from optimizer import suggest_optimization

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
create_table()


def get_disk_usage():
    path = "C:\\" if os.name == "nt" else "/"
    return psutil.disk_usage(path).percent


def get_current_metrics():
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = get_disk_usage()

    net = psutil.net_io_counters()
    net_sent = round(net.bytes_sent / 1024, 2)
    net_recv = round(net.bytes_recv / 1024, 2)

    label = (
        "High Load" if cpu > 80 or memory > 85
        else "Medium Load" if cpu > 50 or memory > 60
        else "Normal"
    )

    timestamp = str(datetime.datetime.now())

    insert_metric(
        timestamp, cpu, memory, disk,
        net_sent, net_recv, label
    )

    return cpu, memory, disk, net_sent, net_recv, label


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/metrics")
def metrics():
    cpu, memory, disk, net_sent, net_recv, label = (
        get_current_metrics()
    )

    model, _ = train_model()

    prediction = label
    if model is not None:
        prediction = predict_load(
            model, cpu, memory, disk, net_sent, net_recv
        )

    suggestions = suggest_optimization(
        prediction, cpu, memory, disk
    )

    rows = fetch_all()
    recent = rows[-20:]
    averages = rows[-10:]

    future_cpu = round(
        sum(row[2] for row in averages) / len(averages), 1
    ) if averages else cpu

    future_mem = round(
        sum(row[3] for row in averages) / len(averages), 1
    ) if averages else memory

    processes = []

    for proc in psutil.process_iter(
        ["pid", "name", "memory_percent"]
    ):
        try:
            info = proc.info
            processes.append({
                "pid": info["pid"],
                "name": info["name"] or "Unknown",
                "memory": round(info["memory_percent"] or 0, 1)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(key=lambda p: p["memory"], reverse=True)

    return jsonify({
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "net_sent": net_sent,
        "net_recv": net_recv,
        "prediction": prediction,
        "suggestions": suggestions,
        "future_cpu": future_cpu,
        "future_mem": future_mem,
        "processes": processes[:10],
        "history": {
            "timestamps": [r[1][11:19] for r in recent],
            "cpu": [r[2] for r in recent],
            "memory": [r[3] for r in recent],
            "disk": [r[4] for r in recent]
        }
    })


@app.route("/download_report")
def download_report():
    rows = fetch_all()
    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "OS Performance Report")
    y -= 30

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        40, y, "Generated: " + str(datetime.datetime.now())
    )
    y -= 25

    if not rows:
        pdf.drawString(40, y, "No performance records available.")
    else:
        pdf.drawString(40, y, "Recent performance records:")
        y -= 20

        for row in rows[-15:]:
            line = (
                f"{row[1]} | CPU: {row[2]}% | "
                f"RAM: {row[3]}% | Disk: {row[4]}% | {row[7]}"
            )

            pdf.drawString(40, y, line[:100])
            y -= 18

            if y < 50:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 10)

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="OS_Performance_Report.pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)
