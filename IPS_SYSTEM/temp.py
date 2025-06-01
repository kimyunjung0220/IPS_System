import psutil

net = psutil.net_io_counters()
total_bytes = net.bytes_sent + net.bytes_recv
total_gb = total_bytes / (1024**3)

print(f"Total Network Usage: {total_gb:.2f} GB")
