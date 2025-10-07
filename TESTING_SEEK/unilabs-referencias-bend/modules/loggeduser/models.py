from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django import forms


class Reference(models.Model):
    name = models.CharField(max_length=70, null=True, unique=True, blank=False, default=None, verbose_name="Cliente")
    code = models.CharField(max_length=20, null=True, unique=True, blank=False, default=None, verbose_name="Código")
    ruc = models.CharField(max_length=20, null=False, unique=False, blank=False, default=None, verbose_name="RUC")

    phone = models.CharField(max_length=20, null=True, unique=False, blank=True, default=None, verbose_name="Telefono")
    email = models.CharField(max_length=70, null=True, unique=False, blank=True, default=None, verbose_name="Email")
    address = models.CharField(max_length=70, null=True, unique=False, blank=True, default=None, verbose_name="Dirección")

    def __str__(self):
        return "{0} - {1}".format(self.name or '-', self.ruc or '-')

    class Meta:
        verbose_name = "Referencia"
        verbose_name_plural = "Referencias"
        ordering = ['name']


class LoggedUser(models.Model):
    username = models.CharField(max_length=45, null=True, blank=True, verbose_name="Nickname")
    name = models.CharField(max_length=70, null=True, blank=True, verbose_name="Nombres")
    email = models.EmailField(max_length=70, null=True, blank=True, verbose_name="Email")
    user_id = models.IntegerField(blank=False, unique=True, null=True, verbose_name="User ID")
    origenes = models.ForeignKey(Reference, to_field='code', null=True, default=None, on_delete=models.CASCADE,
                                  verbose_name='Referencia', related_name='loggeduser_refference')
    onboarding_count = models.IntegerField(blank=False, default=0, null=True, verbose_name="Cantidad onboarding")
    onboarding = models.BooleanField(default=False, null=True, blank=True, verbose_name="Onboarding")
    onboarding_finish = models.BooleanField(default=False, null=True, blank=True, verbose_name="Onboarding finalizado")
    change_password = models.BooleanField(default=True, null=True, blank=True, verbose_name="Contraseña cambiada")

    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    last_login = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Último inicio")
    references = models.ManyToManyField(Reference, verbose_name='Referencias', related_name='loggeduser_reference')

    class Meta:
        verbose_name = "Usuario logeado"
        verbose_name_plural = "Usuarios logeados"

    def __str__(self):
        return self.username or '-'


class UserSession(models.Model):
    created = models.DateTimeField(default=timezone.now, verbose_name="Creación")
    logged_user = models.ForeignKey(LoggedUser, on_delete=models.CASCADE, verbose_name="Usuario",
                                    related_name="logged_user_session")

    class Meta:
        verbose_name = "Sesion"
        verbose_name_plural = "Sesiones"

