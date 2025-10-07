from django.core.exceptions import ValidationError
from django.db import models
from modules.users.models import User
from simple_history.models import HistoricalRecords
from django.utils import timezone
import requests
from django.conf import settings

# Models
from modules.users.models import Reference


class Patient(models.Model):
    GENDER = (('M', 'Feminino'), ('H', 'Masculino'))
    DOC_TYPE = (
        ('dni', 'Dni'),
        ('passport', 'Pasaporte'),
        ('ce', 'Carnet de extranjeria'),
        ('rn', 'Recien nacido'),
        ('pn', 'Partida de nacimiento'),
        ('pdp', 'Paciente con datos protegidos'),
        ('ot', 'Otros')
    )

    name = models.CharField(max_length=45, blank=True, null=True, verbose_name="Nombres")
    first_surname = models.CharField(max_length=45, blank=True, null=True, verbose_name="Apellido paterno")
    last_surname = models.CharField(max_length=45, blank=True, null=True, verbose_name="Apellido materno")
    gender = models.CharField(max_length=40, choices=GENDER, default="H", null=True, verbose_name="Genero")
    document_type = models.CharField(max_length=40, choices=DOC_TYPE, default="dni", verbose_name="Tipo de documento")
    document = models.CharField(max_length=45, unique=False, blank=True, null=True, verbose_name="N. Documento")
    mobile_number = models.CharField(max_length=12, blank=True, null=True, unique=False, verbose_name="Celular")
    complete = models.BooleanField(default=False, null=True, blank=True, verbose_name="Completado")
    creator = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                verbose_name="Creador", related_name="creator_patient")
    creator_fullname = models.CharField(max_length=70, unique=False, blank=True, null=True, verbose_name="Creador")
    updater = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                verbose_name="Actualizado por", related_name="updated_patient")
    date_birth = models.DateField(null=True, blank=True, verbose_name="Fecha nacimiento")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    history = HistoricalRecords()

    def __str__(self):
        if self.name or self.first_surname or self.last_surname:
            return "{0} {1} {2}".format(self.name if self.name else '',
                                        self.first_surname if self.first_surname else '',
                                        self.last_surname if self.last_surname else '')
        else:
            return str(self.id)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-created']


class TestSearchRecord(models.Model):
    code = models.CharField(blank=True, max_length=45, verbose_name="Código ref")
    name = models.CharField(max_length=75, blank=True, verbose_name="Nombre")
    creator_id = models.IntegerField(blank=False, null=True, verbose_name="Creador ID")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created']


class Luggage(models.Model):
    STATUS = (('active', 'Activo'), ('deleted', 'Eliminado'), ('completed', 'Completado'))
    status = models.CharField(max_length=40, choices=STATUS, default="active", verbose_name="Estado")
    number_tubes = models.IntegerField(verbose_name="N. Tubos", null=True, blank=True, default=0)
    image = models.ImageField(upload_to='luggage/image', null=True, blank=True, verbose_name="Imagen")
    creator = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                verbose_name="Creador", related_name="creator_luggage")
    creator_fullname = models.CharField(max_length=70, unique=False, blank=True, null=True, verbose_name="Creador")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    sent = models.BooleanField(default=False, verbose_name="Enviado")
    date_completed = models.DateTimeField(null=True, blank=True, verbose_name="Fecha completada")
    reference = models.ForeignKey(Reference, to_field='code', null=True, default=None, on_delete=models.CASCADE,
                                  verbose_name='Referencia', related_name='luggage_refference')
    history = HistoricalRecords()

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "Valija"
        verbose_name_plural = "Valija"
        ordering = ['-id']


class LuggageDetail(models.Model):
    luggage = models.ForeignKey(Luggage, on_delete=models.CASCADE, verbose_name="Valija", related_name="details")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Paciente", related_name="luggage_patient")
    code = models.CharField(max_length=20, null=True, blank=True, verbose_name="Código")
    response_integration = models.TextField(null=True, blank=True, verbose_name="Respuesta integración")
    body_integration = models.JSONField(null=True, blank=True, verbose_name="Cuerpo integración")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    sent = models.BooleanField(default=False, verbose_name="Enviado")
    history = HistoricalRecords()

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('luggage', 'patient')
        verbose_name = "Valija detalle"
        verbose_name_plural = "Valija detalles"
        ordering = ['-id']


