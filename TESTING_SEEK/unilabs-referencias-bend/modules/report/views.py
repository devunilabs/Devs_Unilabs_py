from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets

# Django
import requests
import io as BytesIO
import base64
from django.conf import settings
from urllib import parse
from django.http import HttpResponse

# Models