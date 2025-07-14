"""
PDF Export Utility Module

This module provides functions for exporting dashboard metrics and visualizations to PDF.
"""

import os
import io
import base64
import datetime
import tempfile
import logging
from typing import List, Dict, Optional, Tuple, Union

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.graph_objs import Figure
# matplotlib not needed
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.platypus.flowables import KeepTogether
from reportlab.pdfgen import canvas

# Define theme colors
def get_theme_colors():
    """Get theme colors for visualizations"""
    return {
        'primary': '#00ff00',  # Matrix green
        'secondary': '#111111',
        'accent': '#ffffff',
        'background': '#000000',
        'text': '#00ff00'
    }

# Configure logging
logger = logging.getLogger(__name__)

# Create 'reports' directory if it doesn't exist
if not os.path.exists('reports'):
    os.makedirs('reports')

def format_currency(value):
    """Format value as currency"""
    if pd.isna(value):
        return "$0.00"
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)

def format_percentage(value):
    """Format value as percentage"""
    if pd.isna(value):
        return "0.0%"
    try:
        return f"{float(value):.1f}%"
    except (ValueError, TypeError):
        return str(value)

def format_number(value):
    """Format numeric value with comma separators"""
    if pd.isna(value):
        return "0"
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)

def get_report_stylesheet():
    """
    Create and return stylesheet for PDF reports with custom styles
    """
    stylesheet = getSampleStyleSheet()
    
    # Add custom title style
    stylesheet.add(
        ParagraphStyle(
            name='CustomTitle',
            parent=stylesheet['Title'],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.darkblue,
        )
    )
    
    # Add custom heading style
    stylesheet.add(
        ParagraphStyle(
            name='CustomHeading',
            parent=stylesheet['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkblue,
        )
    )
    
    # Add custom normal text style
    stylesheet.add(
        ParagraphStyle(
            name='CustomNormal',
            parent=stylesheet['Normal'],
            fontSize=10,
            spaceAfter=8,
        )
    )
    
    # Add date/footer style
    stylesheet.add(
        ParagraphStyle(
            name='Footer',
            parent=stylesheet['Normal'],
            fontSize=8,
            textColor=colors.gray,
        )
    )
    
    return stylesheet

def fig_to_image(fig: Figure, width: int = 600, height: int = 400) -> Image:
    """
    Convert a Plotly figure to a ReportLab Image object
    
    Args:
        fig: Plotly figure to convert
        width: Width of the image in pixels
        height: Height of the image in pixels
        
    Returns:
        ReportLab Image object
    """
    try:
        # Try to use kaleido first (faster and better quality)
        img_bytes = fig.to_image(format="png", width=width, height=height)
        img_io = io.BytesIO(img_bytes)
        return Image(img_io, width=7*inch, height=4*inch)
    except Exception as e:
        # If kaleido is not available, create a placeholder image with a message
        logger.warning(f"Unable to generate plot image: {str(e)}")
        
        # Create a simple placeholder image with reportlab
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(width, height))
        
        # Gray background
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(0, 0, width, height, fill=1)
        
        # Add text explaining the issue
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width/2, height/2, "Chart image unavailable")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height/2 - 20, "Kaleido package required for chart export")
        c.drawCentredString(width/2, height/2 - 40, "Please install: pip install -U kaleido")
        
        c.save()
        buffer.seek(0)
        
        return Image(buffer, width=7*inch, height=4*inch)

