import pandas as pd
import glob
import sys

# Look for Non-PO Invoice files
files = [f for f in glob.glob('saved_data/*.csv') if 'Non-PO' in f]

if not files:
    print("No Non-PO Invoice files found")
    sys.exit(0)

print(f"Found {len(files)} Non-PO Invoice files")

# Try to open each file and check for regions
for file in files:
    print(f"\nChecking file: {file}")
    try:
        # Read in chunks to avoid memory issues
        for chunk in pd.read_csv(file, chunksize=1000):
            if 'Region' in chunk.columns:
                regions = chunk['Region'].dropna().unique()
                print("Regions found:")
                for region in sorted(regions):
                    print(f"  - {region}")
                break
            else:
                print("No 'Region' column found, checking alternatives")
                alt_columns = ['Project Region', 'Dimension4 Description']
                for col in alt_columns:
                    if col in chunk.columns:
                        regions = chunk[col].dropna().unique()
                        print(f"{col} values found:")
                        for region in sorted(regions):
                            print(f"  - {region}")
                        break
                break
    except Exception as e:
        print(f"Error reading file: {str(e)}")