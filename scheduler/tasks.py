from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging
import traceback
from .models import EmailSchedule

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def send_scheduled_email(recipient_email, message, schedule_id):
    print(f"Received: {recipient_email}, {message}, {schedule_id}")
    try:
        # Logic to send the email
        send_mail(
           subject='Scheduled Reminder',  # Subject of the email
            message=message,               # Body of the email
            from_email=settings.EMAIL_HOST_USER,  # Sender's email address
            recipient_list=[recipient_email],     # Recipient email
            fail_silently=False,    # Raise exceptions if any errors
        )
        # If email sent successfully, update the EmailSchedule entry
        email_schedule = EmailSchedule.objects.get(id=schedule_id)
        # print(schedule_id)
        email_schedule.is_sent = True
        email_schedule.save()

        return f"Email successfully sent to {recipient_email}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
