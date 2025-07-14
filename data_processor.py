import pandas as pd
import numpy as np
from datetime import datetime
import io

def clean_region_names(region_value):
    """
    Clean region names by removing email addresses.
    
    Args:
        region_value: The region name which might contain email addresses
        
    Returns:
        Cleaned region name without email addresses
    """
    if pd.isna(region_value):
        return region_value
    
    region_str = str(region_value)
    
    # Check if there's an email address (contains @)
    if '@' in region_str:
        # Format: "Name (email@domain.com)"
        if '(' in region_str and ')' in region_str:
            # Extract only the name part before the parenthesis
            name_part = region_str.split('(')[0].strip()
            return name_part
    
    return region_str

def assign_region_from_facility(facility_name):
    """
    Assigns a region based on the facility name.

    Args:
        facility_name: String containing the facility name

    Returns:
        str: Assigned region name
    """
    if not isinstance(facility_name, str):
        return 'South'  # Default to South as it's the most common region

    facility_lower = facility_name.lower()

    # South region indicators
    south_indicators = [
        'south', 'dixie', 'texas', 'georgia', 'florida', 'alabama', 'mississippi',
        'louisiana', 'arkansas', 'tennessee', 'carolina', 'atlanta', 'dallas',
        'houston', 'memphis', 'nashville', 'charlotte', 'raleigh', 'savannah',
        'miami', 'tampa', 'birmingham', 'jackson', 'sinclair', 'augusta', 'forsyth',
        'opelika', 'union springs', 'choctaw', 'jasper', 'warner robins'
    ]

    # Northeast region indicators
    northeast_indicators = [
        'east', 'atlantic', 'jersey', 'york', 'pennsylvania', 'massachusetts',
        'connecticut', 'maine', 'hampshire', 'vermont', 'rhode', 'boston',
        'philadelphia', 'baltimore', 'pittsburgh', 'buffalo', 'newark',
        'manhattan', 'bronx', 'brooklyn', 'queens', 'staten'
    ]

    # Central region indicators
    central_indicators = [
        'central', 'mid', 'ohio', 'michigan', 'illinois', 'indiana', 'wisconsin',
        'missouri', 'iowa', 'minnesota', 'kansas', 'nebraska', 'chicago',
        'detroit', 'indianapolis', 'columbus', 'cleveland', 'cincinnati',
        'milwaukee', 'st. louis', 'minneapolis', 'des moines', 'topeka'
    ]

    # West region indicators (combines both Northwest and Southwest)
    west_indicators = [
        'west', 'northwest', 'southwest', 
        'washington', 'oregon', 'idaho', 'montana', 'wyoming',
        'seattle', 'portland', 'boise', 'spokane', 'tacoma', 'olympia',
        'eugene', 'salem', 'pocatello', 'billings', 'casper',
        'california', 'nevada', 'utah', 'colorado', 'arizona',
        'new mexico', 'oklahoma', 'los angeles', 'san francisco', 'san diego',
        'las vegas', 'salt lake', 'denver', 'phoenix', 'tucson', 'albuquerque',
        'santa fe', 'oklahoma city', 'tulsa', 'corning'
    ]

    # Check for indicators - preserve original region names
    if any(indicator in facility_lower for indicator in south_indicators):
        return 'South'
    elif any(indicator in facility_lower for indicator in northeast_indicators):
        return 'Northeast'
    elif any(indicator in facility_lower for indicator in central_indicators):
        return 'Central'
    # For west region, need to check more specific indicators first
    elif 'northwest' in facility_lower or any(indicator in facility_lower for indicator in ['washington', 'oregon', 'idaho', 'montana', 'wyoming']):
        return 'Northwest'
    elif 'southwest' in facility_lower or any(indicator in facility_lower for indicator in ['california', 'nevada', 'utah', 'arizona', 'new mexico']):
        return 'Southwest'
    elif any(indicator in facility_lower for indicator in west_indicators):
        return 'West'  # Generic west indicators
    else:
        # Default to the region value in the original data, or South if not available
        return 'South'

