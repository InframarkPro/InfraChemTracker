import pandas as pd

# Load the Excel file
excel_path = './attached_assets/Non-PO Invoice Chemical GL_19032025_0057.xlsx'
df = pd.read_excel(excel_path)

# Print basic information
print(f"Excel file contains {len(df)} rows and {len(df.columns)} columns")

# Print column information
print("\nColumn information:")
for i, col in enumerate(df.columns):
    print(f"Column {i} (Letter {chr(65+i)}): {col}")

# Specifically examine Column C (index 2)
print("\nAnalyzing Column C (Supplier information):")
if len(df.columns) > 2:
    c_column = df.iloc[:, 2]
    print(f"Column C name: {df.columns[2]}")
    print(f"First 10 values in Column C:")
    for i, val in enumerate(c_column.head(10)):
        print(f"  Row {i+1}: {val}")
    
    # Count unique values
    unique_c_values = c_column.unique()
    print(f"\nFound {len(unique_c_values)} unique values in Column C")
    print("Top 10 most common values:")
    value_counts = c_column.value_counts().head(10)
    for val, count in value_counts.items():
        print(f"  {val}: {count} occurrences")
else:
    print("Column C not found in the spreadsheet")

# Check if Chemical or Description columns exist
chemical_cols = [col for col in df.columns if 'Chemical' in str(col) or 'Description' in str(col)]
print("\nPotential Chemical or Description columns found:", chemical_cols)
if chemical_cols:
    for col in chemical_cols[:2]:  # Show just first 2 to keep output manageable
        print(f"\nSample values from {col}:")
        print(df[col].dropna().head(5))

# Check for invoice or order information
invoice_cols = [col for col in df.columns if 'Invoice' in str(col) or 'Order' in str(col)]
print("\nInvoice or Order columns found:", invoice_cols)
if invoice_cols:
    for col in invoice_cols[:2]:  # Show just first 2
        print(f"\nSample values from {col}:")
        print(df[col].dropna().head(5))