def dataframe_to_table(df: pd.DataFrame, max_rows: int = 20) -> Table:
    """
    Convert a pandas DataFrame to a ReportLab Table object
    
    Args:
        df: DataFrame to convert
        max_rows: Maximum number of rows to include
        
    Returns:
        ReportLab Table object
    """
    # Truncate if necessary
    if len(df) > max_rows:
        df = df.head(max_rows)
        has_more = True
    else:
        has_more = False
    
    # Make table more horizontal by shortening column names if needed
    if len(df.columns) > 6:
        # Shorten column names if they're too long
        shortened_columns = []
        for col in df.columns:
            if len(str(col)) > 15:
                shortened_columns.append(str(col)[:12] + '...')
            else:
                shortened_columns.append(str(col))
        df.columns = shortened_columns
    
    # Convert DataFrame to a list of lists
    data = [list(df.columns)]
    for i, row in df.iterrows():
        row_data = []
        for val in row:
            # Limit cell content length to prevent overflow
            if isinstance(val, str) and len(val) > 30:
                row_data.append(val[:27] + '...')
            else:
                row_data.append(val)
        data.append(row_data)
        
    # Add note about truncated data
    if has_more:
        data.append([f"Showing {max_rows} of {len(df)} rows"] + [""] * (len(df.columns) - 1))
    
    # Calculate column widths to fit page
    available_width = 7.5 * inch  # Available width on letter page with margins
    col_width = min(1.5 * inch, available_width / len(df.columns))
    col_widths = [col_width] * len(df.columns)
    
    # Create table with calculated widths
    table = Table(data, colWidths=col_widths)
    
    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),  # Slightly smaller header font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),  # Smaller font for content
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Middle align all content
        ('WORDWRAP', (0, 0), (-1, -1), 1),  # Enable word wrapping
    ])
    
    # Add alternating row colors
    for row in range(1, len(data)):
        if row % 2 == 0:
            style.add('BACKGROUND', (0, row), (-1, row), colors.whitesmoke)
    
    table.setStyle(style)
    return table

def add_page_number(canvas, doc):
    """
    Add page number to each page
    """
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(
        doc.pagesize[0] - 0.5*inch, 0.5*inch, text
    )
    
    # Add date on left side
    today = datetime.datetime.now().strftime("%B %d, %Y")
    canvas.drawString(
        0.5*inch, 0.5*inch, f"Generated on: {today}"
    )
    
    # Add company name in center
    canvas.drawCentredString(
        doc.pagesize[0] / 2, 0.5*inch, "Chemical Dashboard Export"
    )
    
    canvas.restoreState()

