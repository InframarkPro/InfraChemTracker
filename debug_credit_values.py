"""
Debug script to analyze credit values in parentheses in Chemical Spend by Supplier report data.
"""

import pandas as pd
import io
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_credit_values(file_path):
    """Analyze credit values (in parentheses) in the Total column of a CSV file."""
    try:
        # Try different CSV separators and encodings
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
        
        if 'df' not in locals():
            logger.error("Could not read the file with any separator or encoding.")
            return
        
        logger.info(f"DataFrame loaded with {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Columns: {df.columns.tolist()}")
        
        # Check for the Total column
        total_col = None
        for col in df.columns:
            if col.strip() == 'Total':
                total_col = col
                break
        
        if total_col is None:
            logger.error("Could not find Total column in the DataFrame")
            return
        
        # Convert Total column to string
        total_str = df[total_col].astype(str)
        
        # Find values in parentheses using regex
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
            
            # Calculate sum of all values and all credits
            # First clean up currency formatting (remove $ and commas)
            import re
            
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
        
    except Exception as e:
        logger.error(f"Error analyzing credit values: {str(e)}")
        return

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "attached_assets/ChemicalSpendbySupplier-YongdaLi639.csv"
    
    logger.info(f"Analyzing file: {file_path}")
    analyze_credit_values(file_path)