from django.db import models


class Attention(models.Model):
    document = models.CharField(max_length=20, blank=True, verbose_name="Documento")
    value = models.CharField(max_length=45, blank=True, verbose_name="Valor")
    created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = "Atención"
        verbose_name_plural = "Atenciones"

