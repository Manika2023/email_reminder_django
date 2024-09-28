from django.db import models
class EmailReminder(models.Model):
    recipient_email = models.EmailField(blank=False, null=False)
    message = models.TextField(blank=False, null=False)
    scheduled_time = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        return f"Reminder for {self.recipient_email} on {self.scheduled_time}"
    
class EmailSchedule(models.Model):
    reminder = models.ForeignKey(EmailReminder, on_delete=models.CASCADE)
    is_sent = models.BooleanField(default=False)
    task_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

