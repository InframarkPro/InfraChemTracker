import pandas as pd
import sys

def print_excel_info(file_path):
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Print column names
        print("Column names:")
        for col in df.columns:
            print(f"- {col}")
        
        # Print first few rows sample
        print("\nSample data (first 3 rows):")
        print(df.head(3).to_string())
        
        # Print data types
        print("\nData types:")
        for col, dtype in df.dtypes.items():
            print(f"- {col}: {dtype}")
            
        # Print basic statistics
        print("\nBasic info:")
        print(f"- Row count: {len(df)}")
        print(f"- Column count: {len(df.columns)}")
        
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"Analyzing file: {file_path}")
        print_excel_info(file_path)
    else:
        print("Please provide a file path as argument")
