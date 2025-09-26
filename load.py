
import os
import pandas as pd

# Paths
folder_path = os.path.join(os.getcwd(), "CICIDS2018")
output_csv = "dataset_clean.csv"

# Columns we actually need (reduces memory usage)
required_columns = [
    'Destination Port', 'Protocol', 'Flow Duration',
    'Total Fwd Packets', 'Total Backward Packets',
    'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
    'Flow Bytes/s', 'Flow Packets/s',
    'Label'
]

def merge_and_clean():
    all_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    if not all_files:
        print("❌ No CSV files found in CICIDS2018 folder.")
        return

    print(f"📂 Found {len(all_files)} CSV files. Merging...")

    merged_df = pd.DataFrame()

    for idx, file in enumerate(all_files, 1):
        file_path = os.path.join(folder_path, file)
        print(f"🔹 Loading {file} ({idx}/{len(all_files)})...")

        # Read only needed columns if available
        try:
            df = pd.read_csv(file_path, usecols=required_columns, low_memory=False)
        except ValueError:
            # Some files may have different columns, load fully then filter
            df = pd.read_csv(file_path, low_memory=False)
            df = df[[col for col in required_columns if col in df.columns]]

        merged_df = pd.concat([merged_df, df], ignore_index=True)

    print("🧹 Cleaning data...")
    # Drop duplicates
    merged_df.drop_duplicates(inplace=True)

    # Drop rows with NaN values
    merged_df.dropna(inplace=True)

    # Convert Protocol to numeric (TCP/UDP/ICMP → numbers)
    protocol_map = {'TCP': 6, 'UDP': 17, 'ICMP': 1}
    merged_df['Protocol'] = merged_df['Protocol'].map(protocol_map).fillna(0).astype(int)

    # Save cleaned dataset
    merged_df.to_csv(output_csv, index=False)
    print(f"✅ Merged & cleaned data saved to {output_csv}")
    print(f"📏 Final dataset size: {merged_df.shape[0]:,} rows × {merged_df.shape[1]} columns")

if __name__ == "__main__":
    merge_and_clean()
