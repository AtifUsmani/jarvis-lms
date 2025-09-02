import psutil
import time
import threading
try:
    import pynvml
    pynvml.nvmlInit()
    GPU_AVAILABLE = True
except Exception:
    GPU_AVAILABLE = False

from tts.tts import speak_async

def get_system_status():
    """Return real-time CPU, RAM, Disk, Net, GPU stats."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()

    status = {
        "cpu_percent": cpu,
        "ram_percent": ram.percent,
        "ram_used": f"{ram.used / (1024**3):.2f} GB",
        "ram_total": f"{ram.total / (1024**3):.2f} GB",
        "disk_percent": disk.percent,
        "disk_used": f"{disk.used / (1024**3):.2f} GB",
        "disk_total": f"{disk.total / (1024**3):.2f} GB",
        "net_sent_mb": f"{net.bytes_sent / (1024**2):.2f} MB",
        "net_recv_mb": f"{net.bytes_recv / (1024**2):.2f} MB"
    }

    if GPU_AVAILABLE:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        gpu_util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

        status["gpu_util"] = gpu_util.gpu
        status["gpu_mem_used"] = f"{mem_info.used / (1024**2):.2f} MB"
        status["gpu_mem_total"] = f"{mem_info.total / (1024**2):.2f} MB"
        status["gpu_mem_percent"] = (mem_info.used / mem_info.total) * 100

    return status



def system_status_tool(_):
    """LangChain tool wrapper for one-time system status check."""
    stats = get_system_status()
    report = (
        f"CPU: {stats['cpu_percent']}% | RAM: {stats['ram_percent']}% "
        f"({stats['ram_used']} / {stats['ram_total']}) | Disk: {stats['disk_percent']}% "
        f"({stats['disk_used']} / {stats['disk_total']}) | "
        f"Net Sent: {stats['net_sent_mb']} | Net Received: {stats['net_recv_mb']}"
    )

    if "gpu_util" in stats:
        report += f" | GPU: {stats['gpu_util']}% ({stats['gpu_mem_used']} / {stats['gpu_mem_total']})"

    return report

# 🔧 Background monitoring mode
_monitoring = False
_last_alerts = {"cpu": 0, "ram": 0, "gpu": 0}
ALERT_INTERVAL = 300  # seconds between alerts per resource


def _monitor_loop():
    global _monitoring
    while _monitoring:
        stats = get_system_status()
        now = time.time()

        if stats["cpu_percent"] > 85 and now - _last_alerts["cpu"] > ALERT_INTERVAL:
            speak_async(f"Warning: CPU usage is at {stats['cpu_percent']} percent.")
            _last_alerts["cpu"] = now

        if stats["ram_percent"] > 90 and now - _last_alerts["ram"] > ALERT_INTERVAL:
            speak_async(f"Memory alert: RAM is at {stats['ram_percent']} percent.")
            _last_alerts["ram"] = now

        if "gpu_mem_percent" in stats and stats["gpu_mem_percent"] > 90 and now - _last_alerts["gpu"] > ALERT_INTERVAL:
            speak_async(f"GPU memory is almost full at {stats['gpu_mem_percent']:.0f} percent.")
            _last_alerts["gpu"] = now

        time.sleep(10)  # check every 10s without spamming


def start_monitoring():
    global _monitoring
    if not _monitoring:
        _monitoring = True
        threading.Thread(target=_monitor_loop, daemon=True).start()
        speak_async("System monitoring activated. I will warn you only if critical limits are reached.")


def stop_monitoring():
    global _monitoring
    _monitoring = False
    speak_async("System monitoring stopped.")