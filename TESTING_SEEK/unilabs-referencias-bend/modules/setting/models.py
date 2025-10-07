from django.db import models
from adminsortable.models import SortableMixin
from simple_history.models import HistoricalRecords


class Module(SortableMixin):
    MODULES = (
        ('imagenes', 'Imágenes'),
        ('resultados', 'Resultados'),
        ('mis-valijas', 'Valija'),
        ('catalogo-de-pruebas', 'Catálogo'),
        ('registro-atenciones', 'Registro de atenciones'),
        ('manual-pre-analitica', 'Manual pre-analítica'),
        ('notification', 'Notificaciones')
    )

    module = models.CharField(max_length=40, choices=MODULES, unique=True, default="luggage", verbose_name="Módulo")
    icon = models.CharField(max_length=40, default="", verbose_name="Icono")
    icon_image = models.ImageField(upload_to='module/image', null=True, blank=True)
    title = models.CharField(max_length=40, default="", verbose_name="Titulo")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    the_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Modulo"
        verbose_name_plural = "Modulos"
        ordering = ['the_order']

    def __str__(self):
        return self.title or '-'

