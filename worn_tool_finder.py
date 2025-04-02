import os
import glob
import pandas as pd
import numpy as np

base_path = '/Users/josephpieper/Avalon Internship/Machining Code/'
csv_files = glob.glob(os.path.join(base_path, '**/*.csv'))

all_dfs = []

for file in csv_files:
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    all_dfs.append(df)

df_all = pd.concat(all_dfs, ignore_index=True)
df_all['Tool'] = df_all['Tool'].astype(str)
df_all['Cycle'] = pd.to_numeric(df_all['Cycle'], errors='coerce')

df_cycles = df_all[df_all['Cycle'].between(438, 447)]

grouped = df_cycles.groupby(['Tool', 'Cycle'])['Value'].agg(['mean', 'std', 'max', 'min']).reset_index()
mean_pivot = grouped.pivot(index='Cycle', columns='Tool', values='mean')


worn_tools = []

for tool in mean_pivot.columns:
    series = mean_pivot[tool].loc[438:444]

    x = np.arange(len(series))
    y = series.values
    slope, we = np.polyfit(x, y, 1)

    if slope > 0.001:  # Gradual Rise in Vibration (This can be adjusted.) (More vibration means more wear.)
        try:
            mean_447 = mean_pivot.at[447, tool]
            if mean_447 < y[-1] * 0.7:  # This is checking if replacing the tool made the problem better.
                worn_tools.append((tool, slope))
        except KeyError:
            continue


print("Worn Tool Replaced in Cycle 447:")
for t, s in worn_tools:
    print(f"Tool {t}, increasing slope = {s:.4f}")
