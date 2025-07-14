"""
Data Cleaning Utility

This module provides functions for cleaning and standardizing chemical names,
facility names, and other data points to improve consistency in reporting.
"""

import pandas as pd
import re
import numpy as np
from fuzzywuzzy import fuzz, process
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('data_cleaner')

def standardize_chemical_names(df, chemical_col='Chemical'):
    """
    Standardizes chemical names to improve consistency.
    
    Args:
        df: DataFrame containing chemical data
        chemical_col: Name of the column containing chemical names
        
    Returns:
        DataFrame: DataFrame with standardized chemical names added as a new column
    """
    # Create a copy to avoid modifying the original
    df_clean = df.copy()
    
    # Ensure the chemical column exists
    if chemical_col not in df_clean.columns:
        logger.warning(f"Chemical column '{chemical_col}' not found in dataframe")
        return df_clean
    
    # Add standardized column
    std_col = f"Standardized_{chemical_col}"
    
    # Apply standardization rules to each chemical name
    df_clean[std_col] = df_clean[chemical_col].apply(standardize_common_chemicals)
    
    # Log results
    original_unique = df_clean[chemical_col].nunique()
    std_unique = df_clean[std_col].nunique()
    reduction = original_unique - std_unique
    
    logger.info(f"Standardized chemical names: reduced from {original_unique} to {std_unique} unique values ({reduction} eliminated)")
    
    return df_clean

def standardize_common_chemicals(name):
    """
    Standardize names of common chemicals
    
    Args:
        name: Chemical name to standardize
        
    Returns:
        str: Standardized name
    """
    if pd.isna(name) or not isinstance(name, str):
        return "Unknown Chemical"
    
    # Clean up the name
    clean_name = name.strip()
    
    # Common standardization patterns
    
    # 1. Standardize oxidizers
    if re.search(r'sodium\s+hypochlorite|bleach|naocl', clean_name, re.IGNORECASE):
        return "Sodium Hypochlorite"
    
    if re.search(r'chlorine', clean_name, re.IGNORECASE):
        if re.search(r'dioxide|clo2', clean_name, re.IGNORECASE):
            return "Chlorine Dioxide"
        else:
            return "Chlorine"
    
    if re.search(r'hydrogen\s+peroxide|h2o2', clean_name, re.IGNORECASE):
        return "Hydrogen Peroxide"
    
    # 2. Standardize acids
    if re.search(r'sulfuric\s+acid|h2so4', clean_name, re.IGNORECASE):
        return "Sulfuric Acid"
    
    if re.search(r'hydrochloric\s+acid|muriatic|hcl', clean_name, re.IGNORECASE):
        return "Hydrochloric Acid"
    
    if re.search(r'phosphoric\s+acid|h3po4', clean_name, re.IGNORECASE):
        return "Phosphoric Acid"
    
    # 3. Standardize polymers
    if re.search(r'polymer|polyacrylamide', clean_name, re.IGNORECASE):
        if re.search(r'cationic', clean_name, re.IGNORECASE):
            return "Cationic Polymer"
        elif re.search(r'anionic', clean_name, re.IGNORECASE):
            return "Anionic Polymer"
        else:
            return "Polymer"
    
    # 4. Standardize coagulants
    if re.search(r'alum|aluminum\s+sulfate', clean_name, re.IGNORECASE):
        return "Aluminum Sulfate (Alum)"
    
    if re.search(r'pac|poly.+aluminum', clean_name, re.IGNORECASE):
        return "Polyaluminum Chloride (PAC)"
    
    if re.search(r'ferric\s+chloride|fecl3', clean_name, re.IGNORECASE):
        return "Ferric Chloride"
    
    # 5. Standardize bases
    if re.search(r'sodium\s+hydroxide|caustic|naoh', clean_name, re.IGNORECASE):
        return "Sodium Hydroxide (Caustic)"
    
    if re.search(r'calcium\s+hydroxide|lime|ca\(oh\)2', clean_name, re.IGNORECASE):
        return "Calcium Hydroxide (Lime)"
    
    # 6. Standardize disinfection chemicals
    if re.search(r'permanganate|kmno4', clean_name, re.IGNORECASE):
        return "Potassium Permanganate"
    
    # Return the original name for chemicals that don't match any patterns
    return clean_name

