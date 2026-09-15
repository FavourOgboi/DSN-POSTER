import pandas as pd
import re
import os

# Load the Excel file
xl = pd.ExcelFile('../Machine Learning-Driven Corrosion Inhibition Study Okro Leaf Extract in Acidic and Basic Media/Basic/DESIGN OF EXPERIMENT NAOH.xlsx')

# Read the tafel sheet
df = pd.read_excel(xl, sheet_name='tafel')

# Rename columns for clarity
df.columns = ['Sample', 'E_corr_V', 'j_corr_A_cm2', 'I_corr_A', 'CR_mm_yr', 'PR_ohm']

# Function to parse Sample
def parse_sample(sample):
    # Examples: "1.75M,50PPM, 30" -> NaOH_M=1.75, Inhibitor_ppm=50, Temp_C=30
    match = re.match(r'(\d+(?:\.\d+)?)M\s*,\s*(\d+)\s*PPM\s*,\s*(\d+)', sample)
    if match:
        naoh_m = float(match.group(1))
        inhibitor_ppm = int(match.group(2))
        temp_c = int(match.group(3))
        return naoh_m, inhibitor_ppm, temp_c
    else:
        return None, None, None

# Apply parsing
parsed = df['Sample'].apply(parse_sample)
df['NaOH_M'] = parsed.apply(lambda x: x[0])
df['Inhibitor_ppm'] = parsed.apply(lambda x: x[1])
df['Temp_C'] = parsed.apply(lambda x: x[2])

# Check which failed
failed = df[df['NaOH_M'].isnull()]
if not failed.empty:
    print("Failed to parse samples:")
    for s in failed['Sample']:
        print(f"  '{s}'")

# Drop rows with parsing errors
df = df.dropna(subset=['NaOH_M', 'Inhibitor_ppm', 'Temp_C'])

# Convert to appropriate types
df['NaOH_M'] = df['NaOH_M'].astype(float)
df['Inhibitor_ppm'] = df['Inhibitor_ppm'].astype(int)
df['Temp_C'] = df['Temp_C'].astype(int)

# Reorder columns
df = df[['Sample', 'NaOH_M', 'Inhibitor_ppm', 'Temp_C', 'E_corr_V', 'j_corr_A_cm2', 'I_corr_A', 'CR_mm_yr', 'PR_ohm']]

# Check for missing values
print("Missing values:")
print(df.isnull().sum())

# Summary
print("\nDataset shape:", df.shape)
print("\nUnique values:")
print("NaOH_M:", sorted(df['NaOH_M'].unique()))
print("Inhibitor_ppm:", sorted(df['Inhibitor_ppm'].unique()))
print("Temp_C:", sorted(df['Temp_C'].unique()))

# Save cleaned data
output_dir = '../Machine Learning-Driven Corrosion Inhibition Study Okro Leaf Extract in Acidic and Basic Media/Basic/cleaned data naoh/'
os.makedirs(output_dir, exist_ok=True)
df.to_csv(output_dir + 'cleaned_NAOH_tafel_data.csv', index=False)
print(f"\nCleaned data saved to '{output_dir}cleaned_NAOH_tafel_data.csv'")

# Now clean OCP sheet
print("\n--- Cleaning OCP Sheet ---")
df_ocp = pd.read_excel(xl, sheet_name='OCP')

# The columns are grouped: each sample has 3 columns: OCP value (V), Time (s), WE(1).Potential (V)
# But from the data, first row is headers, then data.

# Actually, looking at the output, the columns are named like '1.75M,50PPM, 30', then Unnamed:1, Unnamed:2, etc.
# And the first row under that is 'OCP value (V)', 'Time (s)', 'WE(1).Potential (V)', NaN, then next sample.

# So, the data is stacked horizontally.

# To clean, I need to find the sample columns and extract.

# Let's find columns that are not 'Unnamed'
sample_cols = [col for col in df_ocp.columns if not col.startswith('Unnamed')]

ocp_data = []

for i, sample in enumerate(sample_cols):
    start_col = df_ocp.columns.get_loc(sample)
    # Assume 3 columns per sample: Time, OCP, Potential
    if start_col + 2 < len(df_ocp.columns):
        time_col = df_ocp.iloc[:, start_col + 1]
        ocp_col = df_ocp.iloc[:, start_col]
        pot_col = df_ocp.iloc[:, start_col + 2]
        # Skip the header row
        for j in range(1, len(df_ocp)):
            if pd.notna(time_col.iloc[j]) and pd.notna(ocp_col.iloc[j]):
                ocp_data.append({
                    'Sample': sample,
                    'Time_s': time_col.iloc[j],
                    'OCP_V': ocp_col.iloc[j],
                    'Potential_V': pot_col.iloc[j]
                })

df_ocp_clean = pd.DataFrame(ocp_data)

# Parse Sample
parsed_ocp = df_ocp_clean['Sample'].apply(parse_sample)
df_ocp_clean['NaOH_M'] = parsed_ocp.apply(lambda x: x[0])
df_ocp_clean['Inhibitor_ppm'] = parsed_ocp.apply(lambda x: x[1])
df_ocp_clean['Temp_C'] = parsed_ocp.apply(lambda x: x[2])

# Drop failed parses
df_ocp_clean = df_ocp_clean.dropna(subset=['NaOH_M'])

print(f"OCP cleaned shape: {df_ocp_clean.shape}")
df_ocp_clean.to_csv(output_dir + 'cleaned_NAOH_OCP_data.csv', index=False)
print(f"OCP data saved to '{output_dir}cleaned_NAOH_OCP_data.csv'")

# Now clean lsv sheet
print("\n--- Cleaning LSV Sheet ---")
df_lsv = pd.read_excel(xl, sheet_name='lsv')

# Similar structure
sample_cols_lsv = [col for col in df_lsv.columns if not col.startswith('Unnamed')]

lsv_data = []

for i, sample in enumerate(sample_cols_lsv):
    start_col = df_lsv.columns.get_loc(sample)
    # Assume 3 columns: Potential, Current1, Current2
    if start_col + 2 < len(df_lsv.columns):
        pot_col = df_lsv.iloc[:, start_col]
        curr1_col = df_lsv.iloc[:, start_col + 1]
        curr2_col = df_lsv.iloc[:, start_col + 2]
        for j in range(1, len(df_lsv)):
            if pd.notna(pot_col.iloc[j]) and pd.notna(curr1_col.iloc[j]):
                lsv_data.append({
                    'Sample': sample,
                    'Potential_V': pot_col.iloc[j],
                    'Current1_A': curr1_col.iloc[j],
                    'Current2_A': curr2_col.iloc[j]
                })

df_lsv_clean = pd.DataFrame(lsv_data)

# Parse Sample
parsed_lsv = df_lsv_clean['Sample'].apply(parse_sample)
df_lsv_clean['NaOH_M'] = parsed_lsv.apply(lambda x: x[0])
df_lsv_clean['Inhibitor_ppm'] = parsed_lsv.apply(lambda x: x[1])
df_lsv_clean['Temp_C'] = parsed_lsv.apply(lambda x: x[2])

# Drop failed
df_lsv_clean = df_lsv_clean.dropna(subset=['NaOH_M'])

print(f"LSV cleaned shape: {df_lsv_clean.shape}")
df_lsv_clean.to_csv(output_dir + 'cleaned_NAOH_LSV_data.csv', index=False)
print(f"LSV data saved to '{output_dir}cleaned_NAOH_LSV_data.csv'")
