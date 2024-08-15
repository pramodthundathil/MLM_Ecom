# Home/tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def update_user_designations():
    call_command('update_designations')
