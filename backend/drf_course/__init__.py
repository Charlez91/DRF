from .celery import app as celery_app

__all__ = ("celery_app",)#to enable shared_task to use app on app startup