def create_dashboard_pdf(
    title: str,
    metrics: Dict[str, Union[str, float, int]],
    charts: List[Figure],
    tables: Optional[List[pd.DataFrame]] = None,
    filename: Optional[str] = None,
    selected_sections: Optional[List[str]] = None
) -> str:
    """
    Create a PDF report with dashboard metrics and charts
    
    Args:
        title: Report title
        metrics: Dictionary of metrics to include in the report
        charts: List of Plotly figures to include
        tables: Optional list of pandas DataFrames to include
        filename: Optional filename for the report (default: auto-generated)
        selected_sections: Optional list of section names to include (for selective export)
        
    Returns:
        Path to the generated PDF file
    """
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() else "_" for c in title)
        filename = f"reports/dashboard_{safe_title}_{timestamp}.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )
    
    # Get stylesheet
    stylesheet = get_report_stylesheet()
    
    # Create document elements
    elements = []
    
    # Add title
    elements.append(Paragraph(title, stylesheet['CustomTitle']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add report date
    report_date = datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")
    elements.append(Paragraph(f"Generated on: {report_date}", stylesheet['Footer']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add metrics summary section
    if not selected_sections or 'metrics' in selected_sections:
        elements.append(Paragraph("Key Metrics", stylesheet['CustomHeading']))
        
        # Convert metrics to a more readable format with two columns of metrics
        metrics_data = []
        metrics_list = []
        
        # Process metrics values
        for key, value in metrics.items():
            if isinstance(value, float) and abs(value) < 1:
                # Format as percentage if small float
                formatted_value = format_percentage(value * 100)
            elif isinstance(value, float) or isinstance(value, int):
                # Format as currency if it contains any currency keywords
                if any(kw in key.lower() for kw in ['cost', 'spend', 'price', '$', 'dollar', 'amount']):
                    formatted_value = format_currency(value)
                else:
                    formatted_value = format_number(value)
            else:
                formatted_value = str(value)
                
            metrics_list.append((key, formatted_value))
        
        # Arrange metrics in two columns if there are enough metrics
        if len(metrics_list) > 5:
            # Calculate number of rows needed
            half_count = len(metrics_list) // 2 + (1 if len(metrics_list) % 2 != 0 else 0)
            
            # Create rows for the two-column layout
            for i in range(half_count):
                row = []
                # First column
                row.extend([metrics_list[i][0], metrics_list[i][1]])
                
                # Second column (if available)
                if i + half_count < len(metrics_list):
                    row.extend([metrics_list[i + half_count][0], metrics_list[i + half_count][1]])
                else:
                    row.extend(['', ''])  # Empty cells for alignment
                    
                metrics_data.append(row)
                
            # Create a table with the 2x2 column layout
            col_widths = [2.5*inch, 1.25*inch, 2.5*inch, 1.25*inch]
            metrics_table = Table(metrics_data, colWidths=col_widths)
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
        else:
            # Use the original single column layout for fewer metrics
            for key, formatted_value in metrics_list:
                metrics_data.append([key, formatted_value])
                
            metrics_table = Table(metrics_data, colWidths=[5*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.25*inch))
    
    # Add charts
    if charts and (not selected_sections or 'charts' in selected_sections):
        elements.append(Paragraph("Visualizations", stylesheet['CustomHeading']))
        
        for i, fig in enumerate(charts):
            try:
                # Convert Plotly figure to image and add to PDF
                img = fig_to_image(fig)
                elements.append(img)
                elements.append(Spacer(1, 0.25*inch))
                
                # Add page break after every 2 charts except for the last one
                if (i + 1) % 2 == 0 and i < len(charts) - 1:
                    elements.append(PageBreak())
            except Exception as e:
                logger.error(f"Error adding chart to PDF: {str(e)}")
                # Add text about error
                elements.append(
                    Paragraph(f"Error including visualization #{i+1}: {str(e)}", stylesheet['CustomNormal'])
                )
    
    # Add tables
    if tables and (not selected_sections or 'tables' in selected_sections):
        elements.append(Paragraph("Data Tables", stylesheet['CustomHeading']))
        
        for i, df in enumerate(tables):
            try:
                # Convert DataFrame to table and add to PDF
                table = dataframe_to_table(df)
                elements.append(KeepTogether([
                    Paragraph(f"Table {i+1}", stylesheet['CustomNormal']),
                    table,
                    Spacer(1, 0.1*inch)
                ]))
                
                # Add page break after each table except for the last one
                if i < len(tables) - 1:
                    elements.append(PageBreak())
            except Exception as e:
                logger.error(f"Error adding table to PDF: {str(e)}")
                # Add text about error
                elements.append(
                    Paragraph(f"Error including table #{i+1}: {str(e)}", stylesheet['CustomNormal'])
                )
    
    # Build the PDF document
    try:
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
        logger.info(f"PDF report successfully created: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error building PDF document: {str(e)}")
        raise

def export_to_pdf_button(
    title: str,
    metrics: Dict[str, Union[str, float, int]],
    charts: List[Figure],
    tables: Optional[List[pd.DataFrame]] = None,
    key: str = "export_pdf",
    label: str = "Export to PDF",
    include_timestamp: bool = True,
    allow_section_selection: bool = True
) -> Optional[str]:
    """
    Create an export to PDF button in Streamlit
    
    Args:
        title: Report title
        metrics: Dictionary of metrics to include in the report
        charts: List of Plotly figures to include
        tables: Optional list of pandas DataFrames to include
        key: Unique key for the Streamlit components
        label: Label for the export button
        include_timestamp: Whether to include timestamp in filename
        allow_section_selection: Whether to allow selecting specific sections to export
        
    Returns:
        Path to the generated PDF file if button was clicked, otherwise None
    """
    # Define available sections
    sections = ["metrics", "charts", "tables"]
    selected_sections = sections.copy()
    
    # Selection widget for report sections if enabled
    if allow_section_selection:
        with st.expander("PDF Export Options", expanded=False):
            selected_sections = st.multiselect(
                "Select sections to include in the PDF report:",
                options=sections,
                default=sections,
                format_func=lambda x: x.capitalize(),
                key=f"{key}_sections"
            )
    
    # Export button
    if st.button(label, key=key):
        try:
            with st.spinner("Generating PDF report..."):
                # Generate PDF file
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
                safe_title = "".join(c if c.isalnum() else "_" for c in title)
                filename = f"reports/dashboard_{safe_title}{f'_{timestamp}' if timestamp else ''}.pdf"
                
                # Create PDF with selected sections
                pdf_path = create_dashboard_pdf(
                    title=title,
                    metrics=metrics,
                    charts=charts,
                    tables=tables,
                    filename=filename,
                    selected_sections=selected_sections if allow_section_selection else None
                )
                
                # Create download link
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                    
                b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
                download_filename = os.path.basename(pdf_path)
                
                # Display success message with download link
                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{download_filename}">Click here to download the PDF report</a>'
                st.success("PDF report successfully generated!")
                st.markdown(href, unsafe_allow_html=True)
                
                return pdf_path
        except Exception as e:
            st.error(f"Error generating PDF report: {str(e)}")
            logger.error(f"PDF export error: {str(e)}", exc_info=True)
            return None
    
    return None

def export_multiple_views_to_pdf(
    views: Dict[str, Dict],
    title: str = "Dashboard Report",
    key: str = "multi_export_pdf"
) -> Optional[str]:
    """
    Create a comprehensive PDF with multiple dashboard views/sections
    
    Args:
        views: Dictionary where keys are view names and values are dictionaries with:
              - 'metrics': Dict of metrics for this view
              - 'charts': List of Plotly figures for this view
              - 'tables': Optional list of pandas DataFrames for this view
        title: Overall report title
        key: Unique key for Streamlit components
        
    Returns:
        Path to the generated PDF file if button was clicked, otherwise None
    """
    # Define selection widget for views to include
    available_views = list(views.keys())
    selected_views = available_views.copy()
    
    with st.expander("Comprehensive PDF Export Options", expanded=False):
        selected_views = st.multiselect(
            "Select dashboard views/sections to include in the PDF report:",
            options=available_views,
            default=available_views,
            key=f"{key}_views"
        )
        
        include_toc = st.checkbox("Include table of contents", value=True, key=f"{key}_toc")
    
    # Export button
    if st.button("Export Complete Dashboard to PDF", key=key):
        try:
            with st.spinner("Generating comprehensive PDF report..."):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = "".join(c if c.isalnum() else "_" for c in title)
                filename = f"reports/{safe_title}_{timestamp}.pdf"
                
                # Create PDF document
                doc = SimpleDocTemplate(
                    filename,
                    pagesize=letter,
                    rightMargin=0.5*inch,
                    leftMargin=0.5*inch,
                    topMargin=0.75*inch,
                    bottomMargin=0.75*inch,
                )
                
                # Get stylesheet
                stylesheet = get_report_stylesheet()
                
                # Create document elements
                elements = []
                
                # Add title
                elements.append(Paragraph(title, stylesheet['CustomTitle']))
                elements.append(Spacer(1, 0.25*inch))
                
                # Add report date
                report_date = datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")
                elements.append(Paragraph(f"Generated on: {report_date}", stylesheet['Footer']))
                elements.append(Spacer(1, 0.25*inch))
                
                # Add table of contents if requested
                if include_toc and selected_views:
                    elements.append(Paragraph("Table of Contents", stylesheet['CustomHeading']))
                    toc_data = [[f"{i+1}. {view}"] for i, view in enumerate(selected_views)]
                    toc_table = Table(toc_data, colWidths=[6*inch])
                    toc_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    elements.append(toc_table)
                    elements.append(PageBreak())
                
                # Add each selected view
                for i, view_name in enumerate(selected_views):
                    if view_name in views:
                        view_data = views[view_name]
                        
                        # Add section title
                        elements.append(Paragraph(f"{i+1}. {view_name}", stylesheet['CustomTitle']))
                        elements.append(Spacer(1, 0.25*inch))
                        
                        # Add metrics
                        if 'metrics' in view_data and view_data['metrics']:
                            elements.append(Paragraph("Key Metrics", stylesheet['CustomHeading']))
                            
                            metrics_data = []
                            for key, value in view_data['metrics'].items():
                                if isinstance(value, float) and abs(value) < 1:
                                    formatted_value = format_percentage(value * 100)
                                elif isinstance(value, float) or isinstance(value, int):
                                    if any(kw in key.lower() for kw in ['cost', 'spend', 'price', '$', 'dollar', 'amount']):
                                        formatted_value = format_currency(value)
                                    else:
                                        formatted_value = format_number(value)
                                else:
                                    formatted_value = str(value)
                                    
                                metrics_data.append([key, formatted_value])
                            
                            metrics_table = Table(metrics_data, colWidths=[4*inch, 2*inch])
                            metrics_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                ('TOPPADDING', (0, 0), (-1, -1), 6),
                            ]))
                            
                            elements.append(metrics_table)
                            elements.append(Spacer(1, 0.25*inch))
                        
                        # Add charts
                        if 'charts' in view_data and view_data['charts']:
                            elements.append(Paragraph("Visualizations", stylesheet['CustomHeading']))
                            
                            for j, fig in enumerate(view_data['charts']):
                                try:
                                    img = fig_to_image(fig)
                                    elements.append(img)
                                    elements.append(Spacer(1, 0.25*inch))
                                    
                                    # Add page break after charts
                                    if j < len(view_data['charts']) - 1:
                                        elements.append(PageBreak())
                                except Exception as e:
                                    logger.error(f"Error adding chart to PDF: {str(e)}")
                                    elements.append(
                                        Paragraph(f"Error including visualization #{j+1}: {str(e)}", stylesheet['CustomNormal'])
                                    )
                        
                        # Add tables
                        if 'tables' in view_data and view_data['tables']:
                            elements.append(Paragraph("Data Tables", stylesheet['CustomHeading']))
                            
                            for j, df in enumerate(view_data['tables']):
                                try:
                                    table = dataframe_to_table(df)
                                    elements.append(KeepTogether([
                                        Paragraph(f"Table {j+1}", stylesheet['CustomNormal']),
                                        table,
                                        Spacer(1, 0.1*inch)
                                    ]))
                                    
                                    # Add page break after tables
                                    if j < len(view_data['tables']) - 1:
                                        elements.append(PageBreak())
                                except Exception as e:
                                    logger.error(f"Error adding table to PDF: {str(e)}")
                                    elements.append(
                                        Paragraph(f"Error including table #{j+1}: {str(e)}", stylesheet['CustomNormal'])
                                    )
                        
                        # Add page break between sections
                        if i < len(selected_views) - 1:
                            elements.append(PageBreak())
                
                # Build the PDF document
                doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
                logger.info(f"Comprehensive PDF report successfully created: {filename}")
                
                # Create download link
                with open(filename, "rb") as f:
                    pdf_bytes = f.read()
                    
                b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
                download_filename = os.path.basename(filename)
                
                # Display success message with download link
                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{download_filename}">Click here to download the comprehensive PDF report</a>'
                st.success("Comprehensive PDF report successfully generated!")
                st.markdown(href, unsafe_allow_html=True)
                
                return filename
                
        except Exception as e:
            st.error(f"Error generating comprehensive PDF report: {str(e)}")
            logger.error(f"Comprehensive PDF export error: {str(e)}", exc_info=True)
            return None
    
    return None

def capture_metrics_and_charts():
    """
    Capture the currently displayed metrics and charts in Streamlit
    for later export to PDF.
    
    Note: This is a placeholder function. The actual implementation would be more complex
    as Streamlit doesn't directly provide a way to capture rendered elements.
    """
    st.warning("This is a placeholder function. Actual implementation would require " +
               "restructuring the dashboard code to collect metrics and charts for export.")