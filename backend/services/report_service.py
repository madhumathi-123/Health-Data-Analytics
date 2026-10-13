"""
Report Generation Service
Generates PDF and Excel reports for inventory, outbreaks, and usage
"""
import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.data_utils import (
    get_all_medicines, get_low_stock_medicines,
    get_all_predictions, get_all_orders
)
from config import Config

class ReportService:
    """Service for generating reports"""
    
    def __init__(self):
        self.reports_dir = Config.REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_inventory_report_pdf(self, filename=None):
        """Generate PDF report for inventory"""
        if not filename:
            filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        filepath = os.path.join(self.reports_dir, filename)
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        title = Paragraph("Medicine Inventory Report", title_style)
        elements.append(title)
        
        # Date
        date_text = Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Normal']
        )
        elements.append(date_text)
        elements.append(Spacer(1, 0.3*inch))
        
        # Get data
        medicines = get_all_medicines()
        
        # Summary statistics
        total_medicines = len(medicines)
        total_value = sum(m['current_stock'] * m['unit_price'] for m in medicines)
        low_stock = len([m for m in medicines if m['current_stock'] < m['reorder_level']])
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Medicines', str(total_medicines)],
            ['Total Inventory Value', f'₹{total_value:,.2f}'],
            ['Low Stock Items', str(low_stock)]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Medicine details
        elements.append(Paragraph("Medicine Details", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Create table data
        table_data = [['Medicine', 'Disease', 'Stock', 'Reorder Level', 'Unit Price', 'Status']]
        
        for med in medicines[:20]:  # Limit to 20 for PDF
            status = 'Low' if med['current_stock'] < med['reorder_level'] else 'OK'
            table_data.append([
                med['medicine_name'][:20],
                med['disease_name'][:15],
                str(med['current_stock']),
                str(med['reorder_level']),
                f"₹{med['unit_price']:.2f}",
                status
            ])
        
        medicine_table = Table(table_data, colWidths=[1.5*inch, 1.3*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.6*inch])
        medicine_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        
        elements.append(medicine_table)
        
        # Build PDF
        doc.build(elements)
        
        print(f"✅ Inventory report generated: {filepath}")
        return filepath
    
    def generate_inventory_report_excel(self, filename=None):
        """Generate Excel report for inventory"""
        if not filename:
            filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = os.path.join(self.reports_dir, filename)
        
        # Get data
        medicines = get_all_medicines()
        
        # Convert to DataFrame
        df = pd.DataFrame(medicines)
        
        # Select and rename columns
        df = df[[
            'medicine_name', 'disease_name', 'current_stock', 'reorder_level',
            'unit_price', 'supplier_name', 'expiry_date', 'batch_number'
        ]]
        
        df.columns = [
            'Medicine', 'Disease', 'Current Stock', 'Reorder Level',
            'Unit Price (₹)', 'Supplier', 'Expiry Date', 'Batch Number'
        ]
        
        # Add status column
        df['Status'] = df.apply(
            lambda row: 'Low Stock' if row['Current Stock'] < row['Reorder Level'] else 'Adequate',
            axis=1
        )
        
        # Calculate total value
        df['Total Value (₹)'] = df['Current Stock'] * df['Unit Price (₹)']
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Write main data
            df.to_excel(writer, sheet_name='Inventory', index=False)
            
            # Write summary
            summary_df = pd.DataFrame({
                'Metric': ['Total Medicines', 'Total Inventory Value', 'Low Stock Items'],
                'Value': [
                    len(df),
                    f"₹{df['Total Value (₹)'].sum():,.2f}",
                    len(df[df['Status'] == 'Low Stock'])
                ]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"✅ Inventory Excel report generated: {filepath}")
        return filepath
    
    def generate_outbreak_report_pdf(self, filename=None):
        """Generate PDF report for outbreak predictions"""
        if not filename:
            filename = f"outbreak_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        filepath = os.path.join(self.reports_dir, filename)
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph("Outbreak Prediction Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Get predictions
        predictions = get_all_predictions()
        
        # Summary
        high_risk = len([p for p in predictions if p['probability'] >= 0.7])
        
        summary_text = f"""
        <b>Total Predictions:</b> {len(predictions)}<br/>
        <b>High Risk (≥70%):</b> {high_risk}<br/>
        <b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Predictions table
        table_data = [['Disease', 'Location', 'Date', 'Probability', 'Severity', 'Cases']]
        
        for pred in predictions[:15]:  # Limit to 15
            table_data.append([
                pred['disease_name'][:15],
                f"{pred['location'][:12]}, {pred['state'][:10]}",
                pred['predicted_date'],
                f"{pred['probability']*100:.1f}%",
                pred['severity_level'],
                str(pred['predicted_cases'])
            ])
        
        pred_table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 0.9*inch, 0.9*inch, 0.7*inch])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d32f2f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        
        elements.append(pred_table)
        
        # Build PDF
        doc.build(elements)
        
        print(f"✅ Outbreak report generated: {filepath}")
        return filepath
    
    def generate_orders_report_excel(self, filename=None):
        """Generate Excel report for orders"""
        if not filename:
            filename = f"orders_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = os.path.join(self.reports_dir, filename)
        
        # Get data
        orders = get_all_orders()
        
        # Convert to DataFrame
        df = pd.DataFrame(orders)
        
        # Select columns
        df = df[[
            'order_id', 'medicine_name', 'supplier_name', 'quantity',
            'order_date', 'expected_delivery', 'status', 'total_cost'
        ]]
        
        df.columns = [
            'Order ID', 'Medicine', 'Supplier', 'Quantity',
            'Order Date', 'Expected Delivery', 'Status', 'Total Cost (₹)'
        ]
        
        # Write to Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Orders', index=False)
        
        print(f"✅ Orders Excel report generated: {filepath}")
        return filepath


# Standalone functions
def generate_all_reports():
    """Generate all reports"""
    service = ReportService()
    
    print("\n📊 Generating all reports...")
    
    service.generate_inventory_report_pdf()
    service.generate_inventory_report_excel()
    service.generate_outbreak_report_pdf()
    service.generate_orders_report_excel()
    
    print("\n✅ All reports generated successfully!")


if __name__ == '__main__':
    if '--generate' in sys.argv:
        generate_all_reports()
    else:
        print("Usage: python report_service.py --generate")
