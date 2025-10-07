from django.db.models import IntegerChoices


class ReportType(IntegerChoices):
    REFERENCE_SESSION = 1, 'Sesiones por Referencia'
    REFERENCE_LUGGAGE = 2, 'Valijas por Referencia'
    REFERENCE_USER = 3, 'Referencias por Usuario'
    RESULT_NOT_DOWNLOAD = 4, 'Reporte de resultados no descargados'
    IMAGE_NOT_DOWNLOAD = 5, 'Reporte de imagenes no descargadas'
    NOT_USED_APP = 6, 'Usuarios no usan la aplicación'


class ReportTypeGroupDate(IntegerChoices):
    HOUR = 1, 'Hora'
    DAY = 2, 'Día'
    MONTH = 3, 'Mes'
    YEAR = 4, 'Año'

