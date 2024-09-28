from django.contrib import admin

# Register your models here.
from .models import EmailReminder

@admin.register(EmailReminder)
class EmailAdmin(admin.ModelAdmin):
     list_display=['id']