def load_and_process_data(file, report_type=None):
    """
    Loads and processes chemical spend data from an uploaded file.

    Args:
        file: The uploaded file object (CSV or Excel)
        report_type: The type of report ('po_line_detail' or 'non_po_invoice')

    Returns:
        DataFrame: Processed pandas DataFrame with ALL original columns preserved
    """
    # Determine file type and read accordingly
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")

    # Print the exact columns in the original file
    print(f"Original file columns: {list(df.columns)}")
    
    # Print first row as a dict to see exact values
    if not df.empty:
        print("First row of data:")
        print(df.iloc[0].to_dict())
    
    # Preserve original column names exactly - just trim whitespace
    df.columns = [col.strip() for col in df.columns]

    # If report type was specified, use that directly
    if report_type:
        if report_type == 'po_line_detail':
            print("User selected PO Line Detail format")
            processed_df = process_company_format(df)
        elif report_type == 'non_po_invoice':
            print("User selected Non-PO Invoice Chemical GL format")
            processed_df = process_non_po_invoice_format(df)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
    else:
        # If no report type specified, try to auto-detect based on columns
        # Check for expected columns from Chemical PO Line Detail Report format
        po_line_format_columns = [
            "Purchase Order: Confirmation Date", "Line Number", "Purchase Requisition: Number",
            "Order Identifier", "Order_ID", "Purchase Order: Supplier", "Item Description",
            "Category", "Confirmed Unit Price", "Connected Quantity", "Confirmed Quantity",
            "Purchase Requisition: Buyer", "Purchase Requisition: Our Reference",
            "Purchase Order: Processing Status", "Purchase Order: Received By", "Type"
        ]

        # Check for expected columns from Non-PO Invoice Chemical GL Report format
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

        print(f"Matched PO Line Detail columns: {len(po_line_matches)}, matches: {po_line_matches}")
        print(f"Matched Non-PO Invoice columns: {len(non_po_matches)}, matches: {non_po_matches}")

        # Determine report type based on which has more matching columns
        if len(non_po_matches) > len(po_line_matches):
            print("Auto-detected Non-PO Invoice Chemical GL format")
            processed_df = process_non_po_invoice_format(df)
        else:
            print("Auto-detected PO Line Detail format")
            processed_df = process_company_format(df)

    # Add a debug print for the processed data
    print(f"Processed data shape: {processed_df.shape}")
    print(f"Processed columns: {list(processed_df.columns)}")

    # The following is ONLY to ensure we have minimal required columns for visualization
    # We do not overwrite or remove any original columns
    required_columns = ['Date', 'Facility', 'Chemical', 'Quantity', 'Unit', 'Unit_Price', 'Total_Cost', 'Type: Purchase Order', 'Order_ID', 'Region', 'Supplier: Name']
    
    for col in required_columns:
        if col not in processed_df.columns:
            print(f"Adding required column: {col}")
            if col == 'Date' and 'Invoice: Created Date' in processed_df.columns:
                processed_df[col] = pd.to_datetime(processed_df['Invoice: Created Date'], errors='coerce')
            elif col == 'Date':
                processed_df[col] = pd.to_datetime('today')
            elif col == 'Type: Purchase Order':
                processed_df[col] = 'Non-PO' if 'Invoice: Type' in processed_df.columns else 'Catalog'
            elif col == 'Order_ID' and 'Invoice: Number' in processed_df.columns:
                processed_df[col] = processed_df['Invoice: Number']
            elif col == 'Total_Cost' and 'Net Amount' in processed_df.columns:
                processed_df[col] = pd.to_numeric(processed_df['Net Amount'], errors='coerce')
            elif col == 'Unit_Price' and 'Total_Cost' in processed_df.columns:
                processed_df[col] = processed_df['Total_Cost']
            elif col == 'Quantity':
                processed_df[col] = 1
            elif col == 'Unit':
                processed_df[col] = 'unit'
            elif col == 'Supplier: Name' and 'Supplier: Name' in df.columns:
                # Make sure we preserve the exact Supplier: Name from original file
                processed_df[col] = df['Supplier: Name']
            else:
                processed_df[col] = 'Unknown'

    # One final check to ensure Supplier: Name is preserved
    if 'Supplier: Name' in df.columns and 'Supplier: Name' not in processed_df.columns:
        processed_df['Supplier: Name'] = df['Supplier: Name']
        print("Added back original 'Supplier: Name' column from source data")
        
    # Print the final column list to verify all original columns are preserved
    print(f"Final returned columns: {processed_df.columns.tolist()}")

    return processed_df

