from django.contrib import admin

from .models import Hito


@admin.register(Hito)
class HitoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'periodicidad', 'fecha_inicio', 'fecha_termino', 'estado')
    search_fields = ('codigo', 'nombre')
    list_filter = ('estado', 'periodicidad', 'delegacion')
    filter_horizontal = ('responsables',)
