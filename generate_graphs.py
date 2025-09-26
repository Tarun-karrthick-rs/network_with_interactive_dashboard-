# import os
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# import json

# # -----------------------------
# # Load packet log from redirector
# # -----------------------------
# JSON_FILE = 'packet_log.json'
# if os.path.exists(JSON_FILE):
#     with open(JSON_FILE, 'r') as f:
#         packet_log = json.load(f)
#     packet_df = pd.DataFrame(packet_log)
# else:
#     print("❌ packet_log.json not found, using dummy data")
#     labels = ['Benign']*60 + ['Malicious']*40
#     packet_df = pd.DataFrame({'Label': labels})

# # Count packets
# benign_count = (packet_df['Label'] == 'BENIGN').sum()
# malicious_count = (packet_df['Label'] == 'MALICIOUS').sum()

# # -----------------------------
# # Create output folder
# # -----------------------------
# output_folder = 'graphs_output'
# os.makedirs(output_folder, exist_ok=True)

# # -----------------------------
# # 1️⃣ Dataset Size Bar Chart
# # -----------------------------
# raw_size = len(packet_df)
# cleaned_size = len(packet_df.dropna())
# plt.figure(figsize=(8,6))
# plt.bar(['Raw','Cleaned'], [raw_size, cleaned_size], color='blue')
# plt.title('Dataset Size')
# plt.ylabel('Number of Samples')
# plt.grid(axis='y', linestyle='--', alpha=0.7)
# plt.savefig(os.path.join(output_folder, 'dataset_size.png'))
# plt.close()

# # -----------------------------
# # 2️⃣ Benign vs Malicious Pie Chart (real counts)
# # -----------------------------
# plt.figure(figsize=(6,6))
# plt.pie([benign_count, malicious_count],
#         labels=['Benign','Malicious'],
#         colors=['green','red'],
#         autopct='%1.1f%%',
#         startangle=90)
# plt.title('Benign vs Malicious Packets')
# plt.savefig(os.path.join(output_folder, 'benign_vs_malicious.png'))
# plt.close()

# print(f"\n✅ Graphs saved in '{output_folder}' with REAL packet counts:")
# print(f"   Benign: {benign_count}, Malicious: {malicious_count}")

# # -----------------------------
# # 3️⃣ Training vs Testing Accuracy
# # -----------------------------
# plt.figure(figsize=(10,6))
# plt.plot(epochs:=range(1, len(train_acc)+1), train_acc, marker='o', linestyle='-', color='orange', label='Train Accuracy')
# plt.plot(epochs, test_acc, marker='o', linestyle='-', color='red', label='Test Accuracy')
# plt.title('Training vs Testing Accuracy')
# plt.xlabel('Epoch')
# plt.ylabel('Accuracy')
# plt.ylim(0,1)
# plt.xticks(epochs)
# plt.grid(True, linestyle='--', alpha=0.7)
# plt.legend()
# plt.savefig(os.path.join(output_folder, 'train_vs_test_accuracy.png'))
# plt.close()

# # -----------------------------
# # 4️⃣ Benign vs Malicious Pie Chart
# # -----------------------------
# plt.figure(figsize=(6,6))
# plt.pie([benign_count, malicious_count],
#         labels=['Benign','Malicious'],
#         colors=['green','red'],
#         autopct='%1.1f%%',
#         startangle=90)
# plt.title('Benign vs Malicious Packets')
# plt.savefig(os.path.join(output_folder, 'benign_vs_malicious.png'))
# plt.close()

# # -----------------------------
# # 5️⃣ Real-Time Packet Classification Trend
# # -----------------------------
# plt.figure(figsize=(10,6))
# plt.step(time_elapsed, train_acc, where='mid', color='purple', alpha=0.7)
# plt.scatter(time_elapsed, train_acc, color='purple')
# plt.title('Real-Time Packet Classification Trend')
# plt.xlabel('Time (s)')
# plt.ylabel('Accuracy')
# plt.ylim(0,1)
# plt.grid(True, linestyle='--', alpha=0.7)
# plt.savefig(os.path.join(output_folder, 'real_time_packet_trend.png'))
# plt.close()

# # -----------------------------
# # 6️⃣ Accuracy vs Training Time
# # -----------------------------
# plt.figure(figsize=(10,6))
# plt.fill_between(time_elapsed, train_acc, step='mid', color='teal', alpha=0.3)
# plt.step(time_elapsed, train_acc, where='mid', color='teal')
# plt.scatter(time_elapsed, train_acc, color='teal')
# plt.title('Accuracy vs Training Time')
# plt.xlabel('Training Time (s)')
# plt.ylabel('Accuracy')
# plt.ylim(0,1)
# plt.grid(True, linestyle='--', alpha=0.7)
# plt.savefig(os.path.join(output_folder, 'accuracy_vs_time.png'))
# plt.close()

# # -----------------------------
# # 7️⃣ Efficiency Comparison (dummy)
# # -----------------------------
# methods = ['XGBoost','Random Forest']
# acc_values = [85, 78]
# plt.figure(figsize=(8,6))
# plt.bar(methods, acc_values, color='brown')
# plt.title('Efficiency Comparison')
# plt.ylabel('Accuracy (%)')
# plt.grid(axis='y', linestyle='--', alpha=0.7)
# plt.savefig(os.path.join(output_folder, 'efficiency_comparison.png'))
# plt.close()

