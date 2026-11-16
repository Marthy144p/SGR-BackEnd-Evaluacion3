
from django.contrib import admin
from .models import Item, TipoAtencion, SubAtencion

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'codigo',
        'nombre',
        'descripcion',
        'activo',
    )

    search_fields = (
        'codigo',
        'nombre',
        'descripcion',
    )

    list_filter = (
        'activo',
    )

    ordering = (
        'nombre',
    )

@admin.register(TipoAtencion)
class TipoAtencionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'codigo',
        'nombre',
        'activo',
    )

    search_fields = (
        'codigo',
        'nombre',
    )

    list_filter = (
        'activo',
    )

    ordering = (
        'nombre',
    )

@admin.register(SubAtencion)
class SubAtencionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'codigo',
        'nombre',
        'tipo_atencion',
        'activo',
    )

    search_fields = (
        'codigo',
        'nombre',
        'tipo_atencion__nombre',
    )

    list_filter = (
        'tipo_atencion',
        'activo',
    )

    ordering = (
        'nombre',
    )

    list_select_related = (
        'tipo_atencion',
    )

# Registros administrativos provisionales para revisar las relaciones del paso 1.
# En el paso 2 se desarrollan listados, formularios y detalles propios.
from .models import Actividad, GestionSocial, Evidencia


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'funcionario', 'territorio', 'estado', 'avance')
    list_filter = ('estado', 'territorio', 'tipo')
    search_fields = ('descripcion', 'origen', 'funcionario__usuario__username')


@admin.register(GestionSocial)
class GestionSocialAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_ingreso', 'beneficiario', 'tipo_atencion', 'estado')
    list_filter = ('estado', 'tipo_atencion')
    search_fields = ('beneficiario__nombres', 'beneficiario__apellidos', 'beneficio')


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'tipo', 'autor', 'fecha', 'estado')
    list_filter = ('estado', 'tipo')
    search_fields = ('codigo', 'referencia')
