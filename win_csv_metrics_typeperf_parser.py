import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


TOTAL_MEMORY_MB = 4000  # тачке выделено 4096MB
CSV_FILE = "metrics2win_2cpu_4gb.csv"


def find_column(columns, needle):
    needle = needle.lower()
    for col in columns:
        if needle in col.lower():
            return col
    return None


def load_typeperf_csv(path: str) -> pd.DataFrame:
    # typeperf с русскими счётчиками обычно cp1251
    df = pd.read_csv(path, encoding="cp1251")

    # найти время
    time_col = df.columns[0]
    df = df.rename(columns={time_col: "time"})

    # привести время
    df["time"] = pd.to_datetime(df["time"], format="%m/%d/%Y %H:%M:%S.%f", errors="coerce")

    # найти нужные столбцы
    cpu_col = find_column(df.columns, "процессор(_total)")
    mem_pct_col = find_column(df.columns, "использования выделенной памяти")
    read_bps_col = find_column(df.columns, "чтение байт/с")
    write_bps_col = find_column(df.columns, "запись байт/с")
    queue_col = find_column(df.columns, "средняя длина очереди диска")

    rename_map = {}
    if cpu_col:
        rename_map[cpu_col] = "cpu_percent"
    if mem_pct_col:
        rename_map[mem_pct_col] = "mem_percent"
    if read_bps_col:
        rename_map[read_bps_col] = "disk_read_bps"
    if write_bps_col:
        rename_map[write_bps_col] = "disk_write_bps"
    if queue_col:
        rename_map[queue_col] = "disk_queue"

    df = df.rename(columns=rename_map)

    # привести все числовые поля
    for col in ["cpu_percent", "mem_percent", "disk_read_bps", "disk_write_bps", "disk_queue"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # память в MB
    if "mem_percent" in df.columns:
        df["mem_used_mb"] = TOTAL_MEMORY_MB * df["mem_percent"] / 100.0

    # дисковый IO в MB/s
    if "disk_read_bps" in df.columns:
        df["disk_read_mb_s"] = df["disk_read_bps"] / 1024 / 1024
    if "disk_write_bps" in df.columns:
        df["disk_write_mb_s"] = df["disk_write_bps"] / 1024 / 1024

    # относительное время в секундах от начала теста
    df = df.sort_values("time").reset_index(drop=True)
    df["t_sec"] = (df["time"] - df["time"].iloc[0]).dt.total_seconds()

    return df


def plot_metrics(df: pd.DataFrame, out_dir="plots"):
    Path(out_dir).mkdir(exist_ok=True)

    # CPU
    if "cpu_percent" in df.columns:
        plt.figure(figsize=(12, 5))
        plt.plot(df["t_sec"], df["cpu_percent"])
        plt.title("CPU usage")
        plt.xlabel("Time from start, sec")
        plt.ylabel("CPU, %")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{out_dir}/cpu.png", dpi=150)
        plt.show()

    # Memory percent
    if "mem_percent" in df.columns:
        plt.figure(figsize=(12, 5))
        plt.plot(df["t_sec"], df["mem_percent"])
        plt.title("Memory usage")
        plt.xlabel("Time from start, sec")
        plt.ylabel("Memory, %")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{out_dir}/memory_percent.png", dpi=150)
        plt.show()

    # Memory MB
    if "mem_used_mb" in df.columns:
        plt.figure(figsize=(12, 5))
        plt.plot(df["t_sec"], df["mem_used_mb"])
        plt.title("Memory used")
        plt.xlabel("Time from start, sec")
        plt.ylabel("Memory, MB")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{out_dir}/memory_mb.png", dpi=150)
        plt.show()

    # Disk read
    if "disk_read_mb_s" in df.columns:
        plt.figure(figsize=(12, 5))
        plt.plot(df["t_sec"], df["disk_read_mb_s"])
        plt.title("Disk read")
        plt.xlabel("Time from start, sec")
        plt.ylabel("Read, MB/s")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{out_dir}/disk_read.png", dpi=150)
        plt.show()

    # Disk write
    if "disk_write_mb_s" in df.columns:
        plt.figure(figsize=(12, 5))
        plt.plot(df["t_sec"], df["disk_write_mb_s"])
        plt.title("Disk write")
        plt.xlabel("Time from start, sec")
        plt.ylabel("Write, MB/s")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{out_dir}/disk_write.png", dpi=150)
        plt.show()

    # Disk queue
    if "disk_queue" in df.columns:
        plt.figure(figsize=(12, 5))
        plt.plot(df["t_sec"], df["disk_queue"])
        plt.title("Disk queue length")
        plt.xlabel("Time from start, sec")
        plt.ylabel("Queue length")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{out_dir}/disk_queue.png", dpi=150)
        plt.show()


def print_summary(df: pd.DataFrame):
    print("\n=== SUMMARY ===")
    for col in [
        "cpu_percent",
        "mem_percent",
        "mem_used_mb",
        "disk_read_mb_s",
        "disk_write_mb_s",
        "disk_queue",
    ]:
        if col in df.columns:
            print(
                f"{col}: "
                f"min={df[col].min():.2f}, "
                f"avg={df[col].mean():.2f}, "
                f"max={df[col].max():.2f}"
            )


if __name__ == "__main__":
    df = load_typeperf_csv(CSV_FILE)
    print(df.head())
    print_summary(df)
    plot_metrics(df)