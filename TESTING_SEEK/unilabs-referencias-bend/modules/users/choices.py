from django.db.models import TextChoices


class CronTypeChoices(TextChoices):
    USERS = 'Usuarios', 'Usuarios'
    REFERENCE = 'Referencia', 'Referencia'


class TypeUserChoices(TextChoices):
    UNILABS = 'Unilabs', 'Unilabs'
    REFERENCE = 'Referencia', 'Referencia'


class DocumentTypeChoices(TextChoices):
    DNI = 'Dni', 'Dni'
    CE = 'Carnet extranjeria', 'Carnet extranjeria'
    PASSPORT = 'Pasaporte', 'Pasaporte'
    EMPTY = '', ''


class SexoChoices(TextChoices):
    M = 'Masculino', 'Masculino'
    F = 'Femenino', 'Femenino'
