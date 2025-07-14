"""
Run Database Fixes

This script should be run at application startup to ensure all 
database connections are properly configured for persistence.
"""
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_all_fixes():
    """Run all database fixes"""
    try:
        # Fix supplier pricing database
        from utils.fix_supplier_pricing_persistence import fix_persistence
        fix_persistence()
        
        logger.info("All database fixes completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error running database fixes: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_all_fixes()
    sys.exit(0 if success else 1)