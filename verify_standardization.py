"""
Standardization Verification Script

This script tests the new standardized data processing modules to ensure they correctly
handle both PO Line Detail and Non-PO Invoice data formats.
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='standardization_verification.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

# Add console handler for direct output
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

def verify_file_processing(file_path, expected_type):
    """
    Verify that a file can be processed correctly using the standardized processor.
    
    Args:
        file_path: Path to the file to process
        expected_type: Expected report type ('po_line_detail' or 'non_po_invoice')
        
    Returns:
        bool: True if verification passed, False otherwise
    """
    try:
        from utils.report_processor_manager import process_report
        
        logger.info(f"Verifying file processing for: {file_path}")
        
        # Process the file
        df, report_type = process_report(file_path)
        
        if df is None:
            logger.error(f"Failed to process file: {file_path}")
            return False
        
        logger.info(f"Successfully processed file as {report_type}")
        logger.info(f"DataFrame shape: {df.shape}")
        
        # Verify key columns are present
        required_columns = ['supplier', 'chemical', 'type', 'po_count']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        # Verify PO count is calculated correctly
        if 'po_count' in df.columns:
            total_po_count = df['po_count'].sum()
            logger.info(f"Total PO count: {total_po_count}")
            
            # This should match the number of rows for our line-item based counting
            if total_po_count != len(df):
                logger.warning(f"PO count ({total_po_count}) does not match row count ({len(df)})")
        
        # Verify purchase types 
        if 'type' in df.columns:
            type_counts = df['type'].value_counts().to_dict()
            logger.info(f"Purchase types: {type_counts}")
            
            # At minimum we should have Catalog and Free Text types
            if 'Catalog' not in type_counts and 'Free Text' not in type_counts:
                logger.warning("Missing expected purchase types")
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying file processing: {e}")
        return False

def verify_database_operations(df, report_type, filename):
    """
    Verify that database operations work correctly with the standardized data.
    
    Args:
        df: DataFrame to save
        report_type: Report type ('po_line_detail' or 'non_po_invoice')
        filename: Original filename
        
    Returns:
        bool: True if verification passed, False otherwise
    """
    try:
        # Simulate database operations with a temporary file
        temp_file = f"temp_verification_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        logger.info(f"Verifying database operations with temp file: {temp_file}")
        
        # Save the data
        df.to_csv(temp_file, index=False)
        logger.info(f"Saved data to {temp_file}")
        
        # Read it back
        df_read = pd.read_csv(temp_file)
        logger.info(f"Read data from {temp_file}")
        
        # Verify the data is the same
        if len(df) != len(df_read):
            logger.error(f"Data length mismatch: {len(df)} vs {len(df_read)}")
            return False
        
        # Clean up
        os.remove(temp_file)
        logger.info(f"Removed temporary file {temp_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying database operations: {e}")
        return False

def main():
    """Main verification function"""
    logger.info("Starting standardization verification")
    
    # Get test files
    test_files = []
    
    if len(sys.argv) > 1:
        # Use files specified in command line
        test_files = sys.argv[1:]
    else:
        # Default test files
        asset_dir = "attached_assets"
        if os.path.exists(asset_dir):
            for filename in os.listdir(asset_dir):
                if filename.endswith(".xls") or filename.endswith(".xlsx"):
                    test_files.append(os.path.join(asset_dir, filename))
    
    if not test_files:
        logger.error("No test files found")
        return
    
    logger.info(f"Found {len(test_files)} test files to verify")
    
    # Process each file
    success_count = 0
    failure_count = 0
    
    for file_path in test_files:
        logger.info(f"Processing file: {file_path}")
        
        # Determine expected type based on filename
        filename = os.path.basename(file_path).lower()
        if "chemical" in filename:
            expected_type = "chemical_spend_by_supplier"
        elif "po" in filename:
            expected_type = "po_line_detail"
        elif "invoice" in filename:
            expected_type = "non_po_invoice"
        else:
            expected_type = None
            
        # Verify file processing
        if verify_file_processing(file_path, expected_type):
            logger.info(f"✅ File processing verification passed for {file_path}")
            
            # If processing succeeded, also verify database operations
            from utils.report_processor_manager import process_report
            df, report_type = process_report(file_path)
            
            if df is not None and verify_database_operations(df, report_type, os.path.basename(file_path)):
                logger.info(f"✅ Database operations verification passed for {file_path}")
                success_count += 1
            else:
                logger.error(f"❌ Database operations verification failed for {file_path}")
                failure_count += 1
        else:
            logger.error(f"❌ File processing verification failed for {file_path}")
            failure_count += 1
    
    # Report overall results
    logger.info("=" * 50)
    logger.info(f"Verification complete: {success_count} passed, {failure_count} failed")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()