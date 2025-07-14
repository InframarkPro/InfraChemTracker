# Chemical Spend Dashboard

## Overview

This is a Streamlit-based web application for analyzing chemical spend data across different suppliers, regions, and departments. The application provides interactive dashboards and visualizations for tracking chemical costs, supplier performance, and purchase order analytics in water treatment facilities.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web interface
- **Styling**: Custom CSS themes (Matrix, Monograph, Industrial themes)
- **Visualizations**: Plotly for interactive charts and graphs
- **UI Components**: Custom ShadCN-inspired components for enhanced user experience

### Backend Architecture
- **Language**: Python 3.11+
- **Data Processing**: Pandas for data manipulation and analysis
- **File Processing**: Support for CSV and Excel files (including XML-based Excel formats)
- **Session Management**: Streamlit session state for maintaining user data and preferences
- **Authentication**: Custom authentication system with user management

### Data Storage Solutions
- **File Storage**: Local filesystem with CSV/pickle serialization
- **Database**: SQLite for persistent data storage
- **Session Data**: In-memory storage using Streamlit session state
- **Report Management**: Unified database system for storing and retrieving uploaded reports

## Key Components

### Data Processing Pipeline
1. **File Upload Handler**: Processes CSV and Excel files with multiple encoding support
2. **Report Type Detection**: Automatically identifies report types (PO Line Detail, Non-PO Invoice, Chemical Spend by Supplier)
3. **Data Standardization**: Converts different report formats into unified schemas
4. **Validation**: Ensures data integrity and format compliance

### Dashboard System
- **Chemical Spend Dashboard**: Primary analysis interface for supplier and chemical cost analysis
- **Customized Dashboard**: Enhanced metrics and KPI tracking
- **Trend Analysis**: Historical data comparison and trend visualization
- **Interactive Analysis**: Drill-down capabilities for detailed insights

### Report Processors
- **Chemical Spend by Supplier**: Processes NetSuite chemical spend reports
- **PO Line Detail**: Handles purchase order line item analysis
- **Non-PO Invoice**: Manages non-purchase order invoice data

### Visualization Engine
- **Chart Theming**: Consistent styling across all visualizations
- **Interactive Charts**: Plotly-based charts with drill-down functionality
- **Export Capabilities**: CSV and PDF export functionality
- **Responsive Design**: Mobile-friendly dashboard layouts

## Data Flow

1. **File Upload** → **Format Detection** → **Data Processing** → **Validation**
2. **Processed Data** → **Database Storage** → **Session State** → **Dashboard Rendering**
3. **User Interactions** → **Filter Application** → **Chart Updates** → **Export Generation**

## External Dependencies

### Core Libraries
- `streamlit`: Web application framework
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive visualization library
- `openpyxl`: Excel file processing
- `sqlite3`: Database operations
- `numpy`: Numerical computing

### File Processing
- `xlrd`: Excel 2003 XML format support
- `toml`: Configuration file parsing
- `io`: File stream handling

### Authentication & Security
- `json`: User data serialization
- `logging`: Application logging and debugging

## Deployment Strategy

### Local Development
- Run using `streamlit run app.py`
- SQLite database for local data persistence
- File-based session management
- Development logging enabled

### Production Considerations
- Database migration scripts for persistence fixes
- Error handling and graceful degradation
- Theme preference persistence
- User authentication and session management

### Configuration
- Theme settings stored in `.streamlit/theme_preference.txt`
- Custom CSS in `.streamlit/custom.css`
- Dashboard configurations in `dashboard_configs/` directory

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 01, 2025. Initial setup