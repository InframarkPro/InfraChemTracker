"""
Test script for verifying the removal of the Date Created column from Chemical Spend by Supplier reports.
"""

import os
import pandas as pd
from utils.report_processors.chemical_spend_by_supplier import process_chemical_spend_by_supplier_report

def test_date_created_removal(file_path):
    """Test the removal of Date Created column."""
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return
    
    print(f"Testing Date Created removal for file: {file_path}")
    
    # Try to detect file format based on extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.csv':
        try:
            df = pd.read_csv(file_path, encoding='latin1')
            print("Read CSV file with Latin-1 encoding")
        except Exception as latin_err:
            try:
                # Fallback to UTF-8
                df = pd.read_csv(file_path, encoding='utf-8')
                print("Read CSV file with UTF-8 encoding")
            except Exception as utf_err:
                error_msg = f"Failed to read CSV file with both encodings: {latin_err}, {utf_err}"
                print(error_msg)
                raise ValueError(error_msg)
    elif ext.lower() in ['.xls', '.xlsx']:
        try:
            df = pd.read_excel(file_path)
            print("Read Excel file")
        except Exception as e:
            error_msg = f"Failed to read Excel file: {e}"
            print(error_msg)
            raise ValueError(error_msg)
    else:
        print(f"Unsupported file format: {ext}")
        return
    
    # Check if Date Created is present
    print(f"Original columns: {df.columns.tolist()}")
    has_date_created = 'Date Created' in df.columns
    print(f"'Date Created' column present in original data: {has_date_created}")
    
    if not has_date_created:
        print("Warning: 'Date Created' column not found in the original file, nothing to remove.")
    
    # Process the report
    processed_df = process_chemical_spend_by_supplier_report(df)
    
    # Check if Date Created was removed
    print(f"Processed columns: {processed_df.columns.tolist()}")
    still_has_date_created = 'Date Created' in processed_df.columns
    print(f"'Date Created' column present in processed data: {still_has_date_created}")
    
    if has_date_created and still_has_date_created:
        print("Error: 'Date Created' column was not removed as expected")
    elif has_date_created and not still_has_date_created:
        print("Success: 'Date Created' column was successfully removed")
    elif not has_date_created:
        print("No change needed: 'Date Created' column was not in the original data")
    
    # Return processed data for examination
    return processed_df

if __name__ == "__main__":
    # Test with the sample file
    sample_file = "attached_assets/ChemicalSpendbySupplier-YongdaLi639.csv"
    processed_df = test_date_created_removal(sample_file)
    
    if processed_df is not None:
        print("\nTest completed successfully!")