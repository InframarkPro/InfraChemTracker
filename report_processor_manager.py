"""
Report Processor Manager

This module manages the processing of various report formats by selecting and applying
the appropriate processor based on the report type or content.
"""

import os
import re
import pandas as pd
from .report_processors import process_chemical_spend_by_supplier_report

def detect_report_type(df, filename=""):
    """
    Detect the type of report based on its content and/or filename.
    
    Args:
        df: DataFrame containing the report data
        filename: Original filename (optional)
        
    Returns:
        str: Report type identifier
    """
    # Check if it's a Chemical Spend by Supplier report
    if is_chemical_spend_by_supplier_report(df, filename):
        return 'chemical_spend'
    
    # Default to generic report if no specific type is detected
    return 'generic'

def is_chemical_spend_by_supplier_report(df, filename=""):
    """
    Check if a report is a Chemical Spend by Supplier report.
    
    Args:
        df: DataFrame containing the report data
        filename: Original filename (optional)
        
    Returns:
        bool: True if the report is a Chemical Spend by Supplier report
    """
    # Check filename for indicators
    if filename:
        filename_lower = filename.lower()
        if any(pattern in filename_lower for pattern in ['chemical_spend', 'chem_spend', 'chemsupplier', 'chemical-supplier']):
            return True
    
    # Check column names for indicators
    columns = [str(col).lower() for col in df.columns]
    
    # Look for characteristic columns of Chemical Spend reports
    chemical_indicators = [
        'chemical', 'vendor', 'supplier', 'bill', 'description'
    ]
    
    # Count how many chemical indicators are present
    matches = sum(1 for ind in chemical_indicators if any(ind in col for col in columns))
    
    # If at least 3 indicators are present, it's likely a Chemical Spend report
    return matches >= 3

def process_report(input_data, report_type=None, filename=""):
    """
    Process a report using the appropriate processor.
    
    Args:
        input_data: DataFrame containing the report data or a file path to the data
        report_type: Report type (if known)
        filename: Original filename (optional)
        
    Returns:
        tuple: (processed_df, detected_report_type)
    """
    # Check if input_data is a string (file path)
    if isinstance(input_data, str):
        # Load the data from the file path
        import pandas as pd
        import os
        
        file_path = input_data
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        # Use the file name for detection if not provided
        if not filename:
            filename = os.path.basename(file_path)
    else:
        # Input is already a DataFrame
        df = input_data
    
    # Detect report type if not provided
    if not report_type:
        report_type = detect_report_type(df, filename)
    
    # Process based on report type
    if report_type == 'chemical_spend':
        processed_df = process_chemical_spend_by_supplier_report(df)
    else:
        # For generic reports, return as-is
        processed_df = df.copy()
    
    return processed_df, report_type