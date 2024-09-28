from django.core.mail import send_mail
from django.conf import settings

# Function to send an email
def send_scheduled_email(recipient_email, message):
    """
    Sends an email to the specified recipient with the provided message.
    
    Parameters:
    - recipient_email: The email address of the recipient.
    - message: The message content to be sent in the email.
    """
    send_mail(
        'Scheduled Reminder',  # Subject of the email
        message,  # Body of the email
        settings.EMAIL_HOST_USER,  # Sender's email address (configured in settings)
        [recipient_email],  # List of recipient email addresses
        fail_silently=False,  # If True, suppress errors; else raise exceptions
    )
    print(f"Email sent to {recipient_email}")  # Print confirmation in console
