import pandas as pd
import os
import glob

# Look for CSV files in the saved_data directory
files = glob.glob('saved_data/*.csv')

if files:
    for file in files:
        print(f"Checking file: {file}")
        try:
            df = pd.read_csv(file)
            
            # Check if Region column exists
            if 'Region' in df.columns:
                regions = df['Region'].unique().tolist()
                print(f"Available regions in {os.path.basename(file)}:")
                for region in sorted(regions):
                    print(f"  - {region}")
            else:
                # Try alternate column names that might contain region information
                alternate_columns = ['Project Region', 'region', 'REGION', 'Dimension4 Description']
                found = False
                for col in alternate_columns:
                    if col in df.columns:
                        regions = df[col].unique().tolist()
                        print(f"Available {col} values in {os.path.basename(file)}:")
                        for region in sorted(regions):
                            print(f"  - {region}")
                        found = True
                        break
                
                if not found:
                    print(f"No Region column found in {os.path.basename(file)}")
        except Exception as e:
            print(f"Error reading {file}: {str(e)}")
else:
    print("No CSV files found in saved_data directory")