import os
from typing import cast
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "VeggieVault.settings")
app = Celery("VeggieVault")
app = cast(Celery, app)

app.conf.beat_schedule = {
    'say-hello-task':{
        'task':'base.tasks.say_hello_task',
        'schedule': crontab(minute='*')
        }
    }

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

#intervel based tasks
"""
schedule, _ = IntervalSchedule.objects.get_or_create(
   every=10,
   period=IntervalSchedule.SECONDS,
)
PeriodicTask.objects.create(
   interval=schedule,
   name='Import contacts every 10s',
   task='proj.tasks.import_contacts',
)
"""
#crontab tasks
"""from django_celery_beat.models import CrontabSchedule, PeriodicTask
import zoneinfo
schedule, _ = CrontabSchedule.objects.get_or_create(
   minute='30',
   hour='*',
   day_of_week='*',
   day_of_month='*',
   month_of_year='*',
   timezone=zoneinfo.ZoneInfo('UTC')
)
PeriodicTask.objects.create(
   crontab=schedule,
   name='Import contacts hourly at :30',
   task='proj.tasks.import_contacts',
)"""
