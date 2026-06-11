from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

# Email configuration via environment variables
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'info@zynch.ai')
TO_EMAIL = os.environ.get('TO_EMAIL', 'info@zynch.ai')

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    try:
        data = request.get_json()
        form_type = data.get('formType', 'message')
        
        # Build email subject
        subject = f"New {form_type.title()} Request from {data.get('firstName', '')} {data.get('lastName', '')}"
        
        # Build email body
        body = f"""
New {form_type.title()} Form Submission
========================================

Contact Information:
- Name: {data.get('firstName', '')} {data.get('lastName', '')}
- Email: {data.get('email', '')}
- Phone: {data.get('phone', 'Not provided')}
- Company: {data.get('company', 'Not provided')}
- Title: {data.get('title', 'Not provided')}

Form Type: {form_type.title()}

"""
        
        if form_type == 'message':
            body += f"Subject: {data.get('subject', 'Not specified')}\n\nMessage:\n{data.get('message', '')}"
        else:
            body += f"Company Size: {data.get('companySize', 'Not specified')}\n"
            body += f"Meeting Type: {data.get('meetingType', 'Not specified')}\n"
            body += f"Preferred Date: {data.get('preferredDate', 'Not specified')}\n"
            body += f"Message: {data.get('message', '')}"
        
        # Send email via SMTP
        if SMTP_USERNAME and SMTP_PASSWORD:
            msg = MIMEMultipart()
            msg['From'] = FROM_EMAIL
            msg['To'] = TO_EMAIL
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            
            return jsonify({'success': True, 'message': 'Email sent successfully'}), 200
        else:
            print(f"Email would be sent to {TO_EMAIL}:")
            print(subject)
            print(body)
            return jsonify({'success': True, 'message': 'Email logged (SMTP not configured)'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def serve():
    with open('index.html', 'r') as f:
        return f.read()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    app.run(host='0.0.0.0', port=port)