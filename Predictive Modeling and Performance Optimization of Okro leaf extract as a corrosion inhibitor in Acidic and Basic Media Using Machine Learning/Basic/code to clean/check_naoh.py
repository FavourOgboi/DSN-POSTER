import pandas as pd

# Load the Excel file
xl = pd.ExcelFile('../Machine Learning-Driven Corrosion Inhibition Study Okro Leaf Extract in Acidic and Basic Media/DESIGN OF EXPERIMENT NAOH.xlsx')

print('Sheets:', xl.sheet_names)

# For each sheet, print head
for sheet in xl.sheet_names:
    print(f'\nSheet: {sheet}')
    df = pd.read_excel(xl, sheet_name=sheet)
    print(f'Columns: {list(df.columns)}')
    print(f'Shape: {df.shape}')
    print(f'Dtypes:\n{df.dtypes}')
    try:
        print(df.head(10).to_string())
    except UnicodeEncodeError:
        print('Unicode error in data, printing repr:')
        print(repr(df.head(10)))
