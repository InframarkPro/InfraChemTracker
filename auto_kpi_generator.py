"""
Auto KPI Generator

This module automatically analyzes uploaded data and generates appropriate KPIs
based on the exact column names provided in the data, without any column renaming or mapping.
"""

import pandas as pd
import numpy as np
import logging
import re
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_columns(df):
    """
    Analyze the dataframe columns and categorize them by data type.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        dict: Dictionary with categorized columns
    """
    column_types = {
        'date': [],
        'numeric': [],
        'categorical': [],
        'text': [],
        'boolean': [],
        'id': [],
        'unknown': []
    }
    
    # Log the original column names
    logger.info(f"Auto KPI Generator analyzing {len(df.columns)} columns with original names: {df.columns.tolist()}")
    
    for col in df.columns:
        col_type = str(df[col].dtype)
        sample = df[col].dropna().head(5).tolist()
        sample_str = str(sample)[:100] + "..." if len(str(sample)) > 100 else str(sample)
        logger.info(f"Column '{col}', Type: {col_type}, Sample: {sample_str}")
        
        # Check for ID columns
        if any(term in col.lower() for term in ['id', 'number', 'identifier', 'code', 'key']):
            column_types['id'].append(col)
            continue
            
        # Check for date columns
        if 'datetime' in col_type or 'date' in col_type:
            column_types['date'].append(col)
        elif 'date' in col.lower() or any(date_term in col.lower() for date_term in ['time', 'year', 'month', 'day']):
            # Try to convert to datetime if possible
            try:
                pd.to_datetime(df[col].dropna().iloc[0])
                column_types['date'].append(col)
            except:
                column_types['text'].append(col)
        # Check for numeric columns
        elif 'int' in col_type or 'float' in col_type:
            column_types['numeric'].append(col)
        elif 'amount' in col.lower() or 'price' in col.lower() or 'cost' in col.lower() or 'quantity' in col.lower():
            # Try to convert to numeric if possible
            try:
                pd.to_numeric(df[col])
                column_types['numeric'].append(col)
            except:
                column_types['text'].append(col)
        # Check for boolean columns
        elif 'bool' in col_type:
            column_types['boolean'].append(col)
        # Check for categorical columns
        elif df[col].nunique() < min(20, len(df) / 10):  # If unique values < 20 or < 10% of data
            column_types['categorical'].append(col)
        # Default to text
        else:
            column_types['text'].append(col)
    
    logger.info(f"Column analysis results: {column_types}")
    return column_types

