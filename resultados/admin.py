from django.contrib import admin

from .models import AsignacionMeta, Meta, Trimestre


@admin.register(Meta)
class MetaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'unidad_medida', 'activo')
    search_fields = ('codigo', 'nombre')
    list_filter = ('activo', 'tipo')


@admin.register(Trimestre)
class TrimestreAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'anio', 'numero', 'activo')
    search_fields = ('codigo', 'nombre')
    list_filter = ('anio', 'numero', 'activo')


@admin.register(AsignacionMeta)
class AsignacionMetaAdmin(admin.ModelAdmin):
    list_display = ('id', 'funcionario', 'meta', 'trimestre', 'cantidad_objetivo', 'ponderacion', 'activo')
    list_filter = ('trimestre', 'activo')
    search_fields = ('funcionario__usuario__username', 'meta__nombre')
