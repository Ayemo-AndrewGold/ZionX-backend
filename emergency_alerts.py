"""Emergency alert system for notifying emergency contacts via email."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from users import get_emergency_contacts, has_emergency_consent


def send_emergency_alert(username: str, alert_data: dict) -> tuple[bool, str]:
    """Send emergency alerts to user's emergency contacts.
    
    Args:
        username: Username of the user in distress
        alert_data: Dict with 'severity', 'symptoms', 'ai_assessment', 'user_location'
    
    Returns:
        (success: bool, message: str)
    """
    # Check consent
    if not has_emergency_consent(username):
        return False, "User has not given consent for emergency alerts"
    
    contacts = get_emergency_contacts(username)
    
    # Collect email addresses
    emails_to_notify = []
    
    if contacts.get("doctor", {}).get("email"):
        emails_to_notify.append({
            "email": contacts["doctor"]["email"],
            "name": contacts["doctor"].get("name", "Doctor"),
            "type": "doctor"
        })
    
    for loved_one in contacts.get("loved_ones", []):
        if loved_one.get("email"):
            emails_to_notify.append({
                "email": loved_one["email"],
                "name": loved_one.get("name", "Emergency Contact"),
                "type": "loved_one"
            })
    
    if not emails_to_notify:
        return False, "No emergency contact emails configured"
    
    # Send emails
    sent_count = 0
    for contact in emails_to_notify:
        success = _send_email(
            to_email=contact["email"],
            to_name=contact["name"],
            username=username,
            alert_data=alert_data,
            contact_type=contact["type"]
        )
        if success:
            sent_count += 1
    
    if sent_count > 0:
        return True, f"Emergency alert sent to {sent_count} contact(s)"
    else:
        return False, "Failed to send emergency alerts"


def _send_email(to_email: str, to_name: str, username: str, alert_data: dict, contact_type: str) -> bool:
    """Send individual emergency email.
    
    Returns:
        bool indicating success
    """
    # Email configuration from environment variables
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Email credentials not configured (SMTP_EMAIL, SMTP_PASSWORD)")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"⚠️ URGENT: Health Alert for {username}"
        msg["From"] = f"ZionX Health Alert <{sender_email}>"
        msg["To"] = to_email
        
        # Email body
        severity = alert_data.get("severity", "high")
        symptoms = alert_data.get("symptoms", "Not specified")
        ai_assessment = alert_data.get("ai_assessment", "User requires immediate medical attention")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        location = alert_data.get("user_location", "Not provided")
        
        text_body = f"""
URGENT HEALTH ALERT

Dear {to_name},

This is an automated emergency alert from ZionX Health Platform.

User: {username}
Timestamp: {timestamp}
Severity Level: {severity.upper()}

REPORTED SYMPTOMS:
{symptoms}

AI HEALTH ASSESSMENT:
{ai_assessment}

LOCATION: {location}

{'As their designated doctor, please review this case immediately.' if contact_type == 'doctor' else 'As their emergency contact, please check on them as soon as possible.'}

This alert was sent because {username} has given prior consent to notify you in emergency situations.

If this is a life-threatening emergency, please call emergency services (911 or local equivalent) immediately.

---
ZionX Health Platform
Automated Emergency Alert System
"""
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 3px solid #dc2626; border-radius: 10px; background-color: #fef2f2;">
        <h2 style="color: #dc2626; margin-top: 0;">⚠️ URGENT HEALTH ALERT</h2>
        
        <p>Dear <strong>{to_name}</strong>,</p>
        
        <p>This is an automated emergency alert from <strong>ZionX Health Platform</strong>.</p>
        
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; font-weight: bold;">User:</td>
                    <td style="padding: 8px;">{username}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Timestamp:</td>
                    <td style="padding: 8px;">{timestamp}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Severity:</td>
                    <td style="padding: 8px;"><span style="background: #dc2626; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{severity.upper()}</span></td>
                </tr>
            </table>
        </div>
        
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h3 style="margin-top: 0; color: #dc2626;">Reported Symptoms:</h3>
            <p>{symptoms}</p>
        </div>
        
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h3 style="margin-top: 0; color: #dc2626;">AI Health Assessment:</h3>
            <p>{ai_assessment}</p>
        </div>
        
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h3 style="margin-top: 0;">Location:</h3>
            <p>{location if location != 'Not provided' else '<em>Not provided</em>'}</p>
        </div>
        
        <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 15px 0;">
            <p style="margin: 0; font-weight: bold;">
                {'📋 As their designated doctor, please review this case immediately.' if contact_type == 'doctor' else '❤️ As their emergency contact, please check on them as soon as possible.'}
            </p>
        </div>
        
        <p style="font-size: 12px; color: #666; margin-top: 20px;">
            This alert was sent because {username} has given prior consent to notify you in emergency situations.
        </p>
        
        <div style="background: #fee2e2; border: 1px solid #dc2626; padding: 10px; border-radius: 5px; margin-top: 15px;">
            <p style="margin: 0; color: #dc2626; font-weight: bold;">
                ⚡ If this is a life-threatening emergency, please call emergency services (911 or local equivalent) immediately.
            </p>
        </div>
        
        <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
        
        <p style="font-size: 11px; color: #999; text-align: center; margin-bottom: 0;">
            ZionX Health Platform<br>
            Automated Emergency Alert System
        </p>
    </div>
</body>
</html>
"""
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"Emergency alert sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False


def should_trigger_emergency_alert(risk_level: str, urgency: str) -> bool:
    """Determine if emergency alert should be sent based on AI assessment.
    
    Args:
        risk_level: 'low', 'medium', 'high', or 'critical'
        urgency: 'monitor', 'schedule_visit', 'seek_urgent_care', or 'call_emergency'
    
    Returns:
        bool indicating if alert should be triggered
    """
    # Trigger on critical risk or emergency urgency
    return risk_level == "critical" or urgency == "call_emergency"
