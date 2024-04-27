import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_course.settings') 

app = Celery('drf_course')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY') 

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

#was added in the official celery documentation. dnt feel its important though.
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')