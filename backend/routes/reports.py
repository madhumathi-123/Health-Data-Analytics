"""
Reports Routes
Handles report generation and download
"""
from flask import Blueprint, request, jsonify, send_file
from utils.auth_utils import token_required, log_action
from services.report_service import ReportService
import os

reports_bp = Blueprint('reports', __name__)

# Initialize report service
report_service = ReportService()

@reports_bp.route('/inventory', methods=['GET'])
@token_required
def generate_inventory_report(current_user):
    """Generate inventory report"""
    format_type = request.args.get('format', 'pdf')  # pdf or excel
    
    try:
        if format_type == 'excel':
            filepath = report_service.generate_inventory_report_excel()
        else:
            filepath = report_service.generate_inventory_report_pdf()
        
        # Log action
        log_action(current_user['user_id'], 'generate_report', 'reports',
                  details=f"Inventory report ({format_type})")
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/outbreak-history', methods=['GET'])
@token_required
def generate_outbreak_report(current_user):
    """Generate outbreak history report"""
    try:
        filepath = report_service.generate_outbreak_report_pdf()
        
        # Log action
        log_action(current_user['user_id'], 'generate_report', 'reports',
                  details="Outbreak history report")
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/orders', methods=['GET'])
@token_required
def generate_orders_report(current_user):
    """Generate orders report"""
    try:
        filepath = report_service.generate_orders_report_excel()
        
        # Log action
        log_action(current_user['user_id'], 'generate_report', 'reports',
                  details="Orders report")
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/generate-all', methods=['POST'])
@token_required
def generate_all_reports(current_user):
    """Generate all reports"""
    try:
        report_service.generate_inventory_report_pdf()
        report_service.generate_inventory_report_excel()
        report_service.generate_outbreak_report_pdf()
        report_service.generate_orders_report_excel()
        
        # Log action
        log_action(current_user['user_id'], 'generate_report', 'reports',
                  details="All reports generated")
        
        return jsonify({
            'message': 'All reports generated successfully',
            'reports_dir': report_service.reports_dir
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
