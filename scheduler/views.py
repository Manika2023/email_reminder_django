from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import logging
from .forms import EmailReminderFormSet, ReminderForm
from .models import EmailReminder, EmailSchedule
from .tasks import send_scheduled_email
import traceback
from django.http import HttpResponseForbidden
from django.contrib import messages
from celery import current_app
from celery.result import AsyncResult

# Set up logging for debugging
logger = logging.getLogger(__name__)

def email_reminder_view(request):
    """
    Handles the form submission for scheduling email reminders.
    Validates and schedules email tasks using Celery.
    """
    if request.method == 'POST':
        formset = EmailReminderFormSet(request.POST)
        if formset.is_valid():
            try:
                for form in formset:
                    if form.cleaned_data:
                        reminder = form.save()
                        email_schedule = EmailSchedule(reminder=reminder)
                        email_schedule.save()

                        scheduled_time = reminder.scheduled_time
                        if timezone.is_naive(scheduled_time):
                            scheduled_time = timezone.make_aware(scheduled_time)

                        now = timezone.now()
                        time_until_scheduled = (scheduled_time - now).total_seconds()

                        logger.debug(f"Current time: {now}")
                        logger.debug(f"Scheduled time: {scheduled_time}")
                        logger.debug(f"Time until scheduled: {time_until_scheduled} seconds")

                        # Schedule the email task using Celery
                        if time_until_scheduled > 0:
                            result = send_scheduled_email.apply_async(
                                args=[reminder.recipient_email, reminder.message, email_schedule.id],
                                countdown=time_until_scheduled  # Use countdown to delay the task
                            )
                            email_schedule.task_id = result.id  # Store the task ID
                        else:
                            result = send_scheduled_email.apply_async(
                                args=[reminder.recipient_email, reminder.message, email_schedule.id]
                            )
                            email_schedule.task_id = result.id  # Store the task ID
                            logger.warning(f"Scheduled time {scheduled_time} has already passed. Sending email immediately.")

                        email_schedule.save()  # Save the schedule with the task ID

                # Redirect to the success page after processing
                return redirect('email_success')  # Ensure this matches your urls.py

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

def update_reminder_view(request, pk):
    """
    Updates an existing email reminder and schedules a new email task.
    Cancels the previous email task if it exists.
    """
    # Get the EmailReminder object by primary key (pk)
    reminder = get_object_or_404(EmailReminder, id=pk)
    email_schedule = EmailSchedule.objects.get(reminder=reminder)

    if request.method == 'POST':
        # Bind the submitted form data to the ReminderForm
        form = ReminderForm(request.POST, instance=reminder)
        
        if form.is_valid():
            # Revoke the previous task if it exists
            if email_schedule.task_id:
                current_app.control.revoke(email_schedule.task_id, terminate=True)

            # Save the updated reminder
            form.save()
            messages.success(request, 'Reminder updated successfully!')

            # Create a new scheduled email task
            new_task = send_scheduled_email.apply_async(
                (reminder.recipient_email, reminder.message, email_schedule.id),
                eta=reminder.scheduled_time
            )
            # Update the task_id in EmailSchedule
            email_schedule.task_id = new_task.id
            email_schedule.save()

            return redirect('email_status')  # Redirect to the status page or any other desired page
        else:
            messages.error(request, 'Failed to update the reminder. Please correct the errors.')

    # If the request method is GET, bind the existing reminder to the form
    form = ReminderForm(instance=reminder)
    return render(request, 'scheduler/update_reminder.html', {'form': form})

# View to cancel an email task
# View to cancel an email task
def cancel_email_task(request, task_id):
    try:
        # Get the EmailSchedule object using the task_id
        email_schedule = EmailSchedule.objects.get(task_id=task_id)
        
        # Check if the scheduled time is in the past
        if email_schedule.reminder.scheduled_time < timezone.now():
            messages.warning(request, "This email task cannot be canceled because the scheduled time has already passed.")
        else:
            current_app.control.revoke(task_id, terminate=True)  # Terminate the task
            messages.success(request, "The scheduled email has been successfully canceled.")
    
    except EmailSchedule.DoesNotExist:
        messages.error(request, "The email task could not be found. It may have already been sent or does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred while trying to cancel the email task: {str(e)}")
    
    return redirect('email_status')  # Redirect to your desired status page


# Delete a reminder (for both sent and unsent reminders)
def delete_reminder_view(request, pk):
    """
    Delete a reminder regardless of its status (sent or not sent).
    """
    reminder = get_object_or_404(EmailReminder, pk=pk)
    schedule = EmailSchedule.objects.get(reminder=reminder)

    if request.method == 'POST':
        reminder.delete()  # Deleting the reminder will cascade delete the schedule
        messages.success(request, 'Reminder deleted successfully!')
        return redirect('email_status')  # Redirect to the status page
    return render(request, 'scheduler/delete_reminder.html', {'reminder': reminder, 'schedule': schedule})
