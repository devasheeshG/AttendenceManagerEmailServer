# Path: app/utils/email_client.py
# Description: Email service using Azure Communication Services.

import logging
from typing import Literal
from azure.communication.email import EmailClient
from azure.core.credentials import AzureKeyCredential
from app.config import get_settings
from app.logger import get_logger
from app.utils.models import AttendanceRecord

logger = get_logger()
settings = get_settings()

class EmailService:
    def __init__(self):
        credential = AzureKeyCredential(settings.ACS_KEY)
        self.client = EmailClient(settings.ACS_ENDPOINT, credential)
        self.admin_emails = settings.ADMIN_EMAILS.split(',')

    def send_email(self, to_email: str, subject: str, content: str):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                message = {
                    "senderAddress": settings.ACS_EMAIL,
                    "recipients": {
                        "to": [{"address": to_email}],
                    },
                    "content": {
                        "subject": subject,
                        "plainText": content,
                    }
                }

                poller = self.client.begin_send(message)
                result = poller.result()

                logger.info(f"Email sent successfully to {to_email}. Message ID: {result['id']}")
                break
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed to send email to {to_email}. Error: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} attempts failed to send email to {to_email}.")
                    # Optionally, you can raise the exception here if you want to handle it further up the call stack
                    # raise

    def send_attendance_notification(
        self, 
        name: str,
        email: str,
        notification_type: Literal['present', 'absent'],
        attendance_data: AttendanceRecord,
        change: int,
    ):
        # Compose the email content
        logger.info(f"Sending {notification_type} notification to {email}")

        subject = f"Attendance Notification: {attendance_data.subject_name}"
        if notification_type == 'present':
            
            content = (
                f"Hello, {name}\n\n"
                f"You have been marked present for {change} periods in {attendance_data.subject_name}.\n"
                f"Total Hours: {attendance_data.total_hours}\n"
                f"Present Hours: {attendance_data.present_hours}\n"
                f"Absent Hours: {attendance_data.absent_hours}\n"
                f"Percentage: {attendance_data.percentage}\n\n"
                # f"Change: +{change} hours"
            )
        
        else:
            content = (
                f"Hello, {name}\n\n"
                f"You have been marked absent for {change} periods in {attendance_data.subject_name}.\n"
                f"Total Hours: {attendance_data.total_hours}\n"
                f"Present Hours: {attendance_data.present_hours}\n"
                f"Absent Hours: {attendance_data.absent_hours}\n"
                f"Percentage: {attendance_data.percentage}\n\n"
                # f"Change: -{change} hours"
            )

        self.send_email(email, subject, content)
        logger.info(f"Notification sent successfully to {email}")

    def send_boot_notification(self):
        logger.info("Sending boot notification to admin users")

        subject = "Attendance Monitoring Service Started"
        content = (
            "Hello, Admin\n\n"
            "This is to notify you that the Attendance Monitoring Service has started successfully."
        )

        for admin_email in self.admin_emails:
            self.send_email(admin_email, subject, content)
        logger.info("Boot notification sent successfully to admin users")

    def send_error_notification(self, error_message: str, stack_trace: str):
        logger.info("Sending error notification to admin users")

        subject = "Error in Attendance Monitoring Service"
        content = (
            f"Hello, Admin\n\n"
            f"An error occurred in the Attendance Monitoring Service:\n\n"
            f"Error Message: {error_message}\n\n"
            f"Stack Trace:\n{stack_trace}"
        )

        for admin_email in self.admin_emails:
            self.send_email(admin_email, subject, content)
        logger.info("Error notification sent successfully to admin users")
