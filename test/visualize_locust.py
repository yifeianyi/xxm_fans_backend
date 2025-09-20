import pandas as pd
import matplotlib.pyplot as plt

# 读取 Locust 生成的统计文件
stats_file = "load_test_results_stats.csv"
df = pd.read_csv(stats_file)

# 有些 CSV 会有多余的 "Aggregated" 行，去掉它
df = df[df["Name"] != "Aggregated"]

# 画 QPS（每秒请求数）
plt.figure(figsize=(10, 6))
df.groupby("Name")["Requests/s"].plot(legend=True)
plt.title("QPS per Endpoint")
plt.xlabel("Time (intervals)")
plt.ylabel("Requests per second")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("qps.png")
plt.close()

# 画平均响应时间
plt.figure(figsize=(10, 6))
df.groupby("Name")["Average Response Time"].plot(legend=True)
plt.title("Average Response Time per Endpoint")
plt.xlabel("Time (intervals)")
plt.ylabel("Response Time (ms)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("response_time.png")
plt.close()

# 画失败率
plt.figure(figsize=(10, 6))
df.groupby("Name")["Failure Count"].plot(legend=True)
plt.title("Failures per Endpoint")
plt.xlabel("Time (intervals)")
plt.ylabel("Failures")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("failures.png")
plt.close()

print("✅ 图表已生成: qps.png, response_time.png, failures.png")
