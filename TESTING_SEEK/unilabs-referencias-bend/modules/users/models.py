#models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager as BaseUserManager
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .choices import TypeUserChoices, DocumentTypeChoices, SexoChoices, CronTypeChoices
from modules.setting.models import Module
from django.db.models.signals import post_save
from datetime import datetime
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import Group


class Reference(models.Model):
    name = models.CharField(max_length=250, null=True, unique=False, blank=False, verbose_name="Cliente")
    ruc = models.CharField(max_length=20, null=True, blank=True, verbose_name="RUC")
    code = models.CharField(max_length=20, null=True, unique=True, blank=False, verbose_name="Código")
    phone = models.CharField(max_length=50, null=True, unique=False, blank=False, verbose_name="Telefono")
    email = models.EmailField(max_length=70, null=True, blank=True, verbose_name="Email")
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name="Dirección")

    description_siglo = models.CharField(max_length=250, null=True, blank=True, verbose_name="Descripción siglo")
    name_manager = models.CharField(max_length=150, null=True, blank=True, verbose_name="Nombres del responsable")
    last_name_manager = models.CharField(max_length=150, null=True, blank=True, verbose_name="Apellidos del responsable")
    document_type_manager = models.CharField(verbose_name="Tipo de documento", default=DocumentTypeChoices.EMPTY, max_length=30,
                            choices=DocumentTypeChoices.choices)
    document_number_manager = models.CharField(max_length=70, null=True, blank=True, verbose_name="Documento")
    active = models.BooleanField(default=True, null=False, blank=False, verbose_name="¿Activo?")
    motive = models.TextField(max_length=400, null=True, blank=False, verbose_name="Motivo (activación/desactivación)")
    created = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Fecha de creación")
    history = HistoricalRecords()

    def actives(self):
        return Reference.objects.filter(active=True)

    def __str__(self):
        return "{0} - {1} - {2}".format(self.code or '-', self.name or '-', self.ruc or '-')

    class Meta:
        verbose_name = "Referencia"
        verbose_name_plural = "Referencias"
        ordering = ['name']


class Debts(models.Model):
    name = models.CharField(max_length=70, null=True, unique=True, blank=False, verbose_name="Cliente")
    reference = models.ForeignKey(Reference, to_field='code', default=None, null=True, on_delete=models.CASCADE,
                                 verbose_name='Referencia', related_name='debts_reference')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Deuda"
        verbose_name_plural = "Deudas"
        ordering = ['name']


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    type = models.CharField(verbose_name="Tipo de usuario", default=TypeUserChoices.REFERENCE, max_length=30, choices=TypeUserChoices.choices)
    username = models.CharField(max_length=70, null=False, unique=True, blank=False, verbose_name="Usuario")
    email = models.EmailField(verbose_name=_('Email'), max_length=250, unique=True, null=True, default=None, blank=False, db_index=True)
    first_name = models.CharField(verbose_name=_('nombres'), blank=False, null=False, max_length=150)
    last_name = models.CharField(verbose_name=_('Apellidos'), blank=False, null=True, max_length=150)
    code_activation = models.CharField(verbose_name=_('Código activación'), null=True, blank=True, max_length=6)
    token_activation = models.CharField(verbose_name=_('Token activación'), null=True, blank=True, max_length=250)
    job = models.CharField(verbose_name=_('Puesto'), max_length=150, null=True, blank=False)
    cellphone = models.CharField(verbose_name=_('Celular'), max_length=15, null=True, blank=False)
    gender = models.CharField(verbose_name="Sexo", null=True, default=None, max_length=30, choices=SexoChoices.choices)
    document_type = models.CharField(verbose_name="Tipo de documento", default=None, null=True, blank=False, max_length=30,
                            choices=DocumentTypeChoices.choices)
    document_number = models.CharField(
        verbose_name=_('Documento'), max_length=20, null=True, blank=False, unique=True
    )
    onboarding_count = models.IntegerField(blank=False, default=0, null=True, verbose_name="Cantidad onboarding")
    onboarding = models.BooleanField(default=False, null=True, blank=True, verbose_name="Onboarding")
    onboarding_finish = models.BooleanField(default=False, null=True, blank=True, verbose_name="Onboarding finalizado")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated = models.DateTimeField(auto_now_add=False, default=datetime.now(), null=True, verbose_name="Última de modificación")
    last_login = models.DateTimeField(default=None, null=True, verbose_name="Último inicio")
    references = models.ManyToManyField(Reference, verbose_name='Referencias', blank=True, default=None, related_name='references')
    origenes = models.ForeignKey(Reference, to_field='code', default=None, null=True, blank=True, on_delete=models.CASCADE,
                                 verbose_name='Referencia (activa)', related_name='user_reference')
    access = models.ManyToManyField(Module, verbose_name='Modulos', blank=True, default=None, related_name='modules')
    sync = models.BooleanField(default=False, null=True, blank=True, verbose_name="¿Sincronizar?")
    email_activated = models.BooleanField(default=False, null=False, blank=False, verbose_name="Email activado")
    update_password = models.BooleanField(default=False, null=True, blank=True, verbose_name="¿Contraseña cambiada?")
    update_password_from_bkoffice = models.BooleanField(default=False, null=True, blank=True, verbose_name="Contraseña desde backoffice")
    verify_token = models.CharField(verbose_name=_('Token verify'), max_length=400, null=True, blank=True)
    is_staff = models.BooleanField(verbose_name=_('Staff'), default=True)
    is_active = models.BooleanField(verbose_name=_('¿Activo?'), default=True)
    is_admin_bk = models.BooleanField(verbose_name=_('¿Admin backoffice?'), default=False)
    encript_password = models.BooleanField(verbose_name=_('Encript password'), default=False)
    history = HistoricalRecords()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        response = True
        reference_admin = ReferenceAdmin.objects.filter(user=self.id, reference__active=True).first()
        if ((not reference_admin and self.type == 'Referencia') or not self.email_activated) and not self.is_superuser:
            response = False
        return response

    objects = UserManager()

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name or '', self.last_name or '')

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')

    def __str__(self):
        return self.get_full_name()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_password = self.password


