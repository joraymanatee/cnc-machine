import pandas as pd
import numpy as np

def detect_broken_tool(csv_path_before, csv_path_after, drop_threshold=40.0, corr_threshold=0.85):

    df_before = pd.read_csv(csv_path_before)
    df_after = pd.read_csv(csv_path_after)

    for df in [df_before, df_after]:
        df.columns = df.columns.str.strip()
        df['Tool'] = df['Tool'].astype(str)
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df.dropna(subset=['Tool', 'Value'], inplace=True)

    broken_tools = []

    tools = sorted(set(df_before['Tool'].unique()) & set(df_after['Tool'].unique()))

    for tool in tools:
        sig_before = df_before[df_before['Tool'] == tool]['Value'].dropna().values
        sig_after = df_after[df_after['Tool'] == tool]['Value'].dropna().values

        n = min(len(sig_before), len(sig_after))
        if n < 10:
            continue

        sig_before = sig_before[:n]
        sig_after = sig_after[:n]

        mean_before = np.mean(sig_before)
        mean_after = np.mean(sig_after)
        drop_pct = 100 * (mean_before - mean_after) / mean_before
        corr = np.corrcoef(sig_before, sig_after)[0, 1]

        if drop_pct > drop_threshold and corr < corr_threshold:
            broken_tools.append({
                'Tool': tool,
                'Mean_Before': mean_before,
                'Mean_After': mean_after,
                'Drop %': drop_pct,
                'Correlation': corr,
                'LikelyBroken': True
            })

    result_df = pd.DataFrame(broken_tools).sort_values(by='Drop_%', ascending=False)

    
    print("Broken Tool Detected:")
    for _, row in result_df.iterrows():
        print(f"Tool {row['Tool']}: Drop {row['Drop %']:.1f}%, Corr = {row['Correlation']:.2f}")

    return result_df


result = detect_broken_tool(
    '/Users/josephpieper/Avalon Internship/Machining Code/carrier 439 - anomaly/power vibration data 0952 439.csv',
    '/Users/josephpieper/Avalon Internship/Machining Code/carrier 440/power vibration data 1010 440.csv',
    drop_threshold=10.0,
)