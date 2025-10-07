#admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateRangeFilter
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin
from django_admin_inline_paginator.admin import TabularInlinePaginated, TabularInline
from .models import User, UserSession, Reference, ReferenceAdmin, ReferenceExecutive, UserLogPassword, Synchronization
from .resources import ReferenceExportResource, UserExportResource
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.admin.filters import RelatedOnlyFieldListFilter
from simple_history.admin import SimpleHistoryAdmin
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.urls import path
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import format_html
from modules.users.models import GroupsAdmin
from django.contrib.auth.models import Group
from django import forms
from django.contrib.auth.forms import AdminPasswordChangeForm
from django_admin_listfilter_dropdown.filters import (DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter)
import requests
from requests.auth import HTTPBasicAuth
import re, json

# Helpers
from modules.users.helpers.mails import _send_mail_activation, _send_mail_error
from modules.users.helpers.user_add_unilabs import _send_unilabs_create, _send_unilabs_update
from modules.users.helpers import user_change_password
from admin_auto_filters.filters import AutocompleteFilter, AutocompleteFilterFactory

admin.site.unregister(Group)


# Resources
class UserResource(ModelResource):
    class Meta:
        model = User
        import_id_fields = ['email']
        fields = ['first_name', 'last_name', 'email', 'document_number', 'job', 'cellphone']


class UserInlineForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].label = 'Usuario'


# Inlines
class UserInline(TabularInlinePaginated):
    model = User.references.through
    extra = 0
    ordering = ('-id',)
    verbose_name = "Usuarios de la referencia"
    verbose_name_plural = "Usuarios de la referencia"
    form = UserInlineForm

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReferenceUserAdminInline(TabularInline):
    model = ReferenceAdmin
    extra = 0
    ordering = ('-id',)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(type='Referencia', references__id=request.resolver_match.kwargs['object_id'])
        return super(ReferenceUserAdminInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request, obj):
        if request.user.is_superuser or request.user.is_admin_bk or request.user.type == 'Unilabs':
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.is_admin_bk or request.user.type == 'Unilabs':
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.is_admin_bk or request.user.type == 'Unilabs':
            return True
        else:
            return False


class ReferenceExecutiveUserAdminInline(TabularInline):
    model = ReferenceExecutive
    extra = 0
    ordering = ('-id',)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(type='Unilabs')
        return super(ReferenceExecutiveUserAdminInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request, obj):
        if request.user.is_admin_bk and request.user.type == 'Unilabs':
            return True
        elif request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_admin_bk and request.user.type == 'Unilabs':
            return True
        elif request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_admin_bk and request.user.type == 'Unilabs':
            return True
        elif request.user.is_superuser:
            return True
        else:
            return False

# Forms
class ReferencesFilter(AutocompleteFilter):
    title = 'Referencias'
    field_name = 'references'


# Admin
class MyAdminPasswordChangeForm(AdminPasswordChangeForm):

    def save(self, commit=True):
        password = self.cleaned_data["password1"]
        self.user.set_password(password)

        if commit:
            self.user.save()
            status, response = user_change_password._change_password(self.user, password)
            if not status:
                _send_mail_error("No se pudo actualizar la contraseña", {"response": response, "payload": self.user})

        return self.user