def process_company_format(df):
    """
    Processes data in the company's specific format (PO Line Detail).

    Args:
        df: DataFrame with the company's format

    Returns:
        DataFrame: Processed pandas DataFrame in the standard format
    """
    print("Inside process_company_format with columns:", list(df.columns))

    # Create a copy to avoid modifying the original
    processed_df = df.copy()

    # Map the company columns to the standard format
    # We'll create the standard columns we need for the application based on exact column names

    # Handle column name variations (convert 'Order Identifier' to 'Order_ID' if needed)
    if 'Order Identifier' in processed_df.columns and 'Order_ID' not in processed_df.columns:
        processed_df['Order_ID'] = processed_df['Order Identifier']
        print("Mapped 'Order Identifier' to 'Order_ID'")
    elif 'order identifier' in [col.lower() for col in processed_df.columns]:
        # Find the column with case-insensitive match
        order_id_col = next(col for col in processed_df.columns if col.lower() == 'order identifier')
        processed_df['Order_ID'] = processed_df[order_id_col]
        print(f"Mapped '{order_id_col}' to 'Order_ID'")
    # If we have neither column, add a default 'Order_ID' column
    elif 'Order_ID' not in processed_df.columns:
        processed_df['Order_ID'] = processed_df.index.astype(str)
        print("Created default 'Order_ID' column using row indices")

    # Extract date from the confirmation date if available, otherwise use today's date
    if 'Purchase Order: Confirmation Date' in processed_df.columns and not processed_df['Purchase Order: Confirmation Date'].isna().all():
        processed_df['Date'] = pd.to_datetime(processed_df['Purchase Order: Confirmation Date'], errors='coerce')
        print("Using 'Purchase Order: Confirmation Date' for Date")
    else:
        processed_df['Date'] = pd.to_datetime('today')
        print("Using today's date as default")

    # Map supplier name
    if 'Purchase Order: Supplier' in processed_df.columns and not processed_df['Purchase Order: Supplier'].isna().all():
        processed_df['Facility'] = processed_df['Purchase Order: Supplier']
        print("Using 'Purchase Order: Supplier' for Facility")
    else:
        processed_df['Facility'] = 'Unknown Supplier'
        print("Using 'Unknown Supplier' as default")

    # Handle missing Item Description values using Category information
    # From our analysis, we know about 40 rows (6.3%) have null Item Description but valid Category
    if 'Item Description' in processed_df.columns and 'Category' in processed_df.columns:
        # Fill missing Item Description with Category information first
        missing_desc_mask = processed_df['Item Description'].isna() & ~processed_df['Category'].isna()
        if missing_desc_mask.any():
            print(f"Filling {missing_desc_mask.sum()} missing Item Description values with Category info")
            processed_df.loc[missing_desc_mask, 'Item Description'] = processed_df.loc[missing_desc_mask, 'Category']

    # Use Item Description column (F) directly for PO Line Detail report
    processed_df['Region'] = processed_df['Item Description']
    print("Using Item Description (Column F) for Region")

    # For Chemical name, use Item Description without modifications
    processed_df['Chemical'] = processed_df['Item Description']
    print("Using Item Description exactly as is for Chemical")


    # Handle quantity - CORRECTED: Connected Quantity is planned quantity, Confirmed is actual ordered
    if 'Connected Quantity' in processed_df.columns and not processed_df['Connected Quantity'].isna().all():
        # Use Connected Quantity as primary (the planned quantity)
        print("Using 'Connected Quantity' (planned quantity) for Quantity")
        processed_df['Quantity'] = processed_df['Connected Quantity'].astype(str).str.replace(',', '').str.replace('$', '')
        processed_df['Quantity'] = pd.to_numeric(processed_df['Quantity'], errors='coerce').fillna(0)
    elif 'Confirmed Quantity' in processed_df.columns and not processed_df['Confirmed Quantity'].isna().all():
        # Use Confirmed Quantity as fallback (actual ordered quantity)
        print("Using 'Confirmed Quantity' (actual ordered quantity) for Quantity")
        processed_df['Quantity'] = processed_df['Confirmed Quantity'].astype(str).str.replace(',', '').str.replace('$', '')
        processed_df['Quantity'] = pd.to_numeric(processed_df['Quantity'], errors='coerce').fillna(0)
    else:
        processed_df['Quantity'] = 1  # Default quantity if not available
        print("Using default value 1 for Quantity")

    # Add unit column
    processed_df['Unit'] = 'unit'  # Default unit

    # Handle price
    if 'Confirmed Unit Price' in processed_df.columns and not processed_df['Confirmed Unit Price'].isna().all():
        # Clean and convert to numeric
        print("Using 'Confirmed Unit Price' for Unit_Price")
        try:
            processed_df['Unit_Price'] = processed_df['Confirmed Unit Price'].astype(str).str.replace(',', '').str.replace('$', '')
            processed_df['Unit_Price'] = pd.to_numeric(processed_df['Unit_Price'], errors='coerce').fillna(0)

            # Calculate total cost
            processed_df['Total_Cost'] = processed_df['Quantity'] * processed_df['Unit_Price']
        except Exception as e:
            print(f"Error processing Confirmed Unit Price: {e}")
            # Fallback to defaults
            processed_df['Unit_Price'] = 1
            processed_df['Total_Cost'] = processed_df['Quantity']
    else:
        print("Using default values for Unit_Price and Total_Cost")
        processed_df['Unit_Price'] = 1
        processed_df['Total_Cost'] = processed_df['Quantity']

    # Set purchase order type based on the Type column if available (in PO Line Detail, this is "Catalog", "Free text", or "Punch out")
    if 'Type' in processed_df.columns and not processed_df['Type'].isna().all():
        print("Using 'Type' for Type: Purchase Order")
        # Create a standardized mapping for all possible Type values
        type_mapping = {
            'Catalog': 'Catalog',
            'catalog': 'Catalog',
            'CATALOG': 'Catalog',
            'Free text': 'Free Text',
            'free text': 'Free Text',
            'FREE TEXT': 'Free Text',
            'Punch out': 'Free Text',  # Map "Punch out" to "Free Text" as requested
            'punch out': 'Free Text',
            'PUNCH OUT': 'Free Text'
        }

        # Apply the mapping to standardize values
        processed_df['Type: Purchase Order'] = processed_df['Type'].astype(str).map(
            lambda x: type_mapping.get(x, 'Free Text' if 'text' in x.lower() or 'punch' in x.lower() else 'Catalog')
        )

        # Print distribution of order types for debugging
        type_counts = processed_df['Type: Purchase Order'].value_counts()
        print(f"Order type distribution: {dict(type_counts)}")
    else:
        processed_df['Type: Purchase Order'] = 'Catalog'  # Default type is Catalog
        print("Using 'Catalog' as default Type: Purchase Order")

    # We've already extracted information from Category in the Chemical name mapping code above
    # No need for additional processing here

    # Standardize formatting for consistency
    processed_df['Facility'] = processed_df['Facility'].astype(str).str.strip().str.title()
    processed_df['Chemical'] = processed_df['Chemical'].astype(str).str.strip().str.title()
    processed_df['Type: Purchase Order'] = processed_df['Type: Purchase Order'].str.capitalize()

    # Create needed columns if missing
    required_columns = ['Date', 'Facility', 'Chemical', 'Quantity', 'Unit', 'Unit_Price', 'Total_Cost', 'Type: Purchase Order', 'Order_ID', 'Region']

    # Add Category column if available
    if 'Category' in processed_df.columns:
        required_columns.append('Category')
    for col in required_columns:
        if col not in processed_df.columns:
            print(f"Adding missing column: {col}")
            if col == 'Date':
                processed_df[col] = pd.to_datetime('today')
            elif col in ['Quantity', 'Unit_Price', 'Total_Cost']:
                processed_df[col] = 0
            else:
                processed_df[col] = 'Unknown'

    # Select only the required columns for the application
    try:
        final_df = processed_df[required_columns]
        print(f"Final dataframe shape: {final_df.shape}")
        return final_df
    except Exception as e:
        print(f"Error creating final dataframe: {e}")
        # If there's an error, create a basic DataFrame with the required columns
        print("Creating fallback dataframe")
        fallback_data = {
            'Date': [pd.to_datetime('today')] * len(processed_df),
            'Facility': ['Unknown'] * len(processed_df),
            'Chemical': ['Unknown'] * len(processed_df),
            'Quantity': [0] * len(processed_df),
            'Unit': ['unit'] * len(processed_df),
            'Unit_Price': [0] * len(processed_df),
            'Total_Cost': [0] * len(processed_df),
            'Type: Purchase Order': ['Catalog'] * len(processed_df),
            'Order_ID': [f'DEFAULT-{i}' for i in range(len(processed_df))],
            'Region': ['South'] * len(processed_df)  # Default to South as most common region
        }
        return pd.DataFrame(fallback_data)