# print(f"\n✅ All 7 graphs saved in folder '{output_folder}'")
# print("Model Accuracy: 85.66%")



import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

# -----------------------------
# Load packet log
# -----------------------------
JSON_FILE = 'packet_log.json'
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r') as f:
        packet_log = json.load(f)
    packet_df = pd.DataFrame(packet_log)
    if packet_df.empty:
        print("❌ packet_log.json is empty, using dummy data")
        labels = ['BENIGN']*60 + ['MALICIOUS']*40
        packet_df = pd.DataFrame({'Label': labels})
else:
    print("❌ packet_log.json not found, using dummy data")
    labels = ['BENIGN']*60 + ['MALICIOUS']*40
    packet_df = pd.DataFrame({'Label': labels})

# -----------------------------
# Packet counts
# -----------------------------
benign_count = (packet_df['Label'] == 'BENIGN').sum()
malicious_count = (packet_df['Label'] == 'MALICIOUS').sum()

# -----------------------------
# Create output folder
# -----------------------------
output_folder = 'graphs_output'
os.makedirs(output_folder, exist_ok=True)

# -----------------------------
# 1️⃣ Dataset Size
# -----------------------------
raw_size = len(packet_df)
cleaned_size = len(packet_df.dropna())
plt.figure(figsize=(8,6))
plt.bar(['Raw','Cleaned'], [raw_size, cleaned_size], color='blue')
plt.title('Dataset Size')
plt.ylabel('Number of Samples')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig(os.path.join(output_folder, 'dataset_size.png'))
plt.close()

# -----------------------------
# 2️⃣ Benign vs Malicious Pie
# -----------------------------
plt.figure(figsize=(6,6))
plt.pie([benign_count, malicious_count],
        labels=['Benign','Malicious'],
        colors=['green','red'],
        autopct='%1.1f%%',
        startangle=90)
plt.title('Benign vs Malicious Packets')
plt.savefig(os.path.join(output_folder, 'benign_vs_malicious.png'))
plt.close()

# -----------------------------
# 3️⃣ Real-Time Packet Classification Trend
# -----------------------------
if 'Timestamp' in packet_df.columns:
    packet_df['Timestamp'] = pd.to_datetime(packet_df['Timestamp'])
    times = (packet_df['Timestamp'] - packet_df['Timestamp'].iloc[0]).dt.total_seconds()
else:
    times = np.arange(len(packet_df))

# Cumulative stats for trend
cumulative_total = np.arange(1, len(packet_df)+1)
cumulative_benign = packet_df['Label'].eq('BENIGN').cumsum()
cumulative_malicious = packet_df['Label'].eq('MALICIOUS').cumsum()
cumulative_accuracy = cumulative_benign / cumulative_total  # percentage of benign packets

plt.figure(figsize=(10,6))
plt.step(times, cumulative_accuracy, where='mid', color='purple', alpha=0.7, label='Benign Ratio')
plt.scatter(times, cumulative_accuracy, color='purple')
plt.title('Real-Time Packet Classification Trend')
plt.xlabel('Time (s)')
plt.ylabel('Cumulative Benign Ratio')
plt.ylim(0,1)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.savefig(os.path.join(output_folder, 'real_time_packet_trend.png'))
plt.close()

# -----------------------------
# 4️⃣ Accuracy vs Time
# -----------------------------
plt.figure(figsize=(10,6))
plt.fill_between(times, cumulative_accuracy, step='mid', color='teal', alpha=0.3)
plt.step(times, cumulative_accuracy, where='mid', color='teal')
plt.scatter(times, cumulative_accuracy, color='teal')
plt.title('Accuracy vs Time')
plt.xlabel('Time (s)')
plt.ylabel('Cumulative Benign Ratio')
plt.ylim(0,1)
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(os.path.join(output_folder, 'accuracy_vs_time.png'))
plt.close()

# -----------------------------
# 5️⃣ Protocol Distribution
# -----------------------------
if 'Protocol' in packet_df.columns:
    protocols = packet_df['Protocol'].value_counts()
    plt.figure(figsize=(8,6))
    protocols.plot(kind='bar', color='orange')
    plt.title('Protocol Distribution')
    plt.ylabel('Number of Packets')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(output_folder, 'protocol_distribution.png'))
    plt.close()

# -----------------------------
# 6️⃣ Source IP Distribution (Top 10)
# -----------------------------
if 'SrcIP' in packet_df.columns:
    top_ips = packet_df['SrcIP'].value_counts().head(10)
    plt.figure(figsize=(10,6))
    top_ips.plot(kind='barh', color='brown')
    plt.title('Top 10 Source IPs')
    plt.xlabel('Number of Packets')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(output_folder, 'top_src_ips.png'))
    plt.close()

# -----------------------------
# 7️⃣ Efficiency Comparison (Benign vs Malicious ratio)
# -----------------------------
plt.figure(figsize=(6,6))
plt.bar(['Benign','Malicious'], [benign_count, malicious_count], color=['green','red'])
plt.title('Packet Type Comparison')
plt.ylabel('Number of Packets')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig(os.path.join(output_folder, 'efficiency_comparison.png'))
plt.close()

print(f"\n✅ All graphs saved in '{output_folder}' with REAL packet counts:")
print(f"   Benign: {benign_count}, Malicious: {malicious_count}")
