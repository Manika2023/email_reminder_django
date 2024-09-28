from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_reminder.settings')

# Create Celery app instance
app = Celery('email_reminder')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks
app.autodiscover_tasks()

# Force Windows to use the 'fork' method instead of 'spawn' for starting workers
if os.name == 'nt':
    app.conf.update(
        worker_pool='eventlet'
    )
