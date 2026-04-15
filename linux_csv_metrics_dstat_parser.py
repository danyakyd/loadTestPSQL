import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("metrics2_2cpu_4gb.csv", skiprows=5)

print(df.columns.tolist())  # посмотри реальные имена колонок

# привести числовые колонки
for col in df.columns:
    if col != "time":
        df[col] = pd.to_numeric(df[col], errors="coerce")

# CPU user
plt.figure()
plt.plot(df["total usage:usr"])
plt.title("Linux CPU user %")
plt.xlabel("sample")
plt.ylabel("%")
plt.grid(True)
plt.show()

# CPU system
plt.figure()
plt.plot(df["total usage:sys"])
plt.title("Linux CPU system %")
plt.xlabel("sample")
plt.ylabel("%")
plt.grid(True)
plt.show()

# Memory used
TOTAL_RAM = 3900 #Mi на самой тачке 4096Mi
# привести к числам
for col in df.columns:
    if col != "time":
        df[col] = pd.to_numeric(df[col], errors="coerce")

df["mem_percent"] = df["used"] / (TOTAL_RAM * 1024) * 100



plt.figure()
plt.plot(df["mem_percent"])
plt.title("Linux Memory Usage (%)")
plt.xlabel("sample")
plt.ylabel("%")
plt.grid(True)
plt.show()



# Disk read
plt.figure()
plt.plot(df["dsk/total:read"])
plt.title("Linux img read")
plt.xlabel("sample")
plt.ylabel("blocks/s or KB/s")
plt.grid(True)
plt.show()

# Disk write
plt.figure()
plt.plot(df["dsk/total:writ"])
plt.title("Linux img write")
plt.xlabel("sample")
plt.ylabel("blocks/s or KB/s")
plt.grid(True)
plt.show()