def identify_kpi_candidates(df, column_types):
    """
    Identify potential KPI candidates from the dataset based on column analysis.
    
    Args:
        df: DataFrame to analyze
        column_types: Dictionary with categorized columns from analyze_columns
        
    Returns:
        dict: Dictionary with KPI candidates and their properties
    """
    kpi_candidates = []
    
    # Count metrics
    for id_col in column_types['id']:
        kpi_candidates.append({
            'name': f'Total {id_col.replace("_", " ").title()}',
            'description': f'Count of unique {id_col}',
            'type': 'count',
            'value': df[id_col].nunique(),
            'column': id_col,
            'format': 'number'
        })
    
    # Date range metrics
    for date_col in column_types['date']:
        try:
            # Ensure the column is in datetime format
            if df[date_col].dtype != 'datetime64[ns]':
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            min_date = df[date_col].min()
            max_date = df[date_col].max()
            
            if pd.notna(min_date) and pd.notna(max_date):
                date_range = max_date - min_date
                days_in_range = date_range.days
                
                kpi_candidates.append({
                    'name': f'{date_col.replace("_", " ").title()} Range',
                    'description': f'Date range from {min_date.strftime("%Y-%m-%d")} to {max_date.strftime("%Y-%m-%d")}',
                    'type': 'date_range',
                    'value': days_in_range,
                    'column': date_col,
                    'format': 'days',
                    'start_date': min_date,
                    'end_date': max_date
                })
        except Exception as e:
            logger.warning(f"Could not calculate date metrics for {date_col}: {str(e)}")
    
    # Sum metrics for numeric columns with amount, price, cost in name
    for num_col in column_types['numeric']:
        col_lower = num_col.lower()
        
        # Create sum metrics for financial columns
        if any(term in col_lower for term in ['amount', 'price', 'cost', 'value', 'spend']):
            try:
                sum_value = df[num_col].sum()
                avg_value = df[num_col].mean()
                
                # Special formatting for financial values
                format_type = 'currency' if any(term in col_lower for term in ['amount', 'price', 'cost', 'value', 'spend']) else 'number'
                
                kpi_candidates.append({
                    'name': f'Total {num_col.replace("_", " ").title()}',
                    'description': f'Sum of all {num_col}',
                    'type': 'sum',
                    'value': sum_value,
                    'column': num_col,
                    'format': format_type
                })
                
                kpi_candidates.append({
                    'name': f'Average {num_col.replace("_", " ").title()}',
                    'description': f'Average of {num_col}',
                    'type': 'average',
                    'value': avg_value,
                    'column': num_col,
                    'format': format_type
                })
            except Exception as e:
                logger.warning(f"Could not calculate sum metrics for {num_col}: {str(e)}")
        
        # Create count metrics for quantity columns
        elif any(term in col_lower for term in ['quantity', 'count', 'number']):
            try:
                sum_value = df[num_col].sum()
                
                kpi_candidates.append({
                    'name': f'Total {num_col.replace("_", " ").title()}',
                    'description': f'Sum of all {num_col}',
                    'type': 'sum',
                    'value': sum_value,
                    'column': num_col,
                    'format': 'number'
                })
            except Exception as e:
                logger.warning(f"Could not calculate sum metrics for {num_col}: {str(e)}")
    
    # Distribution metrics for categorical columns
    for cat_col in column_types['categorical']:
        try:
            # Get value counts
            value_counts = df[cat_col].value_counts()
            top_value = value_counts.index[0] if not value_counts.empty else "None"
            top_count = value_counts.iloc[0] if not value_counts.empty else 0
            
            kpi_candidates.append({
                'name': f'{cat_col.replace("_", " ").title()} Categories',
                'description': f'Number of unique {cat_col} categories',
                'type': 'category_count',
                'value': len(value_counts),
                'column': cat_col,
                'format': 'number'
            })
            
            kpi_candidates.append({
                'name': f'Top {cat_col.replace("_", " ").title()}',
                'description': f'Most frequent {cat_col}',
                'type': 'top_category',
                'value': str(top_value),
                'column': cat_col,
                'format': 'text',
                'count': top_count,
                'percentage': (top_count / len(df)) * 100 if len(df) > 0 else 0
            })
        except Exception as e:
            logger.warning(f"Could not calculate distribution metrics for {cat_col}: {str(e)}")
    
    # Special metrics for common columns
    # Look for columns like "Type" that might indicate order types (Catalog/Free Text)
    type_columns = [col for col in df.columns if 'type' in col.lower()]
    for type_col in type_columns:
        try:
            value_counts = df[type_col].value_counts()
            
            # Check for catalog vs free text pattern
            has_catalog = any('catalog' in str(val).lower() for val in value_counts.index)
            has_free_text = any('free' in str(val).lower() and 'text' in str(val).lower() for val in value_counts.index)
            
            if has_catalog and has_free_text:
                # This looks like a PO Type column with Catalog vs Free Text values
                catalog_count = sum(df[type_col].str.lower().str.contains('catalog', na=False))
                free_text_count = sum(df[type_col].str.lower().str.contains('free', na=False) & 
                                    df[type_col].str.lower().str.contains('text', na=False))
                total_count = catalog_count + free_text_count
                
                catalog_pct = (catalog_count / total_count * 100) if total_count > 0 else 0
                
                kpi_candidates.append({
                    'name': 'Catalog Order Percentage',
                    'description': 'Percentage of orders that are Catalog vs Free Text',
                    'type': 'percentage',
                    'value': catalog_pct,
                    'column': type_col,
                    'format': 'percentage',
                    'numerator': catalog_count,
                    'denominator': total_count,
                    'is_key_kpi': True
                })
        except Exception as e:
            logger.warning(f"Could not calculate type distribution metrics for {type_col}: {str(e)}")
    
    # Look for invoice or PO indicators
    if any('invoice' in col.lower() for col in df.columns) and not any('po' in col.lower() for col in df.columns):
        # This appears to be a Non-PO invoice report
        kpi_candidates.append({
            'name': 'Non-PO Invoice Count',
            'description': 'Number of Non-PO invoices in the report',
            'type': 'count',
            'value': len(df),
            'column': None,
            'format': 'number',
            'is_key_kpi': True
        })
    
    logger.info(f"Identified {len(kpi_candidates)} KPI candidates: {[kpi['name'] for kpi in kpi_candidates]}")
    return kpi_candidates

