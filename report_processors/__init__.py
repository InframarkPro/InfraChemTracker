"""
Report Processors Package

This package contains specialized processors for various report formats.
Each processor handles the specific structure and format of its associated report type,
standardizing the data for analysis within the application.
"""

from .chemical_spend_by_supplier import process_chemical_spend_by_supplier_report

# Export available processors
__all__ = [
    'process_chemical_spend_by_supplier_report'
]

# Note: Supplier unit cost processors have been removed as requested