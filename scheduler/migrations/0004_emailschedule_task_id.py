# Generated by Django 5.1.1 on 2024-09-27 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0003_emailreminder_alter_emailschedule_reminder_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailschedule',
            name='task_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]