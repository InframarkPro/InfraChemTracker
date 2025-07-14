"""
NetSuite "Chemical Spend by Supplier" Report Processor

This module provides specialized processing for the Chemical Spend by Supplier reports
from NetSuite. It handles the unique column structure and data format of these reports,
extracting and standardizing the data for analysis in the app.
"""

import re
import pandas as pd
from datetime import datetime

def process_chemical_spend_by_supplier_report(df):
    """
    Process a Chemical Spend by Supplier report from NetSuite.
    
    Args:
        df: DataFrame containing the raw report data
        
    Returns:
        DataFrame: Standardized data with unified column names and data types
    """
    print("Processing Chemical Spend by Supplier report")
    print(f"Original dataframe shape: {df.shape}")
    
    # Make a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Remove blank columns that might cause issues
    blank_cols = [col for col in processed_df.columns if processed_df[col].isna().all()]
    if blank_cols:
        print(f"Removing {len(blank_cols)} blank columns from Chemical Spend report: {blank_cols}")
        processed_df = processed_df.drop(columns=blank_cols)
    
    # Remove 'Date Created' column if it exists as requested by client
    if 'Date Created' in processed_df.columns:
        print("Removing 'Date Created' column as requested")
        processed_df = processed_df.drop(columns=['Date Created'])
    
    # Map the NetSuite column names to our standardized column names
    column_map = {
        'Vendor ID': 'Vendor_ID',
        'Vendor Name': 'Supplier',
        'Supplier Category': 'Supplier_Category',
        'Line of Service': 'Line_of_Service',
        # Keep Project Region as-is - don't rename to Region
        'Department': 'Department',
        'Department ID': 'Department_ID',
        'Bill #': 'Order_ID',
        'Bill Date': 'Date',
        'Description': 'Description',
        'Quantity': 'Quantity',
        'Units': 'Units',
        'Rate': 'Unit_Price',
        'Amount': 'Total_Cost',
        'Purchase Order Type': 'PO_Type'
    }
    
    # Rename columns based on the mapping
    # Only rename columns that exist in the dataframe
    rename_cols = {col: column_map[col] for col in column_map if col in processed_df.columns}
    processed_df = processed_df.rename(columns=rename_cols)
    
    # Ensure required columns exist
    required_columns = ['Supplier', 'Description', 'Date', 'Total_Cost', 'Order_ID']
    
    # Find alternative columns if standard ones don't exist
    if 'Supplier' not in processed_df.columns:
        # Look for vendor or supplier columns
        vendor_cols = [col for col in processed_df.columns if 'vendor' in col.lower() or 'supplier' in col.lower()]
        if vendor_cols:
            processed_df = processed_df.rename(columns={vendor_cols[0]: 'Supplier'})
        else:
            processed_df['Supplier'] = 'Unknown Supplier'
    
    if 'Description' not in processed_df.columns:
        # Look for item or description columns
        desc_cols = [col for col in processed_df.columns if 'description' in col.lower() or 'item' in col.lower()]
        if desc_cols:
            processed_df = processed_df.rename(columns={desc_cols[0]: 'Description'})
        else:
            processed_df['Description'] = 'Unknown Item'
    
    if 'Date' not in processed_df.columns:
        # Look for date columns
        date_cols = [col for col in processed_df.columns if 'date' in col.lower()]
        if date_cols:
            processed_df = processed_df.rename(columns={date_cols[0]: 'Date'})
        else:
            processed_df['Date'] = datetime.now().strftime('%Y-%m-%d')
    
    if 'Total_Cost' not in processed_df.columns:
        # Look for amount or cost columns
        cost_cols = [col for col in processed_df.columns if 'amount' in col.lower() or 'cost' in col.lower()]
        if cost_cols:
            processed_df = processed_df.rename(columns={cost_cols[0]: 'Total_Cost'})
        else:
            processed_df['Total_Cost'] = 0.0
    
    if 'Order_ID' not in processed_df.columns:
        # Look for bill, invoice, or order number columns
        order_cols = [col for col in processed_df.columns if 'bill' in col.lower() or 'invoice' in col.lower() or 'order' in col.lower()]
        if order_cols:
            processed_df = processed_df.rename(columns={order_cols[0]: 'Order_ID'})
        else:
            processed_df['Order_ID'] = 'Unknown'
    
    # Process Purchase Order Type if it exists
    if 'PO_Type' not in processed_df.columns:
        # Look for type columns
        type_cols = [col for col in processed_df.columns if 'type' in col.lower()]
        if type_cols:
            processed_df = processed_df.rename(columns={type_cols[0]: 'PO_Type'})
        else:
            # Try to infer PO type from description
            processed_df['PO_Type'] = processed_df['Description'].apply(determine_po_type)
    
    # Add standardized Type: Purchase Order column for consistency with other report types
    if 'Type: Purchase Order' not in processed_df.columns:
        if 'PO_Type' in processed_df.columns:
            # Map PO_Type values to standardized format
            type_mapping = {
                "Catalog": "Catalog",
                "CATALOG": "Catalog",
                "catalog": "Catalog",
                "Free Text": "Free Text",
                "FREE TEXT": "Free Text", 
                "free text": "Free Text"
            }
            # Apply mapping if PO_Type value is in the mapping, otherwise keep the original value
            processed_df['Type: Purchase Order'] = processed_df['PO_Type'].apply(
                lambda x: type_mapping.get(x, x) if pd.notna(x) else "Free Text"
            )
        else:
            # Default to Free Text if no PO_Type column
            processed_df['Type: Purchase Order'] = processed_df['Description'].apply(
                lambda x: "Catalog" if determine_po_type(x) == "Catalog" else "Free Text"
            )
    
    # Extract chemical name from the Description field
    processed_df['Chemical'] = processed_df['Description'].apply(extract_chemical_name)
    
    # Use exact regions from the report without standardization
    if 'Region' not in processed_df.columns:
        processed_df['Region'] = 'Unknown'
    
    # Convert date columns to datetime
    if 'Date' in processed_df.columns:
        try:
            processed_df['Date'] = pd.to_datetime(processed_df['Date'], errors='coerce')
        except:
            # If conversion fails, use current date
            processed_df['Date'] = datetime.now()
    
    # Ensure Total_Cost is numeric by properly cleaning currency values
    # Check if we have Total column before we have Total_Cost column
    if 'Total' in processed_df.columns and 'Total_Cost' not in processed_df.columns:
        # If we have a Total column but no Total_Cost, use the Total column as Total_Cost
        print("Found 'Total' column but no 'Total_Cost'. Copying Total to Total_Cost.")
        processed_df['Total_Cost'] = processed_df['Total']
    
    if 'Total_Cost' in processed_df.columns:
        try:
            # Log original Total_Cost column information
            print(f"Total_Cost column data types: {processed_df['Total_Cost'].apply(type).value_counts().to_dict()}")
            print(f"Sample Total_Cost values (original): {processed_df['Total_Cost'].head().tolist()}")
            
            # First convert to string for consistent handling
            total_cost_str = processed_df['Total_Cost'].astype(str)
            
            # Identify credit values (enclosed in parentheses)
            is_credit = total_cost_str.str.contains('\(.*\)')
            
            # Log credit values for debugging
            if is_credit.any():
                credit_count = is_credit.sum()
                credit_values = processed_df.loc[is_credit, 'Total_Cost'].head(5).tolist()
                print(f"Found {credit_count} credit values (in parentheses). Examples: {credit_values}")
            
            # Clean up currency formatting (remove $, commas, and parentheses)
            cleaned_str = total_cost_str.str.replace('$', '', regex=False) \
                                      .str.replace(',', '', regex=False) \
                                      .str.replace('\(', '', regex=True) \
                                      .str.replace('\)', '', regex=True) \
                                      .str.strip()
            
            # Convert to numeric, coercing any remaining non-numeric values to NaN
            numeric_values = pd.to_numeric(cleaned_str, errors='coerce')
            
            # Check for NaN values after conversion
            nan_count = numeric_values.isna().sum()
            if nan_count > 0:
                print(f"Warning: {nan_count} values could not be converted to numeric. Example problematic values:")
                problem_indices = numeric_values.isna()
                problem_values = total_cost_str[problem_indices].head(5).tolist()
                print(f"Problematic values: {problem_values}")
            
            # Apply negative sign to credit values (those that were in parentheses)
            processed_df['Total_Cost'] = numeric_values * (-1 * is_credit + 1 * (~is_credit))
            
            # Fill NaN values with 0.0
            processed_df['Total_Cost'] = processed_df['Total_Cost'].fillna(0.0)
            
            # Log the conversion results
            print(f"Converted Total_Cost to numeric. Sample values: {processed_df['Total_Cost'].head(3).tolist()}")
            
            # Calculate and log the total for verification
            total_cost = processed_df['Total_Cost'].sum()
            print(f"Total Cost after accounting for credits: ${total_cost:,.2f}")
            
            # Check for zero values
            zero_count = (processed_df['Total_Cost'] == 0).sum()
            if zero_count > 0:
                print(f"Warning: {zero_count} Total_Cost values are zero. This might affect total spend calculations.")
                
            # If all values are still zero, we may have a problem with the original data
            if total_cost == 0 and 'Total' in processed_df.columns:
                print("All Total_Cost values are zero. Trying alternative approach with 'Total' column...")
                
                # Check if the original 'Total' column has decimal numbers or currency formatted values
                total_str = processed_df['Total'].astype(str)
                
                # Clean up currency formatting 
                cleaned_total = total_str.str.replace('$', '', regex=False) \
                                        .str.replace(',', '', regex=False) \
                                        .str.replace('\(', '-', regex=True) \
                                        .str.replace('\)', '', regex=True) \
                                        .str.strip()
                
                # Convert to numeric
                processed_df['Total_Numeric'] = pd.to_numeric(cleaned_total, errors='coerce').fillna(0.0)
                
                # Use this as Total_Cost if it has non-zero values
                if processed_df['Total_Numeric'].sum() > 0:
                    print(f"Using 'Total_Numeric' column instead. Sum: ${processed_df['Total_Numeric'].sum():,.2f}")
                    processed_df['Total_Cost'] = processed_df['Total_Numeric']
            
        except Exception as e:
            print(f"Error converting Total_Cost to numeric: {str(e)}")
            processed_df['Total_Cost'] = 0.0
    
    # Add Chemical_Category column
    if 'Chemical' in processed_df.columns:
        processed_df['Chemical_Category'] = processed_df['Chemical'].apply(categorize_chemical)
    
    # Handle Facility column for compatibility with standard columns
    if 'Facility' not in processed_df.columns:
        if 'Department' in processed_df.columns:
            processed_df['Facility'] = processed_df['Department']
        elif 'Department Name' in processed_df.columns:
            processed_df['Facility'] = processed_df['Department Name']
        else:
            # Create a basic facility name using Department_ID and Region if available
            if 'Department_ID' in processed_df.columns and 'Region' in processed_df.columns:
                processed_df['Facility'] = processed_df.apply(
                    lambda row: f"{row['Region']} - {row['Department_ID']}" 
                    if pd.notna(row['Department_ID']) and pd.notna(row['Region'])
                    else "Unknown Facility", axis=1
                )
            else:
                processed_df['Facility'] = "Unknown Facility"
    
    # Fill missing values
    processed_df = processed_df.fillna({
        'Supplier': 'Unknown Supplier',
        'Description': 'Unknown Item',
        'Chemical': 'Unknown Chemical',
        'Region': 'Unknown',
        'Department': 'Unknown',
        'PO_Type': 'Unknown',
        'Chemical_Category': 'Other',
        'Facility': 'Unknown Facility',
        'Type: Purchase Order': 'Free Text'
    })
    
    # Handle blank Units values - identify them as Non-PO
    if 'Units' in processed_df.columns:
        # Replace blank/empty/NA values in Units with "Non-PO"
        processed_df['Units'] = processed_df['Units'].fillna('Non-PO')
        # Also replace empty strings with "Non-PO"
        processed_df.loc[processed_df['Units'].astype(str).str.strip() == '', 'Units'] = 'Non-PO'
        print(f"Marked {(processed_df['Units'] == 'Non-PO').sum()} blank Units values as 'Non-PO'")
    
    # Make sure numeric columns are properly typed
    numeric_columns = ['Quantity', 'Unit_Price', 'Total_Cost']
    for col in numeric_columns:
        if col in processed_df.columns:
            processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce').fillna(0)
    
    # Final verification of data before returning
    print(f"Final dataframe shape: {processed_df.shape}")
    print(f"Final Total_Cost sum: ${processed_df['Total_Cost'].sum():,.2f}")
    print(f"Zero values in Total_Cost: {(processed_df['Total_Cost'] == 0).sum()}")
    print(f"NaN values in Total_Cost: {processed_df['Total_Cost'].isna().sum()}")
    
    # Check if there's a mismatch in data which could explain dashboard issues
    row_count = len(processed_df)
    non_zero_total_cost = (processed_df['Total_Cost'] > 0).sum()
    print(f"Percentage of rows with non-zero Total_Cost: {(non_zero_total_cost/row_count)*100:.2f}%")
    
    # Verify summary metrics match total dataset
    top_suppliers = processed_df.groupby('Supplier')['Total_Cost'].sum().sort_values(ascending=False).head(3)
    print(f"Top 3 suppliers by Total_Cost:")
    for supplier, cost in top_suppliers.items():
        print(f"  - {supplier}: ${cost:,.2f}")
    
    return processed_df

