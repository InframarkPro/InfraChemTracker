"""
Script to debug the data in the saved Chemical Spend by Supplier reports.
"""

import os
import sys
import pandas as pd
import sqlite3
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_saved_reports():
    """Analyze the data in saved reports."""
    db_path = "saved_data/reports_database.db"
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at {db_path}")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        logger.info(f"Tables in database: {tables}")
        
        # Get the reports
        cursor.execute("SELECT id, name, report_type FROM reports;")
        reports = cursor.fetchall()
        logger.info(f"Reports in database: {reports}")
        
        # Analyze each report
        for report_id, name, report_type in reports:
            logger.info(f"\nAnalyzing report: {name} (ID: {report_id}, Type: {report_type})")
            
            # Get the CSV file path based on report name
            file_name = name.replace(" ", "").replace("-", "_")
            file_path = f"saved_data/{file_name}.csv"
            
            if not os.path.exists(file_path):
                # Try alternative naming pattern
                file_path = f"saved_data/{name}_{report_id}.csv"
                
                if not os.path.exists(file_path):
                    # Try looking up all CSV files to find a match
                    csv_files = [f for f in os.listdir("saved_data") if f.endswith(".csv")]
                    logger.info(f"Available CSV files: {csv_files}")
                    
                    # Try finding files with the report ID in the name
                    matching_files = [f for f in csv_files if str(report_id) in f]
                    if matching_files:
                        file_path = os.path.join("saved_data", matching_files[0])
                        logger.info(f"Found matching file by ID: {file_path}")
                    elif report_type == "Chemical Spend by Supplier":
                        # Look specifically for Chemical Spend files
                        matching_files = [f for f in csv_files if "ChemicalSpend" in f or "Chemical_Spend" in f]
                        if matching_files:
                            file_path = os.path.join("saved_data", matching_files[0])
                            logger.info(f"Found Chemical Spend file: {file_path}")
                        else:
                            # Last resort: look for any chemical-related files but not PO Line Detail
                            matching_files = [f for f in csv_files if "Chemical" in f and "PO_Line_Detail" not in f]
                            if matching_files:
                                file_path = os.path.join("saved_data", matching_files[0])
                                logger.info(f"Found matching Chemical file: {file_path}")
                    elif report_type == "PO Line Detail":
                        # Look specifically for PO Line Detail files
                        matching_files = [f for f in csv_files if "PO_Line_Detail" in f]
                        if matching_files:
                            file_path = os.path.join("saved_data", matching_files[0])
                            logger.info(f"Found PO Line Detail file: {file_path}")
                    else:
                        # Look for files with partial name match
                        name_parts = name.split("_")
                        for part in name_parts:
                            if len(part) > 3:  # Only use parts that are meaningful (more than 3 chars)
                                matching_files = [f for f in csv_files if part.lower() in f.lower()]
                                if matching_files:
                                    file_path = os.path.join("saved_data", matching_files[0])
                                    logger.info(f"Found matching file by partial name: {file_path}")
                                    break
                
            if not os.path.exists(file_path):
                logger.warning(f"File not found for report {name} (ID: {report_id})")
                # List all CSV files in the saved_data directory
                csv_files = [f for f in os.listdir("saved_data") if f.endswith(".csv")]
                logger.info(f"Available CSV files: {csv_files}")
                continue
            
            # Determine file type and read accordingly
            if file_path.endswith('.csv'):
                # Try different CSV separators and encodings for reliability
                separators = [',', ';', '\t', '|']
                encodings = ['utf-8', 'iso-8859-1', 'latin1']
                
                for separator in separators:
                    for encoding in encodings:
                        try:
                            # Try to read with the current separator and encoding
                            df = pd.read_csv(file_path, sep=separator, encoding=encoding)
                            
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
            elif file_path.endswith(('.xlsx', '.xls')):
                try:
                    df = pd.read_excel(file_path)
                except Exception as e:
                    logger.error(f"Failed to read Excel file: {str(e)}")
                    continue
            else:
                logger.error(f"Unsupported file format: {file_path}")
                continue
            
            if 'df' not in locals():
                logger.error(f"Could not read the file: {file_path}")
                continue
            
            # Basic DataFrame analysis
            logger.info(f"DataFrame shape: {df.shape}")
            logger.info(f"Columns: {df.columns.tolist()}")
            
            # Check for 'Total' column
            total_col = None
            for col in df.columns:
                if col.strip() == 'Total':
                    total_col = col
                    break
            
            if total_col is not None:
                # Convert to string for consistent handling
                total_str = df[total_col].astype(str)
                
                # Check for values in parentheses
                import re
                pattern = r'\(.*\)'
                has_parentheses = total_str.str.contains(pattern, regex=True)
                
                # Count and log values with parentheses
                credit_count = has_parentheses.sum()
                total_count = len(total_str)
                credit_percentage = (credit_count / total_count) * 100 if total_count > 0 else 0
                
                logger.info(f"Total rows: {total_count}")
                logger.info(f"Rows with credit values (in parentheses): {credit_count} ({credit_percentage:.2f}%)")
                
                if credit_count > 0:
                    logger.info("Sample credit values:")
                    credit_values = df.loc[has_parentheses, total_col].head(10).tolist()
                    for i, val in enumerate(credit_values):
                        logger.info(f"  {i+1}. {val}")
                    
                    # Calculate sum with and without credits
                    def clean_currency(val):
                        if not isinstance(val, str):
                            return float(val)
                        
                        val_str = str(val).strip()
                        # Remove $ and commas
                        val_str = val_str.replace('$', '').replace(',', '')
                        
                        # Check if it's a credit value (in parentheses)
                        if '(' in val_str and ')' in val_str:
                            # Remove parentheses and make negative
                            val_str = val_str.replace('(', '').replace(')', '')
                            return -float(val_str)
                        else:
                            return float(val_str)
                    
                    try:
                        # Apply clean_currency to all values and sum
                        total_sum = sum(df[total_col].apply(lambda x: clean_currency(x) if pd.notna(x) else 0))
                        credit_sum = sum(df.loc[has_parentheses, total_col].apply(lambda x: clean_currency(x) if pd.notna(x) else 0))
                        
                        logger.info(f"Sum of all values: ${total_sum:,.2f}")
                        logger.info(f"Sum of credit values: ${credit_sum:,.2f}")
                        logger.info(f"Sum without credits: ${total_sum - credit_sum:,.2f}")
                    except Exception as e:
                        logger.error(f"Error calculating sums: {str(e)}")
            
            # Check for 'Total_Cost' column (which should be the standardized column)
            if "Total_Cost" in df.columns:
                try:
                    total_cost_sum = df["Total_Cost"].sum()
                    logger.info(f"Sum of Total_Cost column: ${total_cost_sum:,.2f}")
                except Exception as e:
                    logger.error(f"Error calculating Total_Cost sum: {str(e)}")
            
            # Get metadata if available
            try:
                cursor.execute("SELECT metadata FROM reports WHERE id = ?;", (report_id,))
                metadata_str = cursor.fetchone()[0]
                metadata = json.loads(metadata_str)
                logger.info(f"Metadata: {metadata}")
            except Exception as e:
                logger.error(f"Error fetching metadata: {str(e)}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error analyzing reports: {str(e)}")

if __name__ == "__main__":
    analyze_saved_reports()