import requests
from django.conf import settings
from modules.luggage.models import Test
from datetime import datetime
from utils.util_json import is_json

# Django
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

# Models
from modules.information.models import Emails
from modules.luggage.models import LuggageAvailableCode, LuggageDetail

# Python
import json


def run(luggage, details, request):

    year = datetime.today().strftime('%y')[1]
    month = datetime.today().strftime('%m')
    day = datetime.today().strftime('%d')
    i = 0
    range_codes = LuggageAvailableCode.objects.values('start', 'end').first()

    payloads_email = []
    fecha = datetime.today().strftime('%Y-%m-%d')

    """ Patients """

    for detail in details:
        i = i+1
        next_code = correlative(i, range_codes)
        pruebas = []
        comments = []

        code = "5{0}{1}{2}".format(month, day, next_code)
        tests = Test.objects.filter(patient=detail.patient, luggage=detail.luggage)

        """ Test's by patient"""
        for test in tests:
            if test.comment:
                comments.append("{0}: {1} ".format(test.code, test.comment))
            pruebas.append({"codigo": test.code})

        payload = {
            "operation": {
                "valor": "peticiones",
                "origen": "app_referencias",
                "items": [{
                    "analisis": code,
                    "fecha": datetime.today().strftime('%Y%m%d'),
                    "dni": detail.patient.document,
                    "nombres": detail.patient.name if detail.patient.name else '',
                    "ape1": detail.patient.first_surname if detail.patient.first_surname else '',
                    "ape2": detail.patient.last_surname if detail.patient.last_surname else '',
                    "fnac": detail.patient.date_birth.strftime('%Y%m%d'),
                    "sexo": detail.patient.gender,
                    "comen_ana": ", ".join(str(x) for x in comments),
                    "comen_pac": "Valija: {0}".format(luggage.id),
                    "demo0": luggage.id,
                    "demo1": luggage.reference.code,
                    "demo2": "",
                    "demo3": "1",
                    "demo4": code,
                    "demo5": "A",
                    "demo6": "",
                    "demo7": "",
                    "demo8": "R",
                    "demo9": "",
                    "extra0": detail.patient.mobile_number,
                    "extra1": "",
                    "extra2": "",
                    "extra3": "",
                    "extra4": "",
                    "pruebas": pruebas
                }]
            }
        }

        response = requests.post(settings.API_INTEGRATION, auth=(settings.USER_INTEGRATION, settings.PASS_INTEGRATION),
                                 json=payload)
        status = valid(response)

        """ Update detail """
        detail.response_integration = response.text
        detail.body_integration = json.dumps(payload)
        detail.code = code
        detail.sent = status
        detail.save()

        """ Send email """
        if not status:
            data = payload['operation']['items']
            data[0]['pruebas'] = []
            test_temp = []

            for test in tests:
                test_temp.append("{0}: {1} | ".format(test.name, test.comment))
            data[0]['pruebas'].append(test_temp)
            payloads_email.append(data[0])

    data = Emails.objects.first()
    if data and payloads_email:
        mail = EmailMultiAlternatives(
            subject=data.subject,
            bcc=tuple(data.emails.split(',')),
            body=render_to_string("emails/error_integration.html",
                                  {"payload": payloads_email,
                                   "luggage": luggage,
                                   "fecha": fecha
                                   })
        )
        mail.content_subtype = 'html'
        mail.send()

    """ Save luggage """
    luggage.date_completed = datetime.now()
    luggage.status = 'completed'
    luggage.sent = True if len(payloads_email) == 0 else False
    luggage.save()
    return True


def resend(detail):
    try:
        body = detail.body_integration
        response = requests.post(settings.API_INTEGRATION, auth=(settings.USER_INTEGRATION, settings.PASS_INTEGRATION),
                                json=json.loads(body))
        status = valid(response)
        detail.response_integration = response.text
        detail.sent = status
        detail.save()
        return status
    except Exception as e:
        return False

def valid(response):
    status = True
    if response.status_code != 200:
        status = False

    if not is_json(response):
        status = False

    if status:
        if response.json()['status']['valor'] == 'NO':
            status = False
    return status


def correlative(i, range_codes):
    today = datetime.now().strftime('%Y-%m-%d')

    last_code = LuggageDetail.objects \
        .filter(luggage__status='completed', luggage__date_completed__range=[today + ' 00:00:00', today + ' 23:59:59']) \
        .values('code').order_by('-code').first()
    if last_code:
        next_correlative = (int(last_code['code'][5:] or 0) + i)
    else:
        if range_codes:
            next_correlative = (int(range_codes['start']) + i) - 1
        else:
            next_correlative = i
    return str(next_correlative).zfill(3)

