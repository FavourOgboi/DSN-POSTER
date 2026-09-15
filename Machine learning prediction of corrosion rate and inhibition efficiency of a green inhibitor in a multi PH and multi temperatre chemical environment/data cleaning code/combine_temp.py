import pandas as pd

# Read all temp files
df_05 = pd.read_csv('Temperature/TEMP DATA 0.5M_cleaned.csv')
df_1 = pd.read_csv('Temperature/TEMP DATA 1.0M_cleaned.csv')
df_15 = pd.read_csv('Temperature/TEMP DATA 1.5M_cleaned.csv')

# Combine
df_all = pd.concat([df_05, df_1, df_15], ignore_index=True)

# Save
df_all.to_csv('Temperature/all_temp_cleaned.csv', index=False)
print('Combined all temp data')
