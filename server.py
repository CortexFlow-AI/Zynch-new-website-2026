from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr, make_msgid
import os
from datetime import datetime

app = Flask(__name__)

# Email configuration via environment variables
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
TO_EMAIL = os.environ.get('TO_EMAIL', 'info@zynch.ai')

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    try:
        data = request.get_json()
        form_type = data.get('formType', 'message')
        
        # Get submitter's info
        submitter_name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
        submitter_email = data.get('email', '')
        
        # Build email subject
        subject = f"Website Contact: {submitter_name} - {data.get('subject', form_type.title())}"
        
        # Build email body with clear formatting
        body = f"""ZYNCH.AI WEBSITE CONTACT FORM
{'='*50}

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Form Type: {form_type.title()}

CONTACTOR INFORMATION
--------------------
Name: {submitter_name}
Email: {submitter_email}
Phone: {data.get('phone', 'Not provided')}
Company: {data.get('company', 'Not provided')}
Job Title: {data.get('jobTitle', 'Not provided')}

"""
        
        if form_type == 'message':
            body += f"""MESSAGE DETAILS
--------------
Subject: {data.get('subject', 'Not specified')}

Message:
{data.get('message', 'No message provided')}

"""
        else:
            body += f"""MEETING REQUEST
--------------
Company Size: {data.get('companySize', 'Not specified')}
Meeting Type: {data.get('meetingType', 'Not specified')}
Preferred Date: {data.get('preferredDate', 'Not specified')}
Additional Notes: {data.get('message', 'None')}

"""
        
        body += """---
This email was sent from the Zynch.ai website contact form.
To reply to this inquiry, click Reply (the sender is the system email).
"""
        
        # Send email via SMTP with proper headers
        if SMTP_USERNAME and SMTP_PASSWORD:
            msg = MIMEMultipart()
            msg['From'] = formataddr((str(Header('Zynch.ai Website', 'utf-8')), SMTP_USERNAME))
            msg['To'] = TO_EMAIL
            msg['Reply-To'] = formataddr((str(Header(submitter_name, 'utf-8')), submitter_email))
            msg['Subject'] = Header(subject, 'utf-8')
            msg['X-Priority'] = '1'
            msg['X-Mailer'] = 'Zynch.ai Contact Form'
            
            # Add unique Message-ID to prevent threading/archiving issues
            msg['Message-ID'] = make_msgid(domain='zynch.ai')
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send with separate Envelope from for proper delivery
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_USERNAME, [TO_EMAIL], msg.as_string())
            
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