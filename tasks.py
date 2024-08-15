from django.conf import settings
import django
import os
#os.environ['DJANGO_SETTINGS_MODULE'] =
django.setup()
import dramatiq
import json, requests
from requests.exceptions import Timeout


def should_retry(retries_so_far, exception):
	return retries_so_far


@dramatiq.actor(max_age=3600000, retry_when=should_retry)
def task_one(data):
    return