def determine_po_type(description):
    """
    Attempt to determine if an order is Catalog or Free Text based on the description.
    
    Args:
        description: The item description text
        
    Returns:
        str: "Catalog" or "Free Text"
    """
    description = str(description).lower()
    
    # Catalog orders often have standardized formatting and might include catalog numbers
    # Free text orders often have inconsistent capitalization, spelling variations, etc.
    if any(pattern in description for pattern in ['catalog', 'cat#', 'item#', 'sku']):
        return 'Catalog'
    elif any(pattern in description for pattern in ['chemical -', 'chemical-']):
        # Chemical followed by standardized chemical name suggests catalog
        return 'Catalog'
    else:
        # Default to Free Text if no catalog indicators
        return 'Free Text'

def extract_chemical_name(description):
    """
    Extract the chemical name from the description field.
    
    Args:
        description: The item description text
        
    Returns:
        str: Extracted chemical name
    """
    description = str(description)
    
    # Try to extract chemical name using common patterns
    
    # Pattern 1: "Chemical - Name - Concentration"
    chemical_pattern = re.compile(r'chemical\s*-\s*(.*?)($|\s*-\s*)', re.IGNORECASE)
    match = chemical_pattern.search(description)
    if match:
        return match.group(1).strip()
    
    # Pattern 2: Look for common chemical names directly
    common_chemicals = [
        "Sodium Hypochlorite", "Bleach", "Chlorine", "Caustic", "Sodium Hydroxide",
        "Lime", "Calcium Hydroxide", "Soda Ash", "Sodium Carbonate", 
        "Ferric Chloride", "Alum", "Aluminum Sulfate", "Polymer", "Fluoride",
        "Activated Carbon", "PAC", "GAC", "Potassium Permanganate", "KMnO4",
        "Peracetic Acid", "Hydrogen Peroxide", "Acids", "Bases", "Muriatic Acid",
        "Sulfuric Acid", "Ammonia", "Sodium Bisulfite", "Citric Acid"
    ]
    
    for chemical in common_chemicals:
        if chemical.lower() in description.lower():
            return chemical
    
    # Pattern 3: If it's a short description, use it as is
    if len(description.split()) <= 3 and len(description) < 30:
        return description
    
    # Default case - use first few words
    return " ".join(description.split()[:3]) + "..."

