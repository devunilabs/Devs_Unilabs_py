# class
from .masters import ReportType, ReportTypeGroupDate

# Models
from modules.users.models import User, UserSession, Reference, ReferenceAdmin
from modules.luggage.models import Luggage
from modules.report.models import Tracking
from django.db.models import Count

# Django
from django.db.models import F
import pandas as pd
from django.db.models import Q


class ReportMaker:
    instance = None
    td = pd.Timedelta(5, unit='h')
    df = None

    def __init__(self, instance, user):
        self.instance = instance
        self.reference_ids = []

        if user.type == 'Unilabs':
            self.reference_ids = Reference.objects.values_list('id', flat=True)
        else:
            self.reference_ids = ReferenceAdmin.objects.filter(user=user.id).values_list('reference__id', flat=True)

    def __group_date(self):
        formats = {
            ReportTypeGroupDate.YEAR: 'YYYY',
            ReportTypeGroupDate.MONTH: 'YYYY-MM',
            ReportTypeGroupDate.DAY: 'YYYY-MM-DD',
            ReportTypeGroupDate.HOUR: 'YYYY-MM-DD hh'
        }
        return formats[self.instance.type_date]

    def __group_date_format_pd(self):
        formats = {
            ReportTypeGroupDate.YEAR: '%Y',
            ReportTypeGroupDate.MONTH: '%b %Y',
            ReportTypeGroupDate.DAY: '%b %d %Y',
            ReportTypeGroupDate.HOUR: '%b %d %Y %H %p'
        }
        return formats[self.instance.type_date]

    """" Reports """
    # SESSION
    def __queryset_user_sessions(self):
        qs = UserSession.objects\
            .extra({'CANTIDAD': 1})
            # .extra(select={'FECHA': "to_char(loggeduser_usersession.created, '{0}')".format(self.__group_date())})

        if self.instance.start_date:
            qs = qs.filter(created__range=[
                self.instance.start_date.strftime('%Y-%m-%d 00:00:00'),
                self.instance.end_date.strftime('%Y-%m-%d 23:59:59')
            ])

        if self.instance.reference:
            qs = qs.filter(reference_active=self.instance.reference)

        return qs\
            .annotate(USER=F('user__username'), FECHA=F('created'), CLIENTE=F('reference_active__name'))\
            .values('USER', 'FECHA', 'CLIENTE', 'CANTIDAD')

    def __report_user_sessions(self):
        qs = self.__queryset_user_sessions()
        if qs:
            df = pd.DataFrame(list(qs))
            df['FECHA'] = df['FECHA'] \
                .apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d %H") - self.td).dt.strftime(self.__group_date_format_pd())
            df = df.groupby(['FECHA', 'USER', 'CLIENTE']).sum()

            df['%'] = (df.CANTIDAD / df.CANTIDAD.sum()) * 100
            df = df.sort_values('FECHA', ascending=False)
            df.loc['Total', :] = df.sum().values
            return df
        return None

    # LUGGAGE
    def __queryset_report_user_luggage(self):
        qs = Luggage.objects.extra({'VALIJAS_TOTALES': 1})

        if self.instance.start_date:
            qs = qs.filter(date_completed__range=[
                               self.instance.start_date.strftime('%Y-%m-%d 00:00:00'),
                               self.instance.end_date.strftime('%Y-%m-%d 23:59:59')
                           ])

        if self.instance.reference:
            qs = qs.filter(reference=self.instance.reference)

        qs = qs.annotate(FECHA=F('date_completed'), CLIENTE=F('reference__name'),
                           PRUEBAS=Count('test_luggage', distinct=True),
                           ATENCIONES_TOTALES=Count('details', distinct=True),
                           ATENCIONES_ENVIADAS=Count('details', filter=Q(details__sent=True), distinct=True),
                           ATENCIONES_NO_ENVIADAS=Count('details', filter=Q(details__sent=False), distinct=True))\
            .values('CLIENTE', 'FECHA', 'VALIJAS_TOTALES', 'PRUEBAS', 'ATENCIONES_TOTALES',
                    'ATENCIONES_ENVIADAS', 'ATENCIONES_NO_ENVIADAS')
        return qs

    def __report_user_luggage(self):
        qs = self.__queryset_report_user_luggage()

        """ Group by - pandas """
        if qs:
            df = pd.DataFrame(list(qs))
            df['FECHA'] = df['FECHA'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d %H") - self.td)\
                .dt.strftime(self.__group_date_format_pd())

            df = df.groupby(['FECHA', 'CLIENTE']).sum()
            df['% Valijas'] = (df.VALIJAS_TOTALES / df.VALIJAS_TOTALES.sum()) * 100
            df = df.sort_values('FECHA', ascending=False)
            df.loc['Total', :] = df.sum().values

            return df
        return None

    # REFERENCE USER
    def __queryset_user_reference_user(self):
        qs = User.objects.prefetch_related("references").filter(type='Referencia', references__id__in=self.reference_ids)
        if self.instance.start_date:
            qs = qs.filter(created__range=[
                self.instance.start_date.strftime('%Y-%m-%d 00:00:00'),
                self.instance.end_date.strftime('%Y-%m-%d 23:59:59')
            ])

        if self.instance.reference:
            qs = qs.filter(references=self.instance.reference)

        return qs\
            .annotate(ID=F('id'), USUARIO=F('username'), FECHA_CREACION=F('created'), DOCUMENTO_TIPO=F('document_type'), DOCUMENTO=F('document_number'), NOMBRES=F('first_name'), APELLIDOS=F('last_name'), REFERENCIA=F('references__name'))\
            .values('ID', 'USUARIO', 'FECHA_CREACION', 'DOCUMENTO_TIPO', 'DOCUMENTO', 'NOMBRES', 'APELLIDOS', 'REFERENCIA')

    def __report_user_reference_user(self):
        qs = self.__queryset_user_reference_user()

        if qs:
            df = pd.DataFrame(list(qs)).set_index('ID')
            df['FECHA_CREACION'] = df['FECHA_CREACION'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d %H") - self.td)\
                .dt.strftime(self.__group_date_format_pd())
            df = df.sort_values('REFERENCIA', ascending=False)
            return df
        return None

    # RESULT NOT DOWNLOAD
    def __queryset_user_result_not_download(self):
        
        users_ids = Tracking.objects.filter(type='result_pdf').filter(created__range=[
                self.instance.start_date.strftime('%Y-%m-%d 00:00:00'),
                self.instance.end_date.strftime('%Y-%m-%d 23:59:59')
            ]).values_list('creator__id', flat=True)

        if users_ids:
            qs = User.objects.exclude(id__in=users_ids).filter(type='Referencia', references__id__in=self.reference_ids)
        else:
            qs = User.objects.filter(type='Referencia', references__id__in=self.reference_ids)

        if self.instance.reference:
            qs = qs.filter(references=self.instance.reference)

        return qs\
            .annotate(ID=F('id'), USUARIO=F('username'), ULTIMA_SESION=F('last_login'), DOCUMENTO_TIPO=F('document_type'), DOCUMENTO=F('document_number'), NOMBRES=F('first_name'), APELLIDOS=F('last_name'), REFERENCIA=F('references__name'))\
            .values('ID', 'USUARIO', 'ULTIMA_SESION', 'DOCUMENTO_TIPO', 'DOCUMENTO', 'NOMBRES', 'APELLIDOS', 'REFERENCIA')

    def __report_user_result_not_download(self):
        qs = self.__queryset_user_result_not_download()

        if qs:
            df = pd.DataFrame(list(qs)).set_index('ID')
            df['ULTIMA_SESION'] = df['ULTIMA_SESION'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d %H") - self.td)\
                .dt.strftime(self.__group_date_format_pd())
            df = df.sort_values('ULTIMA_SESION', ascending=False)
            return df
        return None

    # IMAGE NOT DONWLOAD
    def __queryset_user_image_not_download(self):
        users_ids = Tracking.objects.filter(type='image_pdf').filter(created__range=[
                self.instance.start_date.strftime('%Y-%m-%d 00:00:00'),
                self.instance.end_date.strftime('%Y-%m-%d 23:59:59')
            ]).values_list('creator__id', flat=True)

        if users_ids:
            qs = User.objects.exclude(id__in=users_ids).filter(type='Referencia', references__id__in=self.reference_ids)
        else:
            qs = User.objects.filter(type='Referencia', references__id__in=self.reference_ids)

        if self.instance.reference:
            qs = qs.filter(references=self.instance.reference)

        return qs\
            .annotate(ID=F('id'), USUARIO=F('username'), ULTIMA_SESION=F('last_login'), DOCUMENTO_TIPO=F('document_type'), DOCUMENTO=F('document_number'), NOMBRES=F('first_name'), APELLIDOS=F('last_name'), REFERENCIA=F('references__name'))\
            .values('ID', 'USUARIO', 'ULTIMA_SESION', 'DOCUMENTO_TIPO', 'DOCUMENTO', 'NOMBRES', 'APELLIDOS', 'REFERENCIA')

    def __report_user_image_not_download(self):
        qs = self.__queryset_user_image_not_download()

        if qs:
            df = pd.DataFrame(list(qs)).set_index('ID')
            df['ULTIMA_SESION'] = df['ULTIMA_SESION'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d %H") - self.td)\
                .dt.strftime(self.__group_date_format_pd())
            df = df.sort_values('ULTIMA_SESION', ascending=False)
            return df
        return None

    # USER NOT USED APP
    def __queryset_user_not_used_app(self):
        qs = User.objects.prefetch_related("references").filter(type='Referencia', references__id__in=self.reference_ids)
        qs = qs.exclude(
            Q(last_login__range=[
                self.instance.start_date.strftime('%Y-%m-%d 00:00:00'),
                self.instance.end_date.strftime('%Y-%m-%d 23:59:59')
            ])
        )

        if self.instance.reference:
            qs = qs.filter(references=self.instance.reference)

        return qs\
            .annotate(USER=F('username'), ULTIMA_SESION=F('last_login'))\
            .values('USER', 'ULTIMA_SESION')

    def __report_user_not_used_app(self):
        qs = self.__queryset_user_not_used_app()

        if qs:
            df = pd.DataFrame(list(qs))
            df['ULTIMA_SESION'] = df['ULTIMA_SESION'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d %H") - self.td)\
                .dt.strftime(self.__group_date_format_pd())
            df = df.sort_values('ULTIMA_SESION', ascending=False)
            return df
        return None


    """" Valid """
    def validate_queryset(self):
        if self.instance.type == ReportType.REFERENCE_SESSION:
            return self.__queryset_user_sessions().exists()

        elif self.instance.type == ReportType.REFERENCE_LUGGAGE:
            return self.__queryset_report_user_luggage().exists()

        elif self.instance.type == ReportType.REFERENCE_USER:
            return self.__queryset_user_reference_user().exists()
        
        elif self.instance.type == ReportType.RESULT_NOT_DOWNLOAD:
            return self.__queryset_user_result_not_download().exists()
        
        elif self.instance.type == ReportType.IMAGE_NOT_DOWNLOAD:
            return self.__queryset_user_image_not_download().exists()
        
        elif self.instance.type == ReportType.NOT_USED_APP:
            return self.__queryset_user_not_used_app().exists()

        return False

    def get_report(self):
        types = {
            ReportType.REFERENCE_SESSION: self.__report_user_sessions(),
            ReportType.REFERENCE_LUGGAGE: self.__report_user_luggage(),

            ReportType.REFERENCE_USER: self.__report_user_reference_user(),
            ReportType.RESULT_NOT_DOWNLOAD: self.__report_user_result_not_download(),
            ReportType.IMAGE_NOT_DOWNLOAD: self.__report_user_image_not_download(),
            ReportType.NOT_USED_APP: self.__report_user_not_used_app()
        }
        return types[self.instance.type]