class Test(models.Model):
    detail = models.ForeignKey(LuggageDetail, default=None, on_delete=models.CASCADE, verbose_name="Detalle", related_name="test")
    luggage = models.ForeignKey(Luggage, null=True, on_delete=models.CASCADE, verbose_name="Valija",
                                related_name="test_luggage")
    patient = models.ForeignKey(Patient, null=True, on_delete=models.CASCADE, verbose_name="Paciente",
                                related_name="test_patient")
    code = models.CharField(blank=True, null=True, max_length=40, verbose_name="Prueba código")
    name = models.CharField(max_length=75, blank=True, null=True, verbose_name="Prueba")
    comment = models.TextField(max_length=250, blank=True, verbose_name="Comentario")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    history = HistoricalRecords()

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('detail', 'code')
        verbose_name = "Prueba"
        verbose_name_plural = "Pruebas"
        ordering = ['-created']

    def clean(self):
        response = requests.get(settings.API_INTEGRATION_DOMAIN + "/prueba/detalle/{0}".format(self.code),
                                auth=(settings.USER_INTEGRATION, settings.PASS_INTEGRATION), timeout=30).json()

        if not response['success']:
            raise ValidationError("El código de prueba no existe: {0}".format(self.code))


class LuggageAvailableCode(models.Model):
    start = models.IntegerField(blank=True, null=False, verbose_name="Desde")
    end = models.IntegerField(blank=True, null=False, verbose_name="Hasta")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Código"
        verbose_name_plural = "Códigos"

    def clean(self):
        lasted_row = LuggageDetail.objects.filter(code__isnull=False).values('code').order_by('-id').first()

        if lasted_row:
            lasted_code = lasted_row['code'][5:]

            if lasted_code and int(lasted_code) >= self.end:
                raise ValidationError("El código de inicio debe ser mayor a {0}".format(lasted_code))

        if self.start >= self.end:
            raise ValidationError("La código de inicio no puede ser mayor al código final")

    def __str__(self):
        return "{0} al {1}".format(self.start, self.end)


class SuperLog(models.Model):
    """Luggage"""
    luggage = models.ForeignKey(Luggage, on_delete=models.CASCADE, null=True, verbose_name="Valija",
                                related_name="log_luggage")
    detail = models.IntegerField(null=True, default=None, blank=True, verbose_name="Valija detalle")
    code = models.CharField(max_length=45, null=True, blank=True, verbose_name="Código")
    status = models.CharField(max_length=40, null=True, default='active', blank=True, verbose_name="Estado")
    number_tubes = models.IntegerField(verbose_name="N. Tubos", null=True, blank=True, default=0)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                verbose_name="Creador", related_name="log_creator")
    date_completed = models.DateTimeField(null=True, blank=True, verbose_name="Fecha envío")

    """Patient"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, verbose_name="Paciente", related_name="log_patient")
    name = models.CharField(max_length=45, blank=True, null=True, verbose_name="Nombres")
    first_surname = models.CharField(max_length=45, blank=True, null=True, verbose_name="Apellido paterno")
    last_surname = models.CharField(max_length=45, blank=True, null=True, verbose_name="Apellido materno")
    gender = models.CharField(max_length=40, blank=True, null=True, verbose_name="Genero")
    document_type = models.CharField(max_length=40, blank=True, null=True, default="dni", verbose_name="Tipo de documento")
    document = models.CharField(max_length=45, unique=False, blank=True, null=True, verbose_name="N. Documento")
    complete = models.BooleanField(default=False, null=True, blank=True, verbose_name="Completado")
    date_birth = models.DateField(null=True, blank=True, verbose_name="Fecha nacimiento")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Eliminación paciente")

    """Test"""
    test_code = models.CharField(max_length=45, blank=True, null=True, verbose_name="Prueba ref")
    test_name = models.CharField(max_length=75, blank=True, null=True, verbose_name="Prueba")
    comment = models.TextField(max_length=250, blank=True, null=True, verbose_name="Comentario")
    deleted_at_test = models.DateTimeField(null=True, blank=True, verbose_name="Eliminación prueba")

    """Model"""
    updated = models.DateTimeField(auto_now_add=timezone.now(), verbose_name="Fecha de actualización")
    creator_fullname = models.CharField(max_length=70, blank=True, null=True, default="", verbose_name="Creador")

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "Log"
        verbose_name_plural = "Logs"
        ordering = ['-id']

