from . import views
from django.urls import path,include

urlpatterns = [
     path('', views.email_reminder_view, name='email_reminder'),
    path('success/', views.email_success_view, name='email_success'),
     path('status/', views.email_status_view, name='email_status'),
    path('reminder/update/<int:pk>/', views.update_reminder_view, name='update_reminder'),
    path('reminder/delete/<int:pk>/', views.delete_reminder_view, name='delete_reminder'),
    path('cancel-task/<str:task_id>/', views.cancel_email_task, name='cancel_email_task'),

]
