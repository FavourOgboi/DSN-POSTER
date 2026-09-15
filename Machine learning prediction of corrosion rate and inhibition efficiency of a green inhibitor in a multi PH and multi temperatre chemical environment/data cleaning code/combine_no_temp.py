import pandas as pd

# Read all no temp files
df_05 = pd.read_csv('Time/0.5M_cleaned.csv')
df_1 = pd.read_csv('Time/1M_cleaned.csv')
df_15 = pd.read_csv('Time/1.5M_cleaned.csv')

# Combine
df_all = pd.concat([df_05, df_1, df_15], ignore_index=True)

# Save
df_all.to_csv('Time/all_no_temp_cleaned.csv', index=False)
print('Combined all no temp data')
