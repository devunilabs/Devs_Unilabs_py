from django.db import models
from .masters import ReportType, ReportTypeGroupDate
from modules.users.models import User, Reference
from django.core.exceptions import ValidationError


class ReferencesData(models.Model):
    date = models.DateField(verbose_name='Fecha')
    name = models.CharField(verbose_name='Nombre', max_length=6, unique_for_date='date')
    total = models.PositiveIntegerField(verbose_name='Total', default=0)
    last_id = models.BigIntegerField(verbose_name='Último ID actualizado')
    updated = models.DateTimeField(verbose_name='Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Referencias'
        verbose_name_plural = 'Referencias enviadas'
        managed = False

    def __str__(self):
        return self.name


class UnilabsReport(models.Model):
    name = models.CharField(verbose_name='* Nombre', max_length=120)
    type = models.SmallIntegerField(verbose_name='* Tipo', choices=ReportType.choices)
    type_date = models.SmallIntegerField(verbose_name='* Agrupado', default=2, null=False, blank=False, choices=ReportTypeGroupDate.choices)

    start_date = models.DateField(verbose_name='Fecha de aprobación (inicio)', null=False, default=None, blank=False)
    end_date = models.DateField(verbose_name='Fecha de aprobación (fin)', null=False, default=None, blank=False)

    file = models.FileField(verbose_name='Descargable', null=True, blank=True)
    reference = models.ForeignKey(Reference, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Cliente",
                                  related_name="reference_customer_report")
    created = models.DateTimeField(verbose_name='Creado', auto_now_add=True)

    def clean(self):
        if (self.start_date and self.start_date) and (self.start_date >= self.end_date):
            raise ValidationError("La fecha de inicio no puede ser mayor a la fecha final")

    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'

    def __str__(self):
        return self.name


class Tracking(models.Model):
    TYPE = (
        ('luggage_pdf', 'Valija PDF'),
        ('luggage_excel', 'Valija Excel'),
        ('result_pdf', 'Resultado PDF'),
        ('image_pdf', 'Imagen PDF')
    )

    type = models.CharField(max_length=40, choices=TYPE, default="pdf", null=True, verbose_name="Tipo")
    params = models.CharField(verbose_name='Parametros', max_length=200, null=True, blank=True)
    creator = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                verbose_name="Creador", related_name="logged_result_tracking")
    created = models.DateTimeField(verbose_name='Creación', auto_now=True)

    def __str__(self):
        return self.params

    class Meta:
        verbose_name = 'Tracking'
        verbose_name_plural = 'Tracking'
