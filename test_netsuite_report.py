"""
Test script for the Chemical Spend by Supplier report processor.
This script tests the processor with a sample file.
"""

import os
import sys
import logging
import pandas as pd
from utils.report_processor_manager import process_report, get_supported_report_types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_process_file(file_path):
    """Test processing a specific file."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    
    logger.info(f"Testing processor with file: {file_path}")
    logger.info(f"File size: {os.path.getsize(file_path) / 1024:.2f} KB")
    
    # Test direct detection first
    from utils.report_processors.chemical_spend_by_supplier import is_chemical_spend_report
    is_detected = is_chemical_spend_report(file_path)
    logger.info(f"Direct detection test result: {is_detected}")
    
    # Get a list of supported report types
    report_types = get_supported_report_types()
    logger.info(f"Supported report types: {[rt['display_name'] for rt in report_types]}")
    
    # Process the file
    df, report_type = process_report(file_path)
    
    if df is not None:
        logger.info(f"Successfully processed file as {report_type}")
        logger.info(f"DataFrame shape: {df.shape}")
        logger.info(f"DataFrame columns: {df.columns.tolist()}")
        
        # Display a sample of the data
        logger.info("Sample data:")
        print(df.head(5).to_string())
        
        # Display some summary statistics
        if 'total_cost' in df.columns:
            total_cost = df['total_cost'].sum()
            logger.info(f"Total cost: ${total_cost:.2f}")
        
        if 'supplier' in df.columns:
            supplier_count = df['supplier'].nunique()
            logger.info(f"Number of suppliers: {supplier_count}")
            
        if 'chemical' in df.columns:
            chemical_count = df['chemical'].nunique()
            logger.info(f"Number of chemicals: {chemical_count}")
            
        if 'type' in df.columns:
            type_counts = df['type'].value_counts()
            logger.info(f"Purchase types: {type_counts.to_dict()}")
    else:
        logger.error("Failed to process file")
        
    # Try direct file processing as a last resort
    from utils.report_processors.chemical_spend_by_supplier import process_chemical_spend_report
    logger.info("Trying direct file processing (bypassing detection)...")
    df_direct = process_chemical_spend_report(file_path)
    if df_direct is not None:
        logger.info(f"Direct processing successful, shape: {df_direct.shape}")
        logger.info(f"Columns: {df_direct.columns.tolist()}")
    else:
        logger.error("Direct processing failed as well")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        logger.error("Please provide a file path as an argument")
        sys.exit(1)
    
    file_path = sys.argv[1]
    test_process_file(file_path)

if __name__ == "__main__":
    main()