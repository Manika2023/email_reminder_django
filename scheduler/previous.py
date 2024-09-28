from django.shortcuts import render, redirect
from .forms import EmailReminderFormSet
from django.core.mail import send_mail
from django.conf import settings
import schedule
import time
import threading
from .models import EmailReminder, EmailSchedule
from .tasks import send_scheduled_email
from django.utils import timezone
from .email_sender import send_scheduled_email  # Separate function for sending email
import schedule
import threading
import time

# Function to run the schedule in a background thread
def run_schedule():
    while True:
        schedule.run_pending()  # Check for pending tasks
        time.sleep(60)  # Check every 60 seconds

# Start the scheduler thread (run it only once when the server starts)
threading.Thread(target=run_schedule, daemon=True).start()

# View for creating email reminders
def email_reminder_view(request):
    if request.method == 'POST':
        formset = EmailReminderFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    reminder = form.save()

                    # Schedule the email to be sent at the specified time
                    schedule_email_task(reminder.recipient_email, reminder.message, reminder.scheduled_time)

            return redirect('email_success')
    else:
        formset = EmailReminderFormSet(queryset=EmailReminder.objects.none())

    return render(request, 'scheduler/email_reminder.html', {'formset': formset})

# Success view after emails are scheduled
def email_success_view(request):
    return render(request, 'scheduler/email_success.html')

# Schedule the email to be sent at a specific time
def schedule_email_task(recipient_email, message, scheduled_time):
    """
    Schedules an email to be sent at the specified time using the schedule library.
    
    Parameters:
    - recipient_email: The email address of the recipient.
    - message: The message content to be sent in the email.
    - scheduled_time: The time when the email should be sent.
    """
    # Calculate the time in "%H:%M" format for the schedule library
    scheduled_time_str = scheduled_time.strftime("%H:%M")
    
    # Schedule the email to be sent daily at the specified time
    schedule.every().day.at(scheduled_time_str).do(send_scheduled_email, recipient_email, message)

# View for the success page after setting reminders
def email_success_view(request):
    """
    Displays a success message after email reminders are set.
    
    Parameters:
    - request: The HTTP request object.
    
    Returns:
    - Rendered HTML page indicating success.
    """
    return render(request, 'scheduler/email_success.html')  # Render success page



from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings
import logging
from .forms import EmailReminderFormSet
from .models import EmailReminder, EmailSchedule
from .tasks import send_scheduled_email
import traceback

# Set up logging for debugging
logger = logging.getLogger(__name__)

def email_reminder_view(request):
    if request.method == 'POST':
        formset = EmailReminderFormSet(request.POST)
        if formset.is_valid():
            try:
                for form in formset:
                    if form.cleaned_data:
                        reminder = form.save()

                        # Create a new EmailSchedule entry
                        email_schedule = EmailSchedule(reminder=reminder)
                        email_schedule.save()

                        # Make sure the scheduled time is timezone-aware
                        scheduled_time = reminder.scheduled_time
                        if timezone.is_naive(scheduled_time):
                            scheduled_time = timezone.make_aware(scheduled_time)

                        # Get the current time
                        now = timezone.now()

                        # Calculate the time delay in seconds
                        time_until_scheduled = (scheduled_time - now).total_seconds()

                        # Log the time details for debugging
                        logger.debug(f"Current time: {now}")
                        logger.debug(f"Scheduled time: {scheduled_time}")
                        logger.debug(f"Time until scheduled: {time_until_scheduled} seconds")

                        # Schedule the email task using Celery
                        if time_until_scheduled > 0:
                            send_scheduled_email.apply_async(
                                args=[reminder.recipient_email, reminder.message],
                                countdown=time_until_scheduled
                            )
                            logger.info(f"Email scheduled for {reminder.recipient_email} in {time_until_scheduled} seconds.")
                        else:
                            # send_scheduled_email.apply_async(
                            #     args=[reminder.recipient_email, reminder.message]
                            # )
#                             send_scheduled_email.apply_async(
#     args=[reminder.recipient_email, reminder.message, email_schedule.id],
#     countdown=time_until_scheduled
# )
                            if time_until_scheduled > 0:
    # Schedule the task for a future time using the countdown
                                send_scheduled_email.apply_async(
        args=[reminder.recipient_email, reminder.message, email_schedule.id],
        countdown=time_until_scheduled
    )    
                            logger.warning(f"Scheduled time {scheduled_time} has already passed. Sending email immediately.")

                return redirect('email_success')  # Redirect to success page

            except Exception as e:
                logger.error(f"Error while processing email reminders: {str(e)}")
                logger.debug(traceback.format_exc())
        else:
            logger.warning("Invalid form data")
    else:
        formset = EmailReminderFormSet(queryset=EmailReminder.objects.none())

    return render(request, 'scheduler/email_reminder.html', {'formset': formset})

def email_success_view(request):
    """
    Displays a success message after email reminders are set.
    """
    return render(request, 'scheduler/email_success.html')
def email_status_view(request):
    """
    Displays the status of email reminders.
    """
    schedules = EmailSchedule.objects.all()
    now = timezone.now()  # Get the current time for comparison
    return render(request, 'scheduler/email_status.html', {'schedules': schedules, 'now': now})