class UserLogPassword(models.Model):
    created = models.DateTimeField(default=timezone.now, verbose_name="Creación")
    user_password = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", related_name="user_log_password")
    user_changed = models.CharField(max_length=150, verbose_name="Usuario (admin)")

    def __str__(self):
        return self.user.get_full_name() or ''

    class Meta:
        verbose_name = "Log password"
        verbose_name_plural = "Logs password"


class UserSession(models.Model):
    created = models.DateTimeField(default=timezone.now, verbose_name="Creación")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", related_name="user_session")
    reference_active = models.ForeignKey(Reference, on_delete=models.CASCADE, null=True, default=None, verbose_name="Referencia", related_name="reference_session")

    class Meta:
        verbose_name = "Sesión"
        verbose_name_plural = "Sesiones"

    def __str__(self):
        return self.user.get_full_name() or ''


class ReferenceExecutive(models.Model):
    reference = models.ForeignKey(Reference, to_field='code', default=None, null=True, on_delete=models.CASCADE,
                                  verbose_name='Referencia', related_name='executive_reference')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario",
                             related_name="executive_user_reference")
    history = HistoricalRecords()

    def __str__(self):
        return self.user.get_full_name() or ''

    class Meta:
        verbose_name = "Ejecutivo"
        verbose_name_plural = "Ejecutivos"


class ReferenceAdmin(models.Model):
    reference = models.ForeignKey(Reference, to_field='code', default=None, null=True, on_delete=models.CASCADE,
                                  verbose_name='Referencia', related_name='reference_reference_admin')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Administrador",
                             related_name="user_reference_admin")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"
    
    def __str__(self):
        return self.reference.name or ''


class GroupsAdmin(Group):
    type = models.CharField(verbose_name="Tipo de usuario", default=TypeUserChoices.REFERENCE, max_length=30, choices=TypeUserChoices.choices)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = "Roles y permisos"
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Synchronization(models.Model):
    created = models.DateTimeField(default=timezone.now, verbose_name="Creación")
    is_ok = models.BooleanField(verbose_name=_('Correcto'), default=True)
    type = models.CharField(verbose_name="Cron", default=CronTypeChoices.REFERENCE, max_length=30, choices=CronTypeChoices.choices)
    body = models.TextField(verbose_name="Cuerpo", null=True, blank=True)
    response = models.TextField(verbose_name="Respuesta", null=True, blank=True)
    
    class Meta:
        verbose_name = "Sincronización"
        verbose_name_plural = "Sincronizaciones"

    def __str__(self):
        return str(self.created)


"""
def access_user(sender, instance, **kwargs):
    modules = Module.objects.values_list('id', flat=True)
    for module in modules:
        instance.access.add(module)


post_save.connect(access_user, sender=User)
"""