"""
Notification Service
Handles email notifications and in-app alerts for outbreak predictions and inventory alerts
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import Config
from utils.data_utils import (
    create_notification, get_pending_notifications, 
    mark_notification_sent, get_prediction_by_id,
    get_medicine_by_id
)

class NotificationService:
    """Service for sending notifications"""
    
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.smtp_email = Config.SMTP_EMAIL
        self.smtp_password = Config.SMTP_PASSWORD
        self.alert_recipients = Config.ALERT_EMAIL_RECIPIENTS
    
    def send_email(self, to_emails, subject, body, html_body=None):
        """
        Send email notification
        
        Args:
            to_emails: list of recipient emails or comma-separated string
            subject: email subject
            body: plain text body
            html_body: HTML body (optional)
        
        Returns:
            bool: True if sent successfully
        """
        try:
            # Parse recipients
            if isinstance(to_emails, str):
                to_emails = [email.strip() for email in to_emails.split(',')]
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Add plain text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            return False
    
    def send_outbreak_alert(self, prediction_id):
        """
        Send outbreak alert notification
        
        Args:
            prediction_id: ID of the outbreak prediction
        """
        prediction = get_prediction_by_id(prediction_id)
        if not prediction:
            return False
        
        # Create email content
        subject = f"🚨 URGENT: Predicted {prediction['disease_name']} Outbreak Alert"
        
        body = f"""
OUTBREAK ALERT - ACTION REQUIRED

Dear Healthcare Team,

Our AI-powered prediction system has detected a high-risk disease outbreak:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTBREAK DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Disease:           {prediction['disease_name']}
Location:          {prediction['location']}, {prediction['state']}
Predicted Date:    {prediction['predicted_date']}
Outbreak Probability: {prediction['probability'] * 100:.1f}%
Severity Level:    {prediction['severity_level']}
Expected Cases:    {prediction['predicted_cases']}
Risk Score:        {prediction['risk_score']:.1f}/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Review current medicine inventory for {prediction['disease_name']}
2. Check stock levels and place orders if necessary
3. Prepare medical facilities in the affected region
4. Coordinate with local health authorities
5. Monitor the situation closely

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please log in to the dashboard for detailed information and to take action.

Dashboard: http://localhost:3000/dashboard

This is an automated alert from the Outbreak-Linked Smart Drug Inventory System.
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
Healthcare AI System
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .alert-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
        .details {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
        .label {{ font-weight: bold; color: #666; }}
        .value {{ color: #333; }}
        .severity-high {{ color: #dc3545; font-weight: bold; }}
        .severity-critical {{ color: #d32f2f; font-weight: bold; }}
        .actions {{ background: #e3f2fd; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .actions h3 {{ color: #1976d2; margin-top: 0; }}
        .actions ul {{ padding-left: 20px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; 
                   text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 OUTBREAK ALERT</h1>
            <p>High-Risk Disease Outbreak Detected</p>
        </div>
        <div class="content">
            <div class="alert-box">
                <strong>⚠️ ACTION REQUIRED:</strong> Our AI system has identified a potential outbreak that requires immediate attention.
            </div>
            
            <div class="details">
                <h2>Outbreak Details</h2>
                <div class="detail-row">
                    <span class="label">Disease:</span>
                    <span class="value">{prediction['disease_name']}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Location:</span>
                    <span class="value">{prediction['location']}, {prediction['state']}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Predicted Date:</span>
                    <span class="value">{prediction['predicted_date']}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Probability:</span>
                    <span class="value">{prediction['probability'] * 100:.1f}%</span>
                </div>
                <div class="detail-row">
                    <span class="label">Severity:</span>
                    <span class="value severity-{prediction['severity_level'].lower()}">{prediction['severity_level']}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Expected Cases:</span>
                    <span class="value">{prediction['predicted_cases']}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Risk Score:</span>
                    <span class="value">{prediction['risk_score']:.1f}/100</span>
                </div>
            </div>
            
            <div class="actions">
                <h3>📋 Recommended Actions</h3>
                <ul>
                    <li>Review current medicine inventory for {prediction['disease_name']}</li>
                    <li>Check stock levels and place orders if necessary</li>
                    <li>Prepare medical facilities in the affected region</li>
                    <li>Coordinate with local health authorities</li>
                    <li>Monitor the situation closely</li>
                </ul>
            </div>
            
            <center>
                <a href="http://localhost:3000/dashboard" class="button">View Dashboard</a>
            </center>
            
            <div class="footer">
                <p>This is an automated alert from the Outbreak-Linked Smart Drug Inventory System.</p>
                <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        # Send email
        success = self.send_email(self.alert_recipients, subject, body, html_body)
        
        if success:
            # Create notification record
            create_notification(
                prediction_id=prediction_id,
                notification_type='outbreak_alert',
                title=f"Outbreak Alert: {prediction['disease_name']}",
                message=f"High-risk outbreak predicted in {prediction['location']}",
                sent_to=','.join(self.alert_recipients),
                priority='high'
            )
        
        return success
    
    def send_low_stock_alert(self, medicine_id):
        """
        Send low stock alert notification
        
        Args:
            medicine_id: ID of the medicine with low stock
        """
        medicine = get_medicine_by_id(medicine_id)
        if not medicine:
            return False
        
        subject = f"⚠️ Low Stock Alert: {medicine['medicine_name']}"
        
        body = f"""
LOW STOCK ALERT

Medicine: {medicine['medicine_name']}
Disease: {medicine['disease_name']}
Current Stock: {medicine['current_stock']} units
Reorder Level: {medicine['reorder_level']} units
Supplier: {medicine['supplier_name']}

Action Required: Place order to replenish stock.

Log in to the dashboard to create an order.

Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        success = self.send_email(self.alert_recipients, subject, body)
        
        if success:
            create_notification(
                prediction_id=None,
                notification_type='low_stock',
                title=f"Low Stock: {medicine['medicine_name']}",
                message=f"Current stock ({medicine['current_stock']}) below reorder level ({medicine['reorder_level']})",
                sent_to=','.join(self.alert_recipients),
                priority='medium'
            )
        
        return success
    
    def send_order_update(self, order_id, status, recipient_email):
        """
        Send order status update notification
        
        Args:
            order_id: ID of the order
            status: New order status
            recipient_email: Email of recipient
        """
        subject = f"Order Update: Order #{order_id} - {status.upper()}"
        
        body = f"""
ORDER STATUS UPDATE

Order ID: #{order_id}
New Status: {status.upper()}
Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Log in to the dashboard for more details.

Best regards,
Healthcare Inventory System
        """
        
        return self.send_email([recipient_email], subject, body)
    
    def process_pending_notifications(self):
        """Process all pending notifications"""
        pending = get_pending_notifications()
        
        for notification in pending:
            # Mark as sent (even if email fails, to avoid infinite retries)
            mark_notification_sent(notification['notification_id'])
            
            print(f"Processed notification #{notification['notification_id']}: {notification['title']}")
        
        return len(pending)


# Standalone functions for easy import
def send_outbreak_alert(prediction_id):
    """Send outbreak alert"""
    service = NotificationService()
    return service.send_outbreak_alert(prediction_id)

def send_low_stock_alert(medicine_id):
    """Send low stock alert"""
    service = NotificationService()
    return service.send_low_stock_alert(medicine_id)

def send_order_update(order_id, status, recipient_email):
    """Send order update"""
    service = NotificationService()
    return service.send_order_update(order_id, status, recipient_email)


if __name__ == '__main__':
    # Test notification service
    print("Testing Notification Service...")
    service = NotificationService()
    print("✅ Notification service initialized")
