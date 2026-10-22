import psutil


def bytes_to_gb(value):
    return value / 1024 ** 3


def pc_status(text):
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")

    lines = [
        "Status do PC:",
        f"  CPU: {cpu:.0f}%",
        f"  RAM: {bytes_to_gb(ram.used):.1f} de {bytes_to_gb(ram.total):.1f} GB ({ram.percent:.0f}%)",
        f"  Disco C: {bytes_to_gb(disk.used):.0f} de {bytes_to_gb(disk.total):.0f} GB ({disk.percent:.0f}%)",
    ]

    battery = psutil.sensors_battery()
    if battery is not None:
        plug = "carregando 🔌" if battery.power_plugged else "na bateria 🔋"
        lines.append(f"  Bateria: {battery.percent:.0f}% ({plug})")

    if ram.percent > 90:
        lines.append("⚠️ A memória está quase cheia. Vale fechar alguns programas.")
    return "\n".join(lines)