class UserAdminForm(forms.ModelForm):
    ruc_lookup = forms.CharField(
        max_length=11,
        required=False,
        label="Traer referencias por RUC"
    )

    class Meta:
        model = User
        fields = "__all__"

    def save(self, commit=True):
        user = super().save(commit=False)
        ruc = self.cleaned_data.get("ruc_lookup")
        if ruc:
            resp = requests.get(
                f"https://integraciones.unilabs.pe/ws2seek/empresa/ruc/{ruc}",
                auth=HTTPBasicAuth(settings.USER_INTEGRATION, settings.PASS_INTEGRATION),
                timeout=30
            )
            raw = resp.text
            fixed = re.sub(
                r'"data"\s*:\s*\{(.+)\}\s*}$',
                r'"data":[{\1}]}',
                raw
            )
            payload = json.loads(fixed)['data']
            referencias = []
            for item in payload:
                ref, _ = Reference.objects.update_or_create(
                    ruc=item["ruc"],
                    code=item["codigo_siglo"],
                    defaults={
                        "name": item["nombre_comercial"],
                        "phone": item.get("telefonos") or "",
                        "email": item.get("email") or "",
                        "address": item.get("direccion_fiscal") or "",
                        "description_siglo": item.get("razon_social") or "",
                    }
                )
                referencias.append(ref)
            if commit:
                user.save()
                user.references.set(referencias)
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, BaseUserAdmin):
    list_display = ('id', 'username', 'type', 'first_name', 'last_name', 'resend_btn', 'email_activated', 'email', 'last_login', 'onboarding_finish',
                    'origenes')
    list_filter = [('created', DateRangeFilter), ('last_login', DateRangeFilter), 'type', 'email_activated', ('references__name', DropdownFilter),]
    search_fields = ['email', 'first_name', 'last_name', 'username', 'document_number', 'job']
    ordering = ['first_name']
    form = UserAdminForm
    resource_class = UserExportResource
    list_per_page = 50
    history_list_display = ["changed_fields", "list_changes"]
    readonly_fields = ('origenes', 'updated')
    filter_horizontal = ['references', 'access', 'groups']
    change_password_form = MyAdminPasswordChangeForm
    add_fieldsets = [
        ("Tipo de usuario", {
           'classes': ('wide', ),
           'fields': ('type', )
        }),
        ("Datos personales", {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
        ("Datos adicionales", {
            'classes': ('wide',),
            'fields': ('job', 'cellphone', 'gender', 'document_type', 'document_number'),
        }),
        ("Referencias", {
             'classes': ('wide',),
             'fields': ('origenes', 'references'),
        }),
        (_('Modulos'), {
            'fields': ('access',)
        }),
        (('Permisos'), {
            'fields': ('is_active', 'is_superuser', 'is_admin_bk')
        })
    ]
    fieldsets = [
        (_('Personal info'), {
            'fields': ('type', 'email', 'username', 'first_name', 'last_name', 'document_type', 'document_number',
                       'job', 'cellphone', 'gender', 'email_activated')
        }),
        (_('Cliente'), {
            'fields': ('ruc_lookup', 'origenes', 'references')
        }),
        (_('Modulos'), {
            'fields': ('access',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'groups', 'is_superuser', 'is_admin_bk')
        }),
        (_('Logs'), {
            'fields': ('updated', 'created')
        })
    ]

    class Media:
        js = ('js/users.js',)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<int:pk>/resend/', self.admin_site.admin_view(self._activation_send_email)),
        ]
        return my_urls + urls

    def resend_btn(self, obj):
        if obj.email_activated:
            return mark_safe("-")
        else:
            return mark_safe("<a href='/admin/users/user/{0}/resend/'><u>Enviar</u></a>".format(obj.id))

    resend_btn.short_description = 'Activar correo'
    resend_btn.allow_tags = True

    def _activation_send_email(self, request, pk):
        user = User.objects.filter(id=pk).first()
        if user:
            import jwt
            token = jwt.encode({"email": user.email}, "UnilabsJWT", algorithm="HS256")
            user.token_activation = token
            user.save()

            subject = "{0}".format("Activación de cuenta de usuario")
            email_template_name = "emails/password_reset_user.html"
            c = {
                "email": user.email,
                'domain': settings.APP_DOMAIN,
                'site_name': 'Unilabs',
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token,
                'protocol': 'https',
                'username': user.username,
                'type': user.type
            }
            email = render_to_string(email_template_name, c)
            send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
        self.message_user(request, "Se reenvió el correo de activación del usuario.", messages.SUCCESS)
        return redirect('/admin/users/user')

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        reference_admin = ReferenceAdmin.objects.filter(user=request.user.id).first()

        if reference_admin:
            ref_admin_ids = ReferenceAdmin.objects.filter(user_id=request.user.id).values_list('reference__id', flat=True)
            users_refs = User.objects.filter(references__in=ref_admin_ids, type='Referencia').values_list('id', flat=True)

            if users_refs:
                qs = qs.filter(id__in=users_refs)
            else:
                pass
        return qs

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = ('origenes', 'updated', 'created', 'email_activated')

        if request.user.is_superuser or request.user.is_admin_bk:
            self.readonly_fields = self.readonly_fields
        else:
            self.readonly_fields = self.readonly_fields + ('type', 'groups')

        reference_admin = ReferenceAdmin.objects.filter(user=request.user.id).values_list('reference__id', flat=True)
        if (not request.user.is_superuser or not request.user.is_admin_bk) and request.user.type == 'Referencia' and not reference_admin:
            self.readonly_fields = self.readonly_fields + ('references', 'access',)

        if not request.user.is_superuser or not request.user.is_admin_bk:
            self.readonly_fields = self.readonly_fields + ('origenes', 'is_superuser')

        if (not request.user.is_superuser or not request.user.is_admin_bk) and not request.user.type == 'Unilabs':
            self.readonly_fields = self.readonly_fields + ('is_admin_bk', )

        if request.user.is_superuser:
            self.readonly_fields = ('origenes', 'updated', 'created')
        
        if obj is not None:
            self.readonly_fields = self.readonly_fields + ('username', )
            
        return self.readonly_fields

    def save_model(self, request, obj, form, change):        
        
        try:
            super(UserAdmin, self).save_model(request, obj, form, change)
            if not change:
                user = User.objects.get(id=obj.id)

                if user:
                    import jwt
                    token = jwt.encode({"email": user.email}, "UnilabsJWT", algorithm="HS256")
                    user.token_activation = token

                    # Add group user
                    group = GroupsAdmin.objects.filter(type=user.type, name=user.type).first()
                    if group:
                        user.groups.add(group.id)
                    user.save()

                    # Send email activation account
                    _send_mail_activation(user, token)

                    # Send data - Unilabs
                    status, response, payload = _send_unilabs_create(user, form)
                    if not status:
                        _send_mail_error("Este usuario no se pudo guardar", {"response": response, "payload": payload})
            else:
                status, response, payload = _send_unilabs_update(obj, form)
                if not status:
                    _send_mail_error("Este usuario no se pudo guardar", {"response": response, "payload": payload})

            return redirect('/admin/users/user')
        except Exception as e:
            print('Error: ', e)
            redirect('/admin/users/user')
        
    def has_delete_permission(self, request, obj=None):
        return False

    def has_import_permission(self, request):
        return False

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

    def list_changes(self, obj):
        fields = ""
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)

            for change in delta.changes:
                if change.field == 'password':
                    fields += str("<strong>{}</strong> changed from <span style='background-color:#ffb5ad'>{}</span> to <span style='background-color:#b3f7ab'>{}</span> . <br/>".format(change.field, '******', '******'))
                else:
                    fields += str("<strong>{}</strong> changed from <span style='background-color:#ffb5ad'>{}</span> to <span style='background-color:#b3f7ab'>{}</span> . <br/>".format(change.field, change.old, change.new))
            return format_html(fields)
        return None


