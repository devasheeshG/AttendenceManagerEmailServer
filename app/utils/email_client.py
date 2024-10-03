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

    def send_email(self, to_email: str, subject: str, content: str):
        try:
            message = {
                "senderAddress": settings.AZURE_SENDER_EMAIL,
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

            logger.info(f"Email sent successfully to {to_email}. Message ID: {result.message_id}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}. Error: {str(e)}")
            raise

    def send_attendance_notification(
        self, 
        to_email: str,
        type: Literal['present', 'absent'],
        data: AttendanceRecord,
    ):
        # Compose the email content
        pass
