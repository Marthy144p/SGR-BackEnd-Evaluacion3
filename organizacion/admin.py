
from django.contrib import admin
from .models import Delegacion, Rol, PerfilUsuario


# -----------------------------------------
# ADMINISTRACIÓN DE DELEGACIONES
# -----------------------------------------

@admin.register(Delegacion)
class DelegacionAdmin(admin.ModelAdmin):

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


# -----------------------------------------
# ADMINISTRACIÓN DE ROLES
# -----------------------------------------

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre',
        'descripcion',
        'activo',
    )

    search_fields = (
        'nombre',
        'descripcion',
    )

    list_filter = (
        'activo',
    )

    ordering = (
        'nombre',
    )

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'usuario',
        'rol',
        'delegacion',
    )

    search_fields = (
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'rol__nombre',
        'delegacion__nombre',
    )

    list_filter = (
        'rol',
        'delegacion',
    )

    ordering = (
        'usuario__username',
    )

    list_select_related = (
        'usuario',
        'rol',
        'delegacion',
    )

# Registros adicionales de la Evaluación 3 para inspeccionar modelos en el paso 1.
# Django Admin NO reemplaza el CRUD web propio exigido en el paso 2.
from .models import Cargo, Territorio, Vecino, JuntaVecinos, ParticipacionJunta


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo')
    search_fields = ('codigo', 'nombre')
    list_filter = ('activo',)


@admin.register(Territorio)
class TerritorioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'delegacion', 'activo')
    search_fields = ('codigo', 'nombre', 'delegacion__nombre')
    list_filter = ('delegacion', 'activo')


@admin.register(Vecino)
class VecinoAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombres', 'apellidos', 'territorio', 'activo')
    search_fields = ('rut', 'nombres', 'apellidos')
    list_filter = ('territorio', 'activo')


@admin.register(JuntaVecinos)
class JuntaVecinosAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'delegacion', 'territorio', 'activo')
    search_fields = ('codigo', 'nombre')
    list_filter = ('delegacion', 'territorio', 'activo')


@admin.register(ParticipacionJunta)
class ParticipacionJuntaAdmin(admin.ModelAdmin):
    list_display = ('vecino', 'junta', 'es_dirigente', 'cargo', 'activo')
    search_fields = ('vecino__nombres', 'vecino__apellidos', 'junta__nombre')
    list_filter = ('junta', 'es_dirigente', 'activo')
