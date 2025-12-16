import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------
# CONFIG
# -----------------------------
BASELINE_FILE = "results_maxcapacity.csv"
NEW_FILE = "results_new_maxcapacity.csv"
OUTPUT_PNG = "comparison_results.png"

SERVICES = [
    "connected_vehicles",
    "augmented_reality",
    "video_analysis",
]

# -----------------------------
# LOAD DATA
# -----------------------------
df_base = pd.read_csv(BASELINE_FILE)
df_new = pd.read_csv(NEW_FILE)

# Ensure same timeline
assert len(df_base) == len(df_new), "CSV files must have same length"

time = df_base["time"]

# -----------------------------
# 1️⃣ TOTAL REJECTED REQUESTS
# -----------------------------
rej_cols = [c for c in df_base.columns if c.startswith("rejected_req_")]

rej_base = df_base[rej_cols].sum(axis=1)
rej_new = df_new[rej_cols].sum(axis=1)

# -----------------------------
# 2️⃣ ENERGY CONSUMPTION
# -----------------------------
energy_base = (
    df_base["dynamic_W_servers"]
    + df_base["idle_W_servers"]
    + df_base["W_links"]
)

energy_new = (
    df_new["dynamic_W_servers"]
    + df_new["idle_W_servers"]
    + df_new["W_links"]
)

# -----------------------------
# 3️⃣ UNSATISFIED REQUESTS (SERVICE LEVEL)
# -----------------------------
unsat_base = []
unsat_new = []

for s in SERVICES:
    unsat_base.append(df_base[f"unsatisf_req_{s}"].sum())
    unsat_new.append(df_new[f"unsatisf_req_{s}"].sum())

# -----------------------------
# 4️⃣ 95th PERCENTILE DELAY PER SERVICE
# -----------------------------
def p95_delay(df, service):
    cols = [c for c in df.columns if c.startswith("delay_") and c.endswith(service)]
    return np.percentile(df[cols].values.flatten(), 95)

delay_base = [p95_delay(df_base, s) for s in SERVICES]
delay_new = [p95_delay(df_new, s) for s in SERVICES]

# -----------------------------
# PLOTTING
# -----------------------------
plt.figure(figsize=(16, 12))

# ---- Rejected Requests ----
plt.subplot(2, 2, 1)
plt.plot(time, rej_base, label="Baseline", linewidth=2)
plt.plot(time, rej_new, label="New Allocator", linewidth=2)
plt.title("Total Rejected Requests Over Time")
plt.xlabel("Time")
plt.ylabel("Requests")
plt.legend()
plt.grid(True)

# ---- Energy ----
plt.subplot(2, 2, 2)
plt.plot(time, energy_base, label="Baseline", linewidth=2)
plt.plot(time, energy_new, label="New Allocator", linewidth=2)
plt.title("Total Energy Consumption Over Time")
plt.xlabel("Time")
plt.ylabel("Watts")
plt.legend()
plt.grid(True)

# ---- Unsatisfied Requests ----
plt.subplot(2, 2, 3)
x = np.arange(len(SERVICES))
width = 0.35
plt.bar(x - width/2, unsat_base, width, label="Baseline")
plt.bar(x + width/2, unsat_new, width, label="New Allocator")
plt.xticks(x, SERVICES, rotation=15)
plt.title("Total Unsatisfied Requests by Service")
plt.ylabel("Requests")
plt.legend()
plt.grid(axis="y")

# ---- Delay ----
plt.subplot(2, 2, 4)
plt.bar(x - width/2, delay_base, width, label="Baseline")
plt.bar(x + width/2, delay_new, width, label="New Allocator")
plt.xticks(x, SERVICES, rotation=15)
plt.title("95th Percentile End-to-End Delay by Service")
plt.ylabel("Delay (s)")
plt.legend()
plt.grid(axis="y")

plt.tight_layout()
plt.savefig(OUTPUT_PNG, dpi=300)
plt.show()

print(f"\n✅ Comparison complete. Saved as {OUTPUT_PNG}\n")
