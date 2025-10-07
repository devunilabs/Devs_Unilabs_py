from django.db import models
from simple_history.models import HistoricalRecords


class Information(models.Model):
    key = models.CharField(max_length=45, blank=True, unique=True, verbose_name="Clave")
    value = models.TextField(blank=True, verbose_name="Detalle")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Información"
        verbose_name_plural = "Información"

    def __str__(self):
        return self.key


class Emails(models.Model):
    TYPE = (
        ('error_sync', 'Error sincronización'),
        ('error_luggage', 'Error valijas'),
    )

    type = models.CharField(max_length=40, choices=TYPE, unique=True, default=None, verbose_name="Tipo")
    subject = models.CharField(max_length=70, blank=True, unique=True, verbose_name="Asunto")
    emails = models.TextField(blank=True, verbose_name="Correos (separados por comas)")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Email's"

    def __str__(self):
        return self.subject

