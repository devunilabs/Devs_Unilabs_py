from celery import shared_task
import os
import datetime as dt
from django.utils import timezone as tz

# Django
from django.conf import settings

# Models
from modules.report.models import UnilabsReport, Tracking


@shared_task()
def removes():
    date_init =  tz.now().date() - dt.timedelta(days=30)
    data = UnilabsReport.objects.filter(created__lte=date_init).values_list('file', flat=True)
    
    if data:
        for file in data:
            file_path = "{0}/{1}".format(settings.MEDIA_ROOT, file)
            
            if file and os.path.exists(file_path):
                os.remove(file_path)
            
                # remove row
                UnilabsReport.objects.filter(file=file).delete()
