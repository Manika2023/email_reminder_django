from django import forms
from .models import EmailReminder
from django.forms import modelformset_factory

class ReminderForm(forms.ModelForm):
    class Meta:
        model = EmailReminder
        fields = ['recipient_email', 'message', 'scheduled_time']
        widgets = {
            'recipient_email': forms.EmailInput(attrs={
                'class': 'border border-gray-300 rounded p-2 w-full',
                'placeholder': 'Enter recipient email',
                'required':True
            }),
            'message': forms.Textarea(attrs={
                'class': 'border border-gray-300 rounded p-2 w-full',
                'placeholder': 'Enter your message',
                'rows': 3,
                'required':True
                
            }),
            'scheduled_time': forms.DateTimeInput(attrs={
                'class': 'border border-gray-300 rounded p-2 w-full',
                'type': 'datetime-local',
                'required':True
            }),
        }

    # # Set fields as required
    # def __init__(self, *args, **kwargs):
    #     super(ReminderForm, self).__init__(*args, **kwargs)
    #     self.fields['recipient_email'].required = True
    #     self.fields['message'].required = True
    #     self.fields['scheduled_time'].required = True
    #  # Ensure form validation works
    # def clean(self):
    #     cleaned_data = super().clean()
    #     recipient_email = cleaned_data.get("recipient_email")
    #     message = cleaned_data.get("message")
    #     scheduled_time = cleaned_data.get("scheduled_time")

    #     if not recipient_email or not message or not scheduled_time:
    #         raise forms.ValidationError("All fields are required.")
    #     return cleaned_data   
     
# EmailReminderFormSet is intended to handle multiple forms at once, allowing the user to submit multiple reminders in one go.
# Here, extra=1 means one blank form will always be rendered. 
EmailReminderFormSet = modelformset_factory(EmailReminder, form=ReminderForm, extra=1)