def generate_kpis(df, max_rows=50000, timeout_seconds=45, preferences=None):
    """
    Main function to generate KPIs from a dataframe with user preferences.
    
    Args:
        df: DataFrame to analyze
        max_rows: Maximum number of rows to process for performance
        timeout_seconds: Maximum time to spend generating KPIs
        preferences: Optional dictionary of user KPI preferences
        
    Returns:
        dict: Dictionary with KPIs and metadata
    """
    start_time = datetime.now()
    logger.info(f"Generating KPIs for dataframe with {len(df)} rows and {len(df.columns)} columns")
    
    # Set default preferences if none provided
    if preferences is None:
        preferences = {
            'financial_focus': True,
            'count_focus': True,
            'time_focus': True,
            'distribution_focus': True,
            'catalog_vs_free_text': True,
            'po_vs_non_po': True,
            'other_kpis': "",
            'selected_columns': list(df.columns)
        }
        
    # Filter the dataframe to only include selected columns if specified
    if 'selected_columns' in preferences and preferences['selected_columns']:
        selected_columns = preferences['selected_columns']
        # Make sure all selected columns exist in the dataframe
        valid_columns = [col for col in selected_columns if col in df.columns]
        
        if valid_columns:
            logger.info(f"Filtering dataframe to {len(valid_columns)} selected columns: {valid_columns}")
            analyzed_df = df[valid_columns].copy()
        else:
            # If no valid columns were selected, use all columns
            logger.warning("No valid columns were selected, using all columns")
            analyzed_df = df.copy()
    else:
        # If no columns were specified, use all columns
        analyzed_df = df.copy()
    
    # Sample the dataframe if it's too large
    if len(analyzed_df) > max_rows:
        logger.warning(f"Dataset has {len(analyzed_df)} rows, sampling {max_rows} rows for KPI generation")
        sample_df = analyzed_df.sample(max_rows, random_state=42)
        # Keep the total row count as a metric
        total_rows = len(analyzed_df)
    else:
        sample_df = analyzed_df
        total_rows = len(analyzed_df)
    
    try:
        # Analyze columns with timeout check
        column_types = analyze_columns(sample_df)
        
        # Check timeout after column analysis
        elapsed_time = (datetime.now() - start_time).total_seconds()
        if elapsed_time > timeout_seconds * 0.4:
            logger.warning(f"Column analysis took {elapsed_time:.2f} seconds, returning basic KPIs only")
            # Return basic KPIs with just record count
            basic_kpis = [{
                'name': 'Total Records',
                'value': total_rows,
                'type': 'count',
                'format': 'number',
                'is_key_kpi': True
            }]
            return {
                'key_metrics': basic_kpis,
                'count_metrics': basic_kpis,
                'financial_metrics': [],
                'quantity_metrics': [],
                'time_metrics': [],
                'distribution_metrics': [],
                'all_metrics': basic_kpis,
                'column_types': column_types
            }
        
        # Identify KPI candidates with timeout
        kpi_candidates = identify_kpi_candidates(sample_df, column_types)
        
        # Check timeout again
        elapsed_time = (datetime.now() - start_time).total_seconds()
        if elapsed_time > timeout_seconds * 0.8:
            logger.warning(f"KPI identification took {elapsed_time:.2f} seconds, returning limited KPIs")
            # Pick just a few basic metrics we've already calculated
            basic_kpis = [kpi for kpi in kpi_candidates if kpi['type'] in ['count', 'category_count']][:5]
            # Add the record count if it's not already there
            if not any(kpi['name'] == 'Total Records' for kpi in basic_kpis):
                basic_kpis.append({
                    'name': 'Total Records',
                    'value': total_rows,
                    'type': 'count',
                    'format': 'number',
                    'is_key_kpi': True
                })
            return {
                'key_metrics': basic_kpis,
                'count_metrics': basic_kpis,
                'financial_metrics': [],
                'quantity_metrics': [],
                'time_metrics': [],
                'distribution_metrics': [],
                'all_metrics': basic_kpis,
                'column_types': column_types
            }
        
        # Make sure we have the record count metric
        record_count_kpi = next(
            (kpi for kpi in kpi_candidates if kpi['name'] in ['Record Count', 'Total Records']), 
            None
        )
        if not record_count_kpi:
            kpi_candidates.append({
                'name': 'Total Records',
                'value': total_rows,
                'type': 'count',
                'format': 'number',
                'is_key_kpi': True
            })
        elif record_count_kpi and len(df) != len(sample_df):
            # Update record count to total, not just sampled count
            record_count_kpi['value'] = total_rows
        
        # Apply user preferences to filter KPIs
        filtered_candidates = []
        
        # Always include Record Count
        record_count_kpis = [kpi for kpi in kpi_candidates if kpi['name'] in ['Record Count', 'Total Records']]
        filtered_candidates.extend(record_count_kpis)
        
        # Apply user preferences
        for kpi in kpi_candidates:
            # Skip the record count since we already added it
            if kpi['name'] in ['Record Count', 'Total Records']:
                continue
                
            # Apply financial focus preference
            if preferences.get('financial_focus', True) and kpi['format'] == 'currency':
                filtered_candidates.append(kpi)
                
            # Apply count focus preference  
            elif preferences.get('count_focus', True) and kpi['type'] in ['count', 'category_count', 'sum'] and kpi['format'] == 'number':
                filtered_candidates.append(kpi)
                
            # Apply time focus preference
            elif preferences.get('time_focus', True) and kpi['type'] in ['date_range']:
                filtered_candidates.append(kpi)
                
            # Apply distribution focus preference  
            elif preferences.get('distribution_focus', True) and kpi['type'] in ['top_category']:
                filtered_candidates.append(kpi)
                
            # Apply catalog_vs_free_text preference
            elif preferences.get('catalog_vs_free_text', True) and 'catalog' in kpi['name'].lower():
                filtered_candidates.append(kpi)
                
            # Apply po_vs_non_po preference  
            elif preferences.get('po_vs_non_po', True) and ('po' in kpi['name'].lower() or 'invoice' in kpi['name'].lower()):
                filtered_candidates.append(kpi)
        
        # Add any additional specific KPIs based on user input
        if preferences.get('other_kpis'):
            additional_kpi_terms = [term.strip().lower() for term in preferences['other_kpis'].split(',')]
            for term in additional_kpi_terms:
                if term:
                    # Find any KPIs containing this term that we haven't already added
                    for kpi in kpi_candidates:
                        if (term in kpi['name'].lower() or 
                            (kpi.get('description') and term in kpi['description'].lower())):
                            if kpi not in filtered_candidates:
                                filtered_candidates.append(kpi)
        
        # Organize KPIs into categories
        kpis = {
            'key_metrics': [kpi for kpi in filtered_candidates if kpi.get('is_key_kpi', False)],
            'count_metrics': [kpi for kpi in filtered_candidates if kpi['type'] in ['count', 'category_count']],
            'financial_metrics': [kpi for kpi in filtered_candidates if kpi['type'] in ['sum', 'average'] and kpi['format'] == 'currency'],
            'quantity_metrics': [kpi for kpi in filtered_candidates if kpi['type'] in ['sum'] and kpi['format'] == 'number'],
            'time_metrics': [kpi for kpi in filtered_candidates if kpi['type'] in ['date_range']],
            'distribution_metrics': [kpi for kpi in filtered_candidates if kpi['type'] in ['top_category']],
            'all_metrics': filtered_candidates,
            'column_types': column_types
        }
        
        logger.info(f"Generated KPIs: {len(kpis['all_metrics'])} total, {len(kpis['key_metrics'])} key metrics in {(datetime.now() - start_time).total_seconds():.2f} seconds")
        return kpis
        
    except Exception as e:
        logger.error(f"Error generating KPIs: {str(e)}")
        # Return basic count KPI on error
        basic_kpi = {
            'name': 'Total Records',
            'value': total_rows,
            'type': 'count',
            'format': 'number',
            'is_key_kpi': True
        }
        return {
            'key_metrics': [basic_kpi],
            'count_metrics': [basic_kpi],
            'financial_metrics': [],
            'quantity_metrics': [],
            'time_metrics': [],
            'distribution_metrics': [],
            'all_metrics': [basic_kpi],
            'column_types': {'unknown': list(df.columns)}
        }

