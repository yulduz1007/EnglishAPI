from .celery import app as celery_app

__all__ = ("celery_app",)
# https://realpython.com/asynchronous-tasks-with-django-and-celery/