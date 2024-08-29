from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
    StreamingHttpResponse,
    HttpRequest
)
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import (
    Case,
    When,
    IntegerField,
    CharField,
    Value,
    Q
)
from django.contrib.staticfiles.urls import static
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

import os
import sys
import re
import json
import time
from datetime import datetime
from decimal import Decimal
import base64
import subprocess


def index(request):
    if request.method == 'GET':
        return render(request, 'content/index.html')