def standardize_facility_names(df, facility_col='Facility'):
    """
    Standardizes facility names to improve consistency.
    
    Args:
        df: DataFrame containing facility data
        facility_col: Name of the column containing facility names
        
    Returns:
        DataFrame: DataFrame with standardized facility names added as a new column
    """
    # Create a copy to avoid modifying the original
    df_clean = df.copy()
    
    # Ensure the facility column exists
    if facility_col not in df_clean.columns:
        logger.warning(f"Facility column '{facility_col}' not found in dataframe")
        return df_clean
    
    # Add standardized column
    std_col = f"Standardized_{facility_col}"
    
    # First, get unique facility names
    unique_facilities = df_clean[facility_col].dropna().unique()
    
    # Group similar facilities
    grouped_facilities = group_similar_names(unique_facilities)
    
    # Create mapping dictionary from grouped facilities
    facility_mapping = {}
    for group, facilities in grouped_facilities.items():
        for facility in facilities:
            facility_mapping[facility] = group
    
    # Apply mapping to create standardized names
    df_clean[std_col] = df_clean[facility_col].map(facility_mapping).fillna(df_clean[facility_col])
    
    # Log results
    original_unique = df_clean[facility_col].nunique()
    std_unique = df_clean[std_col].nunique()
    reduction = original_unique - std_unique
    
    logger.info(f"Standardized facility names: reduced from {original_unique} to {std_unique} unique values ({reduction} eliminated)")
    
    return df_clean

def group_similar_names(name_list, threshold=85):
    """
    Groups similar names together using fuzzy matching.
    
    Args:
        name_list: List of strings to group
        threshold: Similarity threshold for grouping (0-100)
        
    Returns:
        dict: Dictionary mapping standardized names to lists of original names
    """
    # Initialize groups
    groups = {}
    processed = set()
    
    # Sort names by length (shortest first)
    sorted_names = sorted(name_list, key=lambda x: len(str(x)) if pd.notna(x) else 0)
    
    for name in sorted_names:
        # Skip if already processed or not a string
        if name in processed or not isinstance(name, str):
            continue
            
        # This name becomes the group representative
        group = [name]
        processed.add(name)
        
        # Check all other names for similarity
        for other in sorted_names:
            if other not in processed and isinstance(other, str):
                # Calculate similarity ratio
                similarity = fuzz.ratio(name.lower(), other.lower())
                
                # If similar enough, add to this group
                if similarity >= threshold:
                    group.append(other)
                    processed.add(other)
        
        # Store the group with its representative as the key
        groups[name] = group
    
    return groups

def standardize_regions(df, region_col='Region'):
    """
    Preserves original region codes while adding a standardized region column.
    As requested, we keep the original region codes without mapping.
    
    Args:
        df: DataFrame containing region data
        region_col: Name of the column containing region codes
        
    Returns:
        DataFrame: DataFrame with region code information preserved
    """
    # Create a copy to avoid modifying the original
    df_clean = df.copy()
    
    # Ensure the region column exists
    if region_col not in df_clean.columns:
        logger.warning(f"Region column '{region_col}' not found in dataframe")
        return df_clean
    
    # Add a regionCode column that contains the exact original values
    region_code_col = "RegionCode"
    if region_code_col not in df_clean.columns:
        df_clean[region_code_col] = df_clean[region_col]
        logger.info(f"Added '{region_code_col}' column with original region values")
    
    # Just count unique values without mapping
    unique_regions = df_clean[region_col].nunique()
    logger.info(f"Found {unique_regions} unique region codes: {df_clean[region_col].unique().tolist()}")
    
    return df_clean

def clean_dataset(df, report_type):
    """
    Performs comprehensive data cleaning on a dataset.
    
    Args:
        df: DataFrame to clean
        report_type: Type of report ('po_line_detail' or 'non_po_invoice')
        
    Returns:
        DataFrame: Cleaned DataFrame with standardized columns
    """
    # Create a copy to avoid modifying the original
    df_cleaned = df.copy()
    
    # Log the cleaning process
    logger.info(f"Cleaning {report_type} dataset with {len(df_cleaned)} rows")
    
    # 1. Standardize chemical names
    df_cleaned = standardize_chemical_names(df_cleaned)
    
    # 2. Standardize facility names
    df_cleaned = standardize_facility_names(df_cleaned)
    
    # 3. Standardize regions
    df_cleaned = standardize_regions(df_cleaned)
    
    # Log results
    logger.info(f"Cleaning complete: {len(df_cleaned)} rows processed")
    
    return df_cleaned