from django.db import models
from modules.users.models import User
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords


class Analytical(models.Model):
    description = models.TextField(verbose_name="Descripción")
    manual = models.FileField(upload_to='analytical/pdf', null=True, blank=True, verbose_name="Manual")
    created = models.DateTimeField(auto_now_add=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.description[:120]+'...'

    class Meta:
        verbose_name = "Pre-analitica"
        verbose_name_plural = "Analiticas"
        ordering = ['id', ]


class VideoAnalytical(models.Model):
    order = models.IntegerField(blank=True, null=True, verbose_name="Orden")
    title = models.CharField(max_length=120, blank=True, verbose_name="Titulo")
    description = models.CharField(max_length=400, blank=True, verbose_name="Descripción")
    duration = models.CharField(max_length=20, blank=True, verbose_name="Duración")
    video = models.CharField(max_length=200, blank=False, null=True, verbose_name="URL video")
    image = models.ImageField(upload_to='video-analytical/image', null=True, blank=False,
                              verbose_name="Imagen (600px x 600px)")
    analytical = models.ForeignKey(Analytical, on_delete=models.CASCADE, related_name="analytical_video",
                                   verbose_name="Analítica")
    created = models.DateTimeField(auto_now_add=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        ordering = ['order', ]

    def clean(self):
        order = VideoAnalytical.objects.filter(order=self.order).first()
        if not self.id and order:
            raise ValidationError("El valor del orden ya existe, por favor elija uno distinto")


class StageAnalytical(models.Model):
    order = models.IntegerField(blank=True, null=True, verbose_name="Orden")
    title = models.CharField(max_length=120, blank=True, verbose_name="Titulo")
    analytical = models.ForeignKey(Analytical, on_delete=models.CASCADE, verbose_name="Analitica",
                                   related_name="analytical_stage")
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Etapa"
        verbose_name_plural = "Etapas"
        ordering = ['order', ]

    def clean(self):
        order = StageAnalytical.objects.filter(order=self.order).first()
        if not self.id and order:
            raise ValidationError("El valor del orden ya existe, por favor elija uno distinto")


class StagePageAnalytical(models.Model):
    order = models.IntegerField(blank=True, null=True, verbose_name="Orden")
    title = models.CharField(max_length=120, blank=True, verbose_name="Titulo")
    description = models.TextField(verbose_name="Descripción")
    nota = models.TextField(verbose_name="Nota", null=True, blank=True)
    video = models.CharField(max_length=200, blank=True, null=True, verbose_name="URL video")
    image = models.ImageField(upload_to='analytical/image', null=True, blank=True, verbose_name="Imagen")
    image_mobile = models.ImageField(upload_to='analytical/image', null=True, blank=True, verbose_name="Imagen Mobile")
    description_image = models.TextField(verbose_name="Descripción Imagen", null=True, blank=True)
    stage = models.ForeignKey(StageAnalytical, on_delete=models.CASCADE, verbose_name="Etapa", related_name="stage_page")
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Pagina"
        verbose_name_plural = "Paginas"
        ordering = ['order', ]

    def clean(self):
        order = StagePageAnalytical.objects.filter(order=self.order).first()
        if not self.id and order:
            raise ValidationError("El valor del orden ya existe, por favor elija uno distinto")


class PageSearchRecord(models.Model):
    title = models.CharField(max_length=120, blank=True, verbose_name="Titulo")
    page = models.IntegerField(null=False, blank=True, verbose_name="Pagina")
    creator = models.ForeignKey(User, null=True, on_delete=models.CASCADE, verbose_name="Creador",
                                related_name="creator_record")
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Pagina"
        verbose_name_plural = "Paginas"
        ordering = ['-id', ]