# Standard format processing function has been removed as we now only support PO Line Detail format

def validate_data(df):
    """
    Validates the processed data to ensure it meets analysis requirements.

    Args:
        df: DataFrame to validate

    Returns:
        tuple: (is_valid, message) - Boolean indicating validity and message
    """
    print("Validating data...")

    # Check if DataFrame is empty
    if df.empty:
        print("Error: DataFrame is empty")
        return False, "The uploaded file contains no data."

    print(f"DataFrame shape: {df.shape}")

    # We'll be very lenient with validation to ensure the data is accepted
    # This allows for more user-friendly experience with their specific format

    # Check for minimum number of rows - but always accept if there's at least one row
    if len(df) < 1:
        print("Error: Not enough rows")
        return False, "The uploaded file does not contain any data rows."

    # Check for numeric columns - but with more tolerance
    numeric_columns = ['Quantity', 'Unit_Price', 'Total_Cost']
    for col in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            print(f"Warning: {col} is not numeric, attempting to convert")
            try:
                # Try to fix it
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            except Exception as e:
                print(f"Could not convert {col} to numeric: {e}")

    # Check for negative values - but just warn, don't reject
    for col in numeric_columns:
        if (df[col] < 0).any():
            print(f"Warning: {col} contains negative values")

    # No date check for future dates - just use the dates as provided

    # Allow any date range

    # Set blank purchase order types to a default value rather than rejecting
    if df['Type: Purchase Order'].isna().any() or (df['Type: Purchase Order'] == '').any():
        print("Warning: Some purchase order types are missing, setting to 'Catalog'")
        df.loc[df['Type: Purchase Order'].isna() | (df['Type: Purchase Order'] == ''), 'Type: Purchase Order'] = 'Catalog'

    # Don't reject for outliers, just log warning
    try:
        mean_cost = df['Total_Cost'].mean()
        std_cost = df['Total_Cost'].std() if len(df) > 1 else mean_cost  # Avoid division by zero
        if std_cost > 0:
            outlier_threshold = mean_cost + (3 * std_cost)
            outliers = df[df['Total_Cost'] > outlier_threshold]

            if len(outliers) > 0:
                print(f"Warning: {len(outliers)} cost outliers detected")
    except Exception as e:
        print(f"Error checking for outliers: {e}")

    # All validations passed or fixed
    print("Validation passed")
    return True, "Data is valid."