def format_kpi_value(kpi):
    """
    Format a KPI value based on its format type.
    
    Args:
        kpi: KPI dictionary with value and format
        
    Returns:
        str: Formatted value
    """
    if kpi['format'] == 'currency':
        return f"${kpi['value']:,.2f}"
    elif kpi['format'] == 'percentage':
        return f"{kpi['value']:.1f}%"
    elif kpi['format'] == 'number':
        return f"{kpi['value']:,}"
    elif kpi['format'] == 'days':
        return f"{kpi['value']} days"
    elif kpi['format'] == 'text':
        return str(kpi['value'])
    else:
        return str(kpi['value'])

def get_kpi_trend(kpi, previous_value=None):
    """
    Calculate the trend direction and percentage for a KPI.
    
    Args:
        kpi: Current KPI dictionary
        previous_value: Previous value to compare against (if available)
        
    Returns:
        dict: Trend information
    """
    if previous_value is None:
        return {'direction': 'neutral', 'percentage': 0}
    
    current = kpi['value']
    
    if current == previous_value:
        return {'direction': 'neutral', 'percentage': 0}
    
    # Calculate percentage change
    if previous_value != 0:
        pct_change = ((current - previous_value) / abs(previous_value)) * 100
    else:
        # If previous value was 0, use current value as percentage change
        pct_change = 100 if current > 0 else -100
    
    # Determine direction
    if kpi.get('is_positive_trend', True):
        # For most metrics, up is good (sales, revenue, etc.)
        direction = 'up' if current > previous_value else 'down'
        direction_label = 'positive' if current > previous_value else 'negative'
    else:
        # For metrics where down is good (costs, errors, etc.)
        direction = 'down' if current < previous_value else 'up'
        direction_label = 'positive' if current < previous_value else 'negative'
    
    return {
        'direction': direction,
        'direction_label': direction_label,
        'percentage': abs(pct_change)
    }