@admin.register(GroupsAdmin)
class GroupsAdminAdmin(ImportExportModelAdmin):
    list_display = ('id', 'type', 'name')
    filter_horizontal = ('permissions', )

    class Media:
        js = ('js/groups.js',)


@admin.register(UserSession)
class UserSessionAdmin(ImportExportModelAdmin):
    list_export = ('xls', 'csv')
    list_filter = [('created', DateRangeFilter), 'created']
    ordering = ('-user',)
    list_display = ('id', 'user', 'reference_active', 'created', 'count_total')
    search_fields = ['created', ]
    list_per_page = 50
    request = None

    def count_total(self, obj):
        qs = super(UserSessionAdmin, self).get_queryset(self.request)
        return qs.filter(user=obj.user).count()

    def get_queryset(self, request):
        qs = super(UserSessionAdmin, self).get_queryset(request)
        """if request.resolver_match.func.__name__ == 'change_view':
            return qs.distinct()"""
        return qs

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        """response.context_data['cl'].queryset = response.context_data['cl'].queryset"""
        cl = response.context_data['cl']
        cl.queryset = cl.queryset.distinct()
        return super().changelist_view(request, {"cl": cl})

    def has_delete_permission(self, request, obj=None):
        return False

    def has_import_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

@admin.register(Synchronization)
class SynchronizationAdmin(ImportExportModelAdmin):
    list_export = ('xls', 'csv')
    list_filter = ['created', 'is_ok', 'type']
    ordering = ('-created',)
    list_display = ('id', 'created', 'is_ok', 'type')
    search_fields = ['created', ]
    list_per_page = 50
    request = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_import_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

