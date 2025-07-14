import pandas as pd
import openpyxl

# Path to the Excel file
file_path = "attached_assets/Dashboard_V1_2025_01_25.xlsx"

# Use openpyxl to get sheet names
wb = openpyxl.load_workbook(file_path, read_only=True)
print("Available sheets:", wb.sheetnames)

# Try to load using pandas
try:
    df = pd.read_excel(file_path, sheet_name=0)
    print("\nFirst few rows of data:")
    print(df.head())
    
    print("\nColumn names and indices:")
    for i, col in enumerate(df.columns):
        print(f"Column {i} ('{chr(65+i)}'): {col}")
except Exception as e:
    print("Error loading with pandas:", str(e))

# Also try to load another example file
try:
    po_file = "attached_assets/Chemical - PO Line Detail_18032025_1848.xlsx"
    po_df = pd.read_excel(po_file)
    print("\nPO Detail file columns:")
    for i, col in enumerate(po_df.columns):
        print(f"Column {i} ('{chr(65+i)}'): {col}")
except Exception as e:
    print("Error loading PO file with pandas:", str(e))