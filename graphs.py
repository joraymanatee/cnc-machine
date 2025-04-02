import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------
# 1) Load all CSVs recursively
# --------------------------------------------
base_path = '/Users/josephpieper/Avalon Internship/Machining Code/'
csv_files = glob.glob(os.path.join(base_path, '**/*.csv'), recursive=True)

print(f"📂 Found {len(csv_files)} CSV files.\n")

all_dfs = []

for file in csv_files:
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()
        df['ParsedTimestamp'] = pd.to_datetime(
            df['Timestamp'], 
            format='%y-%m-%d-%H%M%S%f', 
            errors='coerce'
        )
        df = df.dropna(subset=['ParsedTimestamp'])

        # Infer Source (you could enhance this further)
        for tag in ['438', '439', '440', '441', '442', '443', '444', '445', '446', '447', '448']:
            if tag in file:
                df['Source'] = f"Carrier {tag}"
                break
        else:
            df['Source'] = 'Unknown'

        all_dfs.append(df)
        print(f"✅ Loaded: {os.path.basename(file)}")
    except Exception as e:
        print(f"⚠️ Failed to load {file}: {e}")

# --------------------------------------------
# 2) Combine all data into a single DataFrame
# --------------------------------------------
df_all = pd.concat(all_dfs, ignore_index=True)
df_all.columns = df_all.columns.str.strip()

# Ensure 'Tool' is a string; remove trailing '0' if needed
df_all['Tool'] = df_all['Tool'].astype(str).str.rstrip('0')

# Convert 'Cycle' to numeric
df_all['Cycle'] = pd.to_numeric(df_all['Cycle'], errors='coerce')

# Drop rows with invalid timestamps
df_all.dropna(subset=['ParsedTimestamp'], inplace=True)

# --------------------------------------------
# 3) Filter for cycles 438–448
# --------------------------------------------
df_cycles = df_all[df_all['Cycle'].between(438, 448)].copy()

# 4) Get unique tools in this cycle range
unique_tools = df_cycles['Tool'].dropna().unique()
unique_tools.sort()  # optional, sort them alphabetically

# 5) Loop over each tool
for tool_name in unique_tools:
    tool_df = df_cycles[df_cycles['Tool'] == tool_name].copy()
    if tool_df.empty:
        continue

    # Identify all measure types used by this tool
    measure_types = tool_df['MeasureType'].dropna().unique()
    measure_types.sort()  # optional sorting

    # Identify which cycles exist for this tool
    unique_cycles = sorted(tool_df['Cycle'].dropna().unique())

    # 6) For each measure type, make a single figure with all cycles overlaid
    for mtype in measure_types:
        mtype_df = tool_df[tool_df['MeasureType'] == mtype].copy()
        if mtype_df.empty:
            continue

        # Create a "RelTime" column so each cycle starts at T=0
        mtype_df['RelTime'] = mtype_df.groupby('Cycle')['ParsedTimestamp'].transform(
            lambda x: (x - x.min()).dt.total_seconds()
        )

        # Create a new figure
        plt.figure(figsize=(10, 5))

        # Plot each cycle on the same chart
        for cycle_num in unique_cycles:
            cycle_data = mtype_df[mtype_df['Cycle'] == cycle_num]
            if cycle_data.empty:
                continue

            # Sort by RelTime for proper chronological order
            cycle_data.sort_values('RelTime', inplace=True)

            plt.plot(
                cycle_data['RelTime'],
                cycle_data['Value'],
                label=f'Cycle {cycle_num}'
            )

        # Formatting
        plt.title(f"Tool: {tool_name}\nMeasureType: {mtype} – Cycles Aligned at T=0")
        plt.xlabel("Relative Time (seconds from start of cycle)")
        plt.ylabel("Value")
        plt.legend(loc='best')
        plt.tight_layout()

        # Show the plot
        plt.show()
