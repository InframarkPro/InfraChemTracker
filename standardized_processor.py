"""
Standardized Data Processor

This module provides consistent data processing functions for both PO Line Detail and Non-PO Invoice data,
standardizing column handling and region extraction across both data types.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
import re
import io
from .report_processor_manager import process_report
from .data_processor import clean_region_names

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('data_processor')

# Define standard column mappings for consistent processing
STANDARD_MAPPINGS = {
    # Standard column name -> [PO Line Detail source, Non-PO Invoice source, Alt Source 1, Alt Source 2,...]
    # The first column that exists in the DataFrame will be used
    "Date": ["Purchase Order: Confirmation Date", "Invoice: Created Date", "Date Created", "Date Due"],
    "Facility": ["Purchase Order: Supplier", "Dimension5 Description", "{Vendor}", "Department: Name", "Department", "Supplier: Name"],
    "Chemical": ["Item Description", "Dimension3 Description", "Description", "Item: Category"],
    "Order_ID": ["Order Identifier", "Invoice: Number", "Bill # (Supplier Invoice #)"],
    "Total_Cost": ["", "Net Amount", "Total"],  # PO Line Detail calculates this from quantity * price
    "Supplier": ["Purchase Order: Supplier", "Supplier: Name", "{Vendor}"],
    "Type": ["Type", "Invoice: Type", "Transaction Type"],  # Column P in PO Line Detail files
    "Region": ["Purchase Requisition: Our Reference", "Dimension4 Description", "Project Region"],  # Column M in PO Line Detail files
    "Quantity": ["Connected", "QTY", "Connected Quantity", "Confirmed Quantity"],  # Now using 'Connected' (column J) instead of 'Confirmed Quantity'
    "Unit_Price": ["Confirmed Unit Price", "", "Unit Price"]
}

def standardize_columns(df, report_type):
    """
    Adds standardized column names to a DataFrame while preserving all original columns.
    
    Args:
        df: DataFrame to standardize
        report_type: Type of report ("po_line_detail" or "non_po_invoice")
        
    Returns:
        DataFrame: DataFrame with added standard columns
    """
    logger.info(f"Standardizing columns for {report_type} report")
    logger.info(f"Original columns: {df.columns.tolist()}")
    
    # Create a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Get the index for the current report type (0 for PO, 1 for Non-PO)
    type_idx = 0 if report_type == "po_line_detail" else 1
    
    # Add standard columns based on mappings
    for std_col, source_cols in STANDARD_MAPPINGS.items():
        # Skip if standard column already exists
        if std_col in processed_df.columns:
            continue
            
        # Try all source columns for this field, not just the primary one for the report type
        found_source = False
        
        # First try the primary column for this report type
        primary_source_col = source_cols[type_idx] if len(source_cols) > type_idx else None
        if primary_source_col and primary_source_col in processed_df.columns:
            processed_df[std_col] = processed_df[primary_source_col]
            logger.info(f"Added standard column '{std_col}' from primary source '{primary_source_col}'")
            found_source = True
        else:
            # Try all alternative columns
            for alt_source_col in source_cols:
                if alt_source_col and alt_source_col in processed_df.columns and not found_source:
                    processed_df[std_col] = processed_df[alt_source_col]
                    logger.info(f"Added standard column '{std_col}' from alternative source '{alt_source_col}'")
                    found_source = True
                    break
    
    # Special handling for Total_Cost in PO Line Detail (calculated from quantity * price)
    if report_type == "po_line_detail" and "Total_Cost" not in processed_df.columns:
        # First, try to use Connected quantity (column J) as requested
        if "Confirmed Unit Price" in processed_df.columns and "Connected" in processed_df.columns:
            # Clean and convert price and quantity to numeric
            try:
                if not processed_df["Confirmed Unit Price"].isna().all():
                    # Try different formats of price values
                    unit_price = processed_df["Confirmed Unit Price"].astype(str).str.replace(',', '').str.replace('$', '')
                    unit_price = pd.to_numeric(unit_price, errors='coerce').fillna(0)
                    
                    # Use Connected quantity from column J
                    quantity = processed_df["Connected"].astype(str).str.replace(',', '')
                    quantity = pd.to_numeric(quantity, errors='coerce').fillna(0)
                    
                    # Calculate total cost
                    processed_df["Total_Cost"] = unit_price * quantity
                    logger.info("Added 'Total_Cost' calculated from price * Connected quantity")
                else:
                    # If all prices are NA, set Total_Cost to 0
                    processed_df["Total_Cost"] = 0
                    logger.warning("All prices are NA, setting Total_Cost to 0")
            except Exception as e:
                logger.error(f"Error calculating Total_Cost with Connected quantity: {str(e)}")
                # Fall back to Confirmed Quantity if there's an error
                try:
                    if "Confirmed Quantity" in processed_df.columns:
                        unit_price = processed_df["Confirmed Unit Price"].astype(str).str.replace(',', '').str.replace('$', '')
                        unit_price = pd.to_numeric(unit_price, errors='coerce').fillna(0)
                        
                        quantity = processed_df["Confirmed Quantity"].astype(str).str.replace(',', '')
                        quantity = pd.to_numeric(quantity, errors='coerce').fillna(0)
                        
                        processed_df["Total_Cost"] = unit_price * quantity
                        logger.info("Fallback: Added 'Total_Cost' calculated from price * Confirmed Quantity")
                    else:
                        processed_df["Total_Cost"] = 0
                        logger.warning("Missing Connected or Confirmed Quantity columns, setting Total_Cost to 0")
                except Exception as e2:
                    logger.error(f"Error in fallback Total_Cost calculation: {str(e2)}")
                    processed_df["Total_Cost"] = 0
        # Fallback to Confirmed Quantity if Connected column is not available
        elif "Confirmed Unit Price" in processed_df.columns and "Confirmed Quantity" in processed_df.columns:
            # Clean and convert price and quantity to numeric
            try:
                if not processed_df["Confirmed Unit Price"].isna().all():
                    # Try different formats of price values
                    unit_price = processed_df["Confirmed Unit Price"].astype(str).str.replace(',', '').str.replace('$', '')
                    unit_price = pd.to_numeric(unit_price, errors='coerce').fillna(0)
                    
                    quantity = processed_df["Confirmed Quantity"].astype(str).str.replace(',', '')
                    quantity = pd.to_numeric(quantity, errors='coerce').fillna(0)
                    
                    # Calculate total cost
                    processed_df["Total_Cost"] = unit_price * quantity
                    logger.info("Added 'Total_Cost' calculated from price * Confirmed Quantity (Connected column not found)")
                else:
                    # If all prices are NA, set Total_Cost to 0
                    processed_df["Total_Cost"] = 0
                    logger.warning("All prices are NA, setting Total_Cost to 0")
            except Exception as e:
                logger.error(f"Error calculating Total_Cost: {str(e)}")
                processed_df["Total_Cost"] = 0
        else:
            # Set a default Total_Cost column if needed values are missing
            processed_df["Total_Cost"] = 0
            logger.warning("Missing price or quantity columns, setting Total_Cost to 0")
    
    # Handle missing Date column with appropriate default
    if "Date" not in processed_df.columns:
        processed_df["Date"] = pd.to_datetime("today")
        logger.info("Added default 'Date' column with today's date")
        
    # Ensure Date is in datetime format
    if "Date" in processed_df.columns and not pd.api.types.is_datetime64_dtype(processed_df["Date"]):
        processed_df["Date"] = pd.to_datetime(processed_df["Date"], errors="coerce")
        # Fill NaT dates with today's date
        processed_df["Date"] = processed_df["Date"].fillna(pd.Timestamp("today"))
        logger.info("Converted 'Date' column to datetime format")
        
    # Ensure Total_Cost is numeric, correctly handling currency formats and credits (parentheses)
    if "Total_Cost" in processed_df.columns:
        try:
            # First convert to string for consistent handling
            total_cost_str = processed_df["Total_Cost"].astype(str)
            
            # Identify credit values (enclosed in parentheses)
            is_credit = total_cost_str.str.contains('\(.*\)')
            
            # Calculate percentage of credit values for logging
            credit_percentage = is_credit.mean() * 100
            if credit_percentage > 0:
                logger.info(f"Detected {credit_percentage:.1f}% of values as credits (in parentheses)")
            
            # Clean up currency formatting (remove $, commas, and parentheses)
            cleaned_str = total_cost_str.str.replace('$', '', regex=False) \
                                      .str.replace(',', '', regex=False) \
                                      .str.replace('\(', '', regex=True) \
                                      .str.replace('\)', '', regex=True) \
                                      .str.strip()
            
            # Convert to numeric, coercing any remaining non-numeric values to NaN
            numeric_values = pd.to_numeric(cleaned_str, errors='coerce')
            
            # Apply negative sign to credit values (those that were in parentheses)
            processed_df["Total_Cost"] = numeric_values * (-1 * is_credit + 1 * (~is_credit))
            
            # Fill NaN values with 0.0
            processed_df["Total_Cost"] = processed_df["Total_Cost"].fillna(0.0)
            
            # Log sample values and total
            logger.info(f"Total_Cost converted to numeric format. Sample values: {processed_df['Total_Cost'].head(3).tolist()}")
            
            # Calculate and log the total sum for verification
            raw_total = processed_df["Total_Cost"].sum()
            logger.info(f"Total Cost after reprocessing: ${raw_total:,.2f}")
            
            # Additional safeguard for very large/small total calculations - add a debug log
            if abs(raw_total) > 1000000000:  # More than 1 billion
                logger.warning(f"VERY LARGE TOTAL DETECTED: ${raw_total:,.2f}")
                logger.warning(f"Row count: {len(processed_df)}")
                logger.warning(f"Max value: ${processed_df['Total_Cost'].max():,.2f}")
                logger.warning(f"Min value: ${processed_df['Total_Cost'].min():,.2f}")
                logger.warning(f"Mean value: ${processed_df['Total_Cost'].mean():,.2f}")
                # Log the distribution of highest values for debugging
                largest_values = processed_df.nlargest(5, 'Total_Cost')['Total_Cost']
                logger.warning(f"Top 5 largest values: {largest_values.tolist()}")
            
        except Exception as e:
            logger.error(f"Error converting Total_Cost to numeric: {str(e)}")
            processed_df["Total_Cost"] = 0.0
        
    # Add standard PO Type column
    if "Type: Purchase Order" not in processed_df.columns:
        if report_type == "po_line_detail" and "Type" in processed_df.columns:
            # Map Type values to standardized format
            type_mapping = {
                "Catalog": "Catalog",
                "catalog": "Catalog",
                "CATALOG": "Catalog",
                "Free text": "Free Text",
                "free text": "Free Text",
                "FREE TEXT": "Free Text",
                "Punch out": "Free Text",  # Map "Punch out" to "Free Text" as requested
                "punch out": "Free Text",
                "PUNCH OUT": "Free Text",
                "Punchout": "Free Text",
                "punchout": "Free Text",
                "PUNCHOUT": "Free Text"
            }
            
            # Apply mapping if Type value is in the mapping, otherwise keep the original value
            processed_df["Type: Purchase Order"] = processed_df["Type"].apply(
                lambda x: type_mapping.get(x, x) if pd.notna(x) else "Catalog"
            )
            logger.info("Added 'Type: Purchase Order' from 'Type' with standardized values")
        else:
            # Default for Non-PO Invoice data
            processed_df["Type: Purchase Order"] = "Non-PO"
            logger.info("Added 'Type: Purchase Order' with default 'Non-PO' value")
            
    # Add minimal required columns for analysis if they don't exist
    if "Quantity" not in processed_df.columns:
        processed_df["Quantity"] = 1
        logger.info("Added default 'Quantity' column with value 1")
    else:
        # Ensure Quantity is numeric
        try:
            # Convert Quantity to string first to safely handle currency and commas
            processed_df["Quantity"] = processed_df["Quantity"].astype(str).str.replace(',', '').str.replace('$', '')
            # Convert to numeric, coercing any non-numeric values to NaN
            processed_df["Quantity"] = pd.to_numeric(processed_df["Quantity"], errors='coerce')
            # Fill NaN with 1 (default quantity)
            processed_df["Quantity"] = processed_df["Quantity"].fillna(1)
            logger.info("Converted Quantity column to numeric format")
        except Exception as e:
            logger.error(f"Error converting Quantity to numeric: {str(e)}")
            # Keep existing values but warn about the issue
            logger.warning("Keeping original Quantity values despite conversion error")
        
    if "Unit" not in processed_df.columns:
        # First check if 'Units' column exists (from Chemical Spend by Supplier)
        if "Units" in processed_df.columns:
            # Copy from Units to Unit, preserving any Non-PO markings
            processed_df["Unit"] = processed_df["Units"]
            logger.info("Copied 'Units' to 'Unit' column")
        else:
            # Use default unit value
            processed_df["Unit"] = "unit"
            logger.info("Added default 'Unit' column with value 'unit'")
        
    if "Unit_Price" not in processed_df.columns and "Total_Cost" in processed_df.columns:
        processed_df["Unit_Price"] = processed_df["Total_Cost"]
        logger.info("Added 'Unit_Price' based on 'Total_Cost'")
        
    # Helper function to consolidate all region formats to main regions
    def consolidate_to_main_region(region_value):
        """
        Consolidate any region or sub-region to its main region.
        Main regions are: Central, Mid-Atlantic, South, West
        
        Args:
            region_value: The region value to consolidate
            
        Returns:
            str: The main region name
        """
        if pd.isna(region_value):
            return "Unknown"
            
        region_str = str(region_value).strip()
        
        # Extract the main region from complex formats (like "Mid-Atlantic : Bristol")
        if ':' in region_str:
            # Take the part before the first colon (trimming whitespace)
            main_region = region_str.split(':', 1)[0].strip()
            return main_region
            
        # Consolidate regions by prefix
        if region_str.startswith("South"):
            return "South"
        elif region_str.startswith("Mid-Atlantic") or region_str.startswith("MidAtlantic"):
            return "Mid-Atlantic"
        elif region_str.startswith("Central"):
            return "Central"
        elif region_str.startswith("West"):
            return "West"
            
        # Return the original if it doesn't match any pattern
        return region_str
    
    # Process region information consistently
    if "Region" in processed_df.columns:
        # For Chemical Spend by Supplier, now also apply consolidation
        if report_type == "chemical_spend_by_supplier":
            processed_df["Region"] = processed_df["Region"].apply(consolidate_to_main_region)
            logger.info("Consolidated all Chemical Spend by Supplier regions to main regions")
        # For Non-PO Invoice data, Dimension4 Description has raw region code
        elif report_type == "non_po_invoice":
            try:
                if "Dimension4 Description" in df.columns:
                    # Extract main region from Dimension4 Description
                    processed_df["Region"] = processed_df["Dimension4 Description"].apply(consolidate_to_main_region)
                    logger.info("Consolidated all regions from Dimension4 Description to main regions")
                else:
                    # Apply consolidation to existing Region column
                    processed_df["Region"] = processed_df["Region"].apply(consolidate_to_main_region)
                    logger.info("Consolidated existing Region values to main regions")
            except Exception as e:
                logger.warning(f"Error consolidating regions: {str(e)}")
                # Fall back to basic consolidation
                processed_df["Region"] = processed_df["Region"].apply(consolidate_to_main_region)
        else:
            # For PO Line Detail
            processed_df["Region"] = processed_df["Region"].apply(consolidate_to_main_region)
            logger.info("Consolidated all PO Line Detail regions to main regions")
    elif report_type == "po_line_detail" and "Purchase Requisition: Our Reference" in processed_df.columns:
        processed_df["Region"] = processed_df["Purchase Requisition: Our Reference"]
        # Also consolidate this region to main regions
        processed_df["Region"] = processed_df["Region"].apply(consolidate_to_main_region)
        logger.info("Added and consolidated 'Region' based on 'Purchase Requisition: Our Reference'")
    else:
        processed_df["Region"] = "Unknown"
        logger.warning("No region information found, setting to 'Unknown'")
            
    # Clean region names to remove email addresses
    if "Region" in processed_df.columns:
        processed_df["Region"] = processed_df["Region"].apply(clean_region_names)
        logger.info("Cleaned Region names to remove email addresses")
        
        # Apply the main region consolidation again after cleaning email addresses
        # This ensures that all region formats are properly consolidated
        processed_df["Region"] = processed_df["Region"].apply(consolidate_to_main_region)
        logger.info("Final consolidation of all region names to main regions")
    
    # Log all columns to verify
    logger.info(f"Final column list after standardization: {processed_df.columns.tolist()}")
    
    return processed_df

def extract_standard_data(file, report_type=None):
    """
    Load data from file and standardize columns while preserving all original data.
    
    Args:
        file: File path or uploaded file object
        report_type: Optional report type override ('po_line_detail' or 'non_po_invoice')
        
    Returns:
        DataFrame: Standardized DataFrame with all original columns preserved
    """
    # Determine file type and read accordingly
    if hasattr(file, 'name'):
        # Handle uploaded file object
        file_name = file.name
        if file_name.endswith('.csv'):
            # Try different CSV separators and encodings
            separators = [',', ';', '\t', '|']
            encodings = ['utf-8', 'iso-8859-1', 'latin1']
            
            # Make a copy of the file content to retry with different parameters
            file_content = file.read()
            
            for separator in separators:
                for encoding in encodings:
                    try:
                        # Reset to the beginning of the content for each attempt
                        file_copy = io.BytesIO(file_content)
                        
                        # Try to read with the current separator and encoding
                        df = pd.read_csv(file_copy, sep=separator, encoding=encoding)
                        
                        # If successful, log and break out
                        logger.info(f"Successfully read CSV with separator '{separator}' and encoding '{encoding}'")
                        
                        # If we get a DataFrame with only one column, it's likely the wrong separator
                        if len(df.columns) <= 1:
                            logger.warning(f"CSV read with separator '{separator}' resulted in only {len(df.columns)} columns, likely incorrect")
                            continue
                            
                        break
                    except Exception as e:
                        logger.warning(f"Failed to read CSV with separator '{separator}' and encoding '{encoding}': {str(e)}")
                        continue
                
                # If we successfully loaded a DataFrame with more than one column, break out of both loops
                if 'df' in locals() and len(df.columns) > 1:
                    break
            
            # If we couldn't read the file as CSV with any separator, raise an error
            if 'df' not in locals():
                raise ValueError("Could not read the CSV file with any separator or encoding. Please check the file format.")
                
        elif file_name.endswith(('.xlsx', '.xls')):
            # Try different Excel engines to handle various Excel formats
            try:
                # First try with openpyxl (newer Excel formats)
                df = pd.read_excel(file, engine='openpyxl')
                logger.info("Successfully read Excel file with openpyxl engine")
            except Exception as excel_err:
                try:
                    # Reset file pointer
                    file.seek(0)
                    # Try with xlrd (older Excel formats)
                    df = pd.read_excel(file, engine='xlrd')
                    logger.info("Successfully read Excel file with xlrd engine")
                except Exception as xlrd_err:
                    # Reset file pointer
                    file.seek(0)
                    # Try with odf for OpenDocument formats
                    try:
                        df = pd.read_excel(file, engine='odf')
                        logger.info("Successfully read Excel file with odf engine")
                    except Exception as odf_err:
                        # Try a last resort approach - read as CSV
                        file.seek(0)
                        try:
                            # Try reading as CSV (some Excel files exported as CSV still have .xlsx extension)
                            df = pd.read_csv(file, sep=None, engine='python')  # python engine tries to detect separator
                            logger.info("Successfully read Excel-named file as CSV with automatic separator detection")
                        except Exception as csv_err:
                            # Log all errors for debugging
                            err_msg = (f"Failed to read Excel file with multiple engines: "
                                      f"openpyxl: {str(excel_err)} | "
                                      f"xlrd: {str(xlrd_err)} | "
                                      f"odf: {str(odf_err)} | "
                                      f"csv: {str(csv_err)}")
                            logger.error(err_msg)
                            raise ValueError(f"Could not read the Excel file with any available engine. Please check the file format or convert to CSV and try again. Error details recorded in log.")
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
    else:
        # Handle file path string
        if isinstance(file, str): 
            if file.endswith('.csv'):
                # Try different CSV separators and encodings
                separators = [',', ';', '\t', '|']
                encodings = ['utf-8', 'iso-8859-1', 'latin1']
                
                for separator in separators:
                    for encoding in encodings:
                        try:
                            # Try to read with the current separator and encoding
                            df = pd.read_csv(file, sep=separator, encoding=encoding)
                            
                            # If successful, log and break out
                            logger.info(f"Successfully read CSV with separator '{separator}' and encoding '{encoding}'")
                            
                            # If we get a DataFrame with only one column, it's likely the wrong separator
                            if len(df.columns) <= 1:
                                logger.warning(f"CSV read with separator '{separator}' resulted in only {len(df.columns)} columns, likely incorrect")
                                continue
                                
                            break
                        except Exception as e:
                            logger.warning(f"Failed to read CSV with separator '{separator}' and encoding '{encoding}': {str(e)}")
                            continue
                    
                    # If we successfully loaded a DataFrame with more than one column, break out of both loops
                    if 'df' in locals() and len(df.columns) > 1:
                        break
                
                # If we couldn't read the file as CSV with any separator, try using the python engine
                if 'df' not in locals():
                    try:
                        df = pd.read_csv(file, sep=None, engine='python')  # python engine tries to detect separator
                        logger.info("Successfully read CSV with python engine auto-detection")
                    except Exception as e:
                        raise ValueError(f"Could not read the CSV file with any separator or encoding. Please check the file format. Error: {str(e)}")
                
            elif file.endswith(('.xlsx', '.xls')):
                # Try different Excel engines to handle various Excel formats
                try:
                    # First try with openpyxl (newer Excel formats)
                    df = pd.read_excel(file, engine='openpyxl')
                    logger.info("Successfully read Excel file with openpyxl engine")
                except Exception as excel_err:
                    try:
                        # Try with xlrd (older Excel formats)
                        df = pd.read_excel(file, engine='xlrd')
                        logger.info("Successfully read Excel file with xlrd engine")
                    except Exception as xlrd_err:
                        # Try with odf for OpenDocument formats
                        try:
                            df = pd.read_excel(file, engine='odf')
                            logger.info("Successfully read Excel file with odf engine")
                        except Exception as odf_err:
                            # Try a last resort approach - read as CSV
                            try:
                                # Try reading as CSV (some Excel files exported as CSV still have .xlsx extension)
                                df = pd.read_csv(file, sep=None, engine='python')  # python engine tries to detect separator
                                logger.info("Successfully read Excel-named file as CSV with automatic separator detection")
                            except Exception as csv_err:
                                # Log all errors for debugging
                                err_msg = (f"Failed to read Excel file with multiple engines: "
                                          f"openpyxl: {str(excel_err)} | "
                                          f"xlrd: {str(xlrd_err)} | "
                                          f"odf: {str(odf_err)} | "
                                          f"csv: {str(csv_err)}")
                                logger.error(err_msg)
                                raise ValueError(f"Could not read the Excel file with any available engine. Please check the file format or convert to CSV and try again. Error details recorded in log.")
            else:
                raise ValueError("Unsupported file format. Please provide a CSV or Excel file path.")
        else:
            raise ValueError("File must be a string path or an uploaded file object.")
    
    # Print the exact columns in the original file
    logger.info(f"Original file columns: {list(df.columns)}")
    
    # Print first row as a dict to see exact values
    if not df.empty:
        logger.info("First row of data:")
        logger.info(df.iloc[0].to_dict())
    
    # Remove blank columns that might cause issues
    # First identify columns that are entirely empty
    blank_cols = [col for col in df.columns if df[col].isna().all()]
    if blank_cols:
        logger.info(f"Removing {len(blank_cols)} blank columns: {blank_cols}")
        df = df.drop(columns=blank_cols)
    
    # Preserve original column names exactly - just trim whitespace
    df.columns = [col.strip() for col in df.columns]

    # Auto-detect report type if not provided
    if report_type is None:
        # Note: Supplier unit cost detection has been removed as requested
        filename = file.name if hasattr(file, 'name') else ""
        
        # Check if it's a Chemical Spend by Supplier report
        from .report_processor_manager import is_chemical_spend_by_supplier_report
        
        if is_chemical_spend_by_supplier_report(df, filename):
            logger.info("Auto-detected Chemical Spend by Supplier format")
            # Use the specialized processor
            from .report_processor_manager import process_report
            processed_df, detected_report_type = process_report(df, report_type="chemical_spend", filename=filename)
            
            # Store the processed data in session state if needed
            try:
                import streamlit as st
                if 'chemical_spend_data' not in st.session_state:
                    st.session_state.chemical_spend_data = processed_df
            except:
                logger.info("Not in Streamlit context, skipping session state update")
            
            return processed_df, "chemical_spend"
            
        # Check for expected columns from each report type
        po_line_format_columns = [
            "Purchase Order: Confirmation Date", "Line Number", "Purchase Requisition: Number",
            "Order Identifier", "Order_ID", "Purchase Order: Supplier", "Item Description",
            "Category", "Confirmed Unit Price", "Connected", "Connected Quantity",  # Now checking for just "Connected" (column J)
            "Purchase Requisition: Buyer", "Purchase Requisition: Our Reference",  # Column M - critical for region data
            "Purchase Order: Processing Status", "Purchase Order: Received By", "Type"  # Column P - critical for catalog/free text identification
        ]

        non_po_format_columns = [
            "Invoice: Type", "Invoice: Created Date", "Supplier: Name", "Invoice: Number",
            "Coding Line Number", "Dimension1 Value", "Dimension1 Description", 
            "Dimension2 Value", "Net Amount", "Dimension3 Description", 
            "Dimension4 Description", "Dimension5 Description", "Dimension5 Value"
        ]

        # Count how many columns match each report type
        po_line_matches = [col for col in po_line_format_columns 
                        if col in df.columns or col.strip().lower() in [c.strip().lower() for c in df.columns]]

        non_po_matches = [col for col in non_po_format_columns 
                        if col in df.columns or col.strip().lower() in [c.strip().lower() for c in df.columns]]

        logger.info(f"Matched PO Line Detail columns: {len(po_line_matches)}, matches: {po_line_matches}")
        logger.info(f"Matched Non-PO Invoice columns: {len(non_po_matches)}, matches: {non_po_matches}")

        # Determine report type based on which has more matching columns
        if len(non_po_matches) > len(po_line_matches):
            logger.info("Auto-detected Non-PO Invoice Chemical GL format")
            report_type = "non_po_invoice"
        else:
            logger.info("Auto-detected PO Line Detail format")
            report_type = "po_line_detail"
    
    # Standardize columns based on detected or provided report type
    standardized_df = standardize_columns(df, report_type)
    
    # Print the final column list to verify all original columns are preserved
    logger.info(f"Final returned columns: {standardized_df.columns.tolist()}")

    return standardized_df, report_type

def validate_data(df, report_type=None):
    """
    Validates the processed data to ensure it meets analysis requirements.

    Args:
        df: DataFrame to validate
        report_type: Type of report, used to determine validation rules

    Returns:
        tuple: (is_valid, message) - Boolean indicating validity and message
    """
    if df is None or len(df) == 0:
        return False, "Data is empty or missing"
    
    # Note: Supplier unit cost validation has been removed as requested
    
    # Standard validation for other report types
    # Check for required columns
    required_columns = ['Date', 'Total_Cost']
    
    for col in required_columns:
        if col not in df.columns:
            return False, f"Required column '{col}' is missing"
    
    # Check if date column is actually dates
    try:
        if not pd.api.types.is_datetime64_dtype(df['Date']):
            # Try to convert
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            if df['Date'].isna().all():
                return False, "Date column contains no valid dates"
    except Exception as e:
        return False, f"Error processing dates: {str(e)}"
    
    # Check for date range issues - warn but don't reject
    current_year = datetime.now().year
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    
    if min_date and max_date:
        if min_date.year < current_year - 10:
            logger.warning(f"Data contains very old dates: {min_date}")
        if max_date.year > current_year + 1:
            logger.warning(f"Data contains future dates: {max_date}")
    
    # Check for missing values in cost column
    if df['Total_Cost'].isna().all():
        return False, "Total_Cost column contains all missing values"
    
    # Identify numeric columns that might need checking
    numeric_columns = ['Total_Cost']
    if 'Quantity' in df.columns:
        numeric_columns.append('Quantity')
    if 'Unit_Price' in df.columns:
        numeric_columns.append('Unit_Price')
    
    # Check numeric columns for non-numeric values
    for col in numeric_columns:
        if col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                # Try to convert to numeric after cleaning currency and thousand separators
                cleaned_values = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                df[col] = pd.to_numeric(cleaned_values, errors='coerce')
                
                # Handle missing values differently based on column
                na_count = df[col].isna().sum()
                if col == 'Total_Cost' and na_count > len(df) * 0.5:  # More than 50% NaN for Total_Cost
                    return False, f"Column '{col}' has too many non-numeric values"
                elif col == 'Quantity' and na_count > len(df) * 0.5:  # For Quantity, replace with 1 instead of failing
                    logger.warning(f"Column '{col}' has many non-numeric values, using default value 1")
                    df[col] = df[col].fillna(1)
                elif col == 'Unit_Price' and na_count > len(df) * 0.5:  # For Unit_Price, try to compute from Total_Cost
                    logger.warning(f"Column '{col}' has many non-numeric values, will try to calculate from Total_Cost")
                    df[col] = df[col].fillna(df['Total_Cost'] if 'Total_Cost' in df.columns else 0)
    
    # Check for negative values - but just warn, don't reject
    for col in numeric_columns:
        if col in df.columns and (df[col] < 0).any():
            logger.warning(f"Warning: {col} contains negative values")

    # Don't reject for outliers, just log warning
    try:
        mean_cost = df['Total_Cost'].mean()
        std_cost = df['Total_Cost'].std() if len(df) > 1 else mean_cost  # Avoid division by zero
        if std_cost > 0:
            outlier_threshold = mean_cost + (3 * std_cost)
            outliers = df[df['Total_Cost'] > outlier_threshold]

            if len(outliers) > 0:
                logger.warning(f"Warning: {len(outliers)} cost outliers detected")
    except Exception as e:
        logger.error(f"Error checking for outliers: {str(e)}")

    # All validations passed
    logger.info("Validation passed")
    return True, "Data is valid."