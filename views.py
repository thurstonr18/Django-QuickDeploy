from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpRequest
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.db.models import Case, When, IntegerField, CharField, Value
from django.contrib.staticfiles.urls import static
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User  
from django.http import StreamingHttpResponse 
from django.core.serializers.json import DjangoJSONEncoder
import os, sys, re, json, time
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.decorators import login_required
import requests
from decimal import Decimal
import base64
import subprocess
import time


def index(request):
	if request.method == 'GET':
		return render(request, 'content/index.html')
