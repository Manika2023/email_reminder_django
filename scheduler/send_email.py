from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

def send_reminder_email(to_email, subject, message):
    """
    Function to send an email reminder to the specified email address.

    Parameters:
    - to_email: Email address to send the reminder.
    - subject: Subject of the email.
    - message: Content of the email.
    """
    try:
        send_mail(
            subject,  # Subject
            message,  # Message
            settings.DEFAULT_FROM_EMAIL,  # From email
            [to_email],  # To email(s)
            fail_silently=False,  # Fail loudly for debugging purposes
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False