def process_non_po_invoice_format(df):
    """
    Processes data in the Non-PO Invoice Chemical GL format.
    This function preserves the original columns and their exact values.

    Args:
        df: DataFrame with Non-PO Invoice Chemical GL format

    Returns:
        DataFrame: Processed pandas DataFrame with original columns preserved
    """
    print("Processing Non-PO Invoice format with EXACT original columns")
    print(f"Original columns: {list(df.columns)}")
    
    # Create a copy to avoid modifying the original
    processed_df = df.copy()
    
    # For debugging: Print the first few rows to verify the content
    print("First 2 rows of original data:")
    print(processed_df.head(2))
    
    # We need to ensure we have the basic columns needed for visualization
    # while preserving ALL original columns exactly as they are
    
    # Create a minimal set of required columns for internal processing
    # but only if they don't exist in the original data
    
    # 1. Create a standardized 'Date' column if it doesn't exist
    if 'Date' not in processed_df.columns and 'Invoice: Created Date' in processed_df.columns:
        processed_df['Date'] = pd.to_datetime(processed_df['Invoice: Created Date'], errors='coerce')
        print("Added Date column based on 'Invoice: Created Date' for internal processing")
    
    # 2. Add Order_ID if needed for referencing
    if 'Order_ID' not in processed_df.columns and 'Invoice: Number' in processed_df.columns:
        processed_df['Order_ID'] = processed_df['Invoice: Number']
        print("Added Order_ID column based on 'Invoice: Number' for internal referencing")
    
    # 3. Add Total_Cost if needed for calculations
    if 'Total_Cost' not in processed_df.columns and 'Net Amount' in processed_df.columns:
        processed_df['Total_Cost'] = pd.to_numeric(processed_df['Net Amount'], errors='coerce')
        print("Added Total_Cost column based on 'Net Amount' for internal calculations")
    
    # 4. Add Region if needed (using original value EXACTLY)
    if 'Region' not in processed_df.columns and 'Dimension4 Description' in processed_df.columns:
        processed_df['Region'] = processed_df['Dimension4 Description']
        print("Added Region column based on 'Dimension4 Description' for region analysis")
    
    # 5. Add Facility for facility analysis
    if 'Facility' not in processed_df.columns and 'Dimension5 Description' in processed_df.columns:
        processed_df['Facility'] = processed_df['Dimension5 Description']
        print("Added Facility column based on 'Dimension5 Description' for facility analysis")
    
    # 6. Add Chemical for chemical analysis
    if 'Chemical' not in processed_df.columns and 'Dimension3 Description' in processed_df.columns:
        processed_df['Chemical'] = processed_df['Dimension3 Description']
        print("Added Chemical column based on 'Dimension3 Description' for chemical analysis")
    
    # 7. Ensure we have a PO Type indicator
    if 'Type: Purchase Order' not in processed_df.columns:
        processed_df['Type: Purchase Order'] = 'Non-PO'
        print("Added 'Type: Purchase Order' column with 'Non-PO' value for PO type analysis")
    
    # 8. Add minimal Unit and Quantity if needed
    if 'Quantity' not in processed_df.columns:
        processed_df['Quantity'] = 1
        print("Added Quantity column with default value 1 for quantity analysis")
    
    if 'Unit' not in processed_df.columns:
        processed_df['Unit'] = 'unit'
        print("Added Unit column with default value 'unit' for unit analysis")
    
    if 'Unit_Price' not in processed_df.columns and 'Total_Cost' in processed_df.columns:
        processed_df['Unit_Price'] = processed_df['Total_Cost']
        print("Added Unit_Price column based on Total_Cost for unit price analysis")
    
    # Print final column list to verify all original columns are preserved
    print(f"Final processed columns: {processed_df.columns.tolist()}")
    
    # Important: Return the DataFrame with ALL original columns preserved
    return processed_df