@admin.register(Reference)
class ReferenceClassAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    search_fields = ['name', 'ruc', 'code', 'email', 'user_reference__first_name', 'user_reference__last_name',
                     'user_reference__document_number', 'user_reference__username']
    list_display = ('id', 'name', 'active', 'ruc', 'code')
    list_export = ('xls', 'csv', 'json', 'csv')
    list_filter = [
                   ('executive_reference__user', RelatedOnlyFieldListFilter),
                   ('created', DateRangeFilter), 'active']
    inlines = (UserInline, ReferenceUserAdminInline, ReferenceExecutiveUserAdminInline)
    resource_class = ReferenceExportResource
    history_list_display = ["changed_fields","list_changes"]

    class Media:
        js = ('js/references.js',)

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = ('created', )

        if obj is not None:
            if request.user.type == 'Referencia' and not request.user.is_superuser:
                self.readonly_fields = self.readonly_fields + ('active', 'motive')

            if User.objects.filter(references=obj.id).first() or ReferenceAdmin.objects.filter(reference=obj.code).first() or ReferenceExecutive.objects.filter(reference=obj.code).first():
                self.readonly_fields = ('code', )
        
        # return self.readonly_fields
        self.readonly_fields = ('name', 'ruc', 'code', 'phone', 'email', 'address', 'description_siglo',
                                'name_manager', 'last_name_manager', 'document_type_manager', 'document_number_manager',
                                'active', 'motive')
        return self.readonly_fields

    def get_inlines(self, request, obj=None):
        if not obj:
            inlines = []
        else:
            inlines = [UserInline, ReferenceUserAdminInline, ReferenceExecutiveUserAdminInline]
        return inlines

    def get_queryset(self, request):
        from itertools import chain

        qs = super(ReferenceClassAdmin, self).get_queryset(request)
        ref_admin = ReferenceAdmin.objects.filter(user=request.user.id).values_list('reference__id', flat=True)
        ref_exec = ReferenceExecutive.objects.filter(user=request.user.id).values_list('reference__id', flat=True)
        ref_assoc = request.user.references.values_list('id', flat=True)

        ids_list = chain(ref_admin, ref_exec, ref_assoc, [request.user.origenes.id if request.user.origenes else 0])

        if not request.user.is_superuser and request.user.type == 'Referencia':
            if ids_list:
                qs = qs.filter(id__in=ids_list)
        else:
            pass

        return qs

    def save_model(self, request, obj, form, change):
        if change and form.changed_data and 'active' in form.changed_data:
            """ Send mail """
            references_emails = ReferenceAdmin.objects.filter(reference__id=obj.id).values_list('user__email', flat=True)

            if references_emails:
                mail = EmailMultiAlternatives(
                    subject="La referencia {0} cambió de estado".format(obj.name),
                    bcc=tuple(references_emails),
                    body=render_to_string("emails/change_active_reference.html", {"data": obj})
                )
                mail.content_subtype = 'html'
                mail.send()

        return super(ReferenceClassAdmin, self).save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_import_permission(self, request):
        return False

    def has_add_permission(self, request):
        return False

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return delta.changed_fields
        return None

    def list_changes(self, obj):
        fields = ""
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)

            for change in delta.changes:
                fields += str("<strong>{}</strong> changed from <span style='background-color:#ffb5ad'>{}</span> to <span style='background-color:#b3f7ab'>{}</span> . <br/>".format(change.field, change.old, change.new))
            return format_html(fields)
        return None