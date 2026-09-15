import pandas as pd

df = pd.read_csv('Time/all_no_temp_cleaned.csv')
df = df[['acid_m','time_h','conc_ppm','initial_weight_g','final_weight_g','wl_g','wl_mg','ie_percent','cr_mm_yr']]
df.to_csv('Time/all_no_temp_cleaned.csv', index=False)
print('Removed log_wl column')