def standardize_region(region):
    """
    Standardize region names for consistency.
    
    Args:
        region: The original region name
        
    Returns:
        str: Standardized region name
    """
    region = str(region).strip()
    
    # Map common variations of region names
    region_map = {
        'SE': 'Southeast',
        'NE': 'Northeast',
        'SW': 'Southwest',
        'NW': 'Northwest',
        'S': 'South',
        'N': 'North',
        'E': 'East',
        'W': 'West',
        'M': 'Midwest',
        'MW': 'Midwest',
        'Mid': 'Midwest',
        'Mid-West': 'Midwest',
        'Mid-Atlantic': 'MidAtlantic',
        'MA': 'MidAtlantic'
    }
    
    # Check if the full region name matches any map key
    if region in region_map:
        return region_map[region]
    
    # Check if the region starts with any of the keys
    for abbr, full in region_map.items():
        if region.startswith(abbr):
            return full
    
    return region

def categorize_chemical(chemical_name):
    """
    Categorize chemicals into standard groups.
    
    Args:
        chemical_name: The chemical name
        
    Returns:
        str: Chemical category
    """
    chemical_name = str(chemical_name).lower()
    
    category_patterns = {
        'Disinfectant': ['chlorine', 'bleach', 'sodium hypochlorite', 'hypochlorite', 'cl2'],
        'pH Adjustment': ['caustic', 'sodium hydroxide', 'lime', 'soda ash', 'sodium carbonate', 'acid', 'naoh'],
        'Coagulant': ['ferric', 'alum', 'aluminum sulfate', 'poly aluminum', 'coagulant'],
        'Polymer': ['polymer', 'flocculant'],
        'Oxidant': ['permanganate', 'kmno4', 'hydrogen peroxide', 'peracetic'],
        'Adsorbent': ['carbon', 'pac', 'gac', 'activated'],
        'Corrosion Control': ['phosphate', 'zinc', 'silicate', 'inhibitor']
    }
    
    for category, patterns in category_patterns.items():
        if any(pattern in chemical_name for pattern in patterns):
            return category
    
    return 'Other'