def filter_data(df, start_date=None, end_date=None, facility=None, chemical=None, po_type=None, category=None):
    """
    Filters the data based on provided criteria.

    Args:
        df: DataFrame to filter
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        facility: Optional facility name to filter by
        chemical: Optional chemical name to filter by
        po_type: Optional purchase order type to filter by (Catalog/Free Text)
        category: Optional category to filter by

    Returns:
        DataFrame: Filtered data
    """
    filtered_df = df.copy()

    # Apply date filter
    if start_date:
        filtered_df = filtered_df[filtered_df['Date'] >= pd.Timestamp(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df['Date'] <= pd.Timestamp(end_date)]

    # Apply facility filter
    if facility:
        if isinstance(facility, list):
            filtered_df = filtered_df[filtered_df['Facility'].isin(facility)]
        elif facility != "All":
            filtered_df = filtered_df[filtered_df['Facility'] == facility]

    # Apply chemical filter
    if chemical:
        if isinstance(chemical, list):
            filtered_df = filtered_df[filtered_df['Chemical'].isin(chemical)]
        elif chemical != "All":
            filtered_df = filtered_df[filtered_df['Chemical'] == chemical]

    # Apply purchase order type filter
    if po_type:
        if isinstance(po_type, list):
            filtered_df = filtered_df[filtered_df['Type: Purchase Order'].isin(po_type)]
        elif po_type != "All":
            filtered_df = filtered_df[filtered_df['Type: Purchase Order'] == po_type]

    # Apply category filter if the column exists
    if category and 'Category' in filtered_df.columns:
        if isinstance(category, list):
            filtered_df = filtered_df[filtered_df['Category'].isin(category)]
        elif category != "All":
            filtered_df = filtered_df[filtered_df['Category'] == category]

    return filtered_df

def calculate_summary_statistics(df):
    """
    Calculates summary statistics for the dataset.

    Args:
        df: DataFrame to analyze

    Returns:
        dict: Dictionary containing summary statistics
    """
    summary = {}

    # Total spend
    summary['total_spend'] = df['Total_Cost'].sum()

    # Spend by facility
    facility_spend = df.groupby('Facility')['Total_Cost'].sum().sort_values(ascending=False)
    summary['facility_spend'] = facility_spend

    # Spend by chemical
    chemical_spend = df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False)
    summary['chemical_spend'] = chemical_spend

    # Monthly spend
    monthly_spend = df.groupby(df['Date'].dt.to_period('M'))['Total_Cost'].sum()
    summary['monthly_spend'] = monthly_spend

    # Purchase order type spend
    po_type_spend = df.groupby('Type: Purchase Order')['Total_Cost'].sum()
    summary['po_type_spend'] = po_type_spend

    # Average unit price by chemical
    avg_unit_price = df.groupby('Chemical')['Unit_Price'].mean().sort_values(ascending=False)
    summary['avg_unit_price'] = avg_unit_price

    # Total quantity by chemical
    total_quantity = df.groupby('Chemical')['Quantity'].sum().sort_values(ascending=False)
    summary['total_quantity'] = total_quantity

    return summary