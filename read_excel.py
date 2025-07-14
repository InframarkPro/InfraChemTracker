import pandas as pd
import sys

def read_excel_file(file_path):
    """Read the Excel file and print its structure and sample data."""
    try:
        # Read the Excel file
        print(f"Attempting to read file: {file_path}")
        df = pd.read_excel(file_path)
        
        # Print general information
        print("\nFile successfully read!")
        print(f"Number of rows: {len(df)}")
        print(f"Number of columns: {len(df.columns)}")
        
        # Print column names and data types
        print("\nColumns and data types:")
        for col in df.columns:
            print(f"  - {col} ({df[col].dtype})")
        
        # Print sample data (first 5 rows)
        print("\nSample data (first 5 rows):")
        print(df.head(5).to_string())
        
        # Check for any key columns related to KPIs
        kpi_related_columns = []
        for col in df.columns:
            col_lower = col.lower()
            if any(term in col_lower for term in ['cost', 'price', 'quantity', 'type', 'category', 'supplier', 'date']):
                kpi_related_columns.append(col)
        
        if kpi_related_columns:
            print("\nPotential KPI-related columns:")
            for col in kpi_related_columns:
                print(f"  - {col}")
        
    except Exception as e:
        print(f"Error reading file: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        read_excel_file(file_path)
    else:
        read_excel_file("attached_assets/Dashboard_V1_2025_01_25.xlsx")