"""Grupos Django Consulta y Gestión; solo ejecutar desde la consola administradora."""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction
from gestion.registro import RECURSOS
from organizacion.models import Rol


class Command(BaseCommand):
    help = 'Configura permisos Django para Consulta (ver) y Gestión (CRUD).'

    @transaction.atomic
    def handle(self, *args, **options):
        consulta, _ = Group.objects.get_or_create(name='Consulta')
        gestion, _ = Group.objects.get_or_create(name='Gestión')
        consulta_permisos, gestion_permisos = [], []
        for r in RECURSOS:
            content_type = r.clase._meta.app_label
            nombre = r.clase._meta.model_name
            p = list(Permission.objects.filter(
                content_type__app_label=content_type,
                content_type__model=nombre,
                codename__in=[f'{a}_{nombre}' for a in ('view', 'add', 'change', 'delete')],
            ))
            if len(p) != 4:
                raise ValueError(f'Faltan permisos de {r.titulo}; ejecuta migrate primero.')
            gestion_permisos.extend(p)
            consulta_permisos.extend([x for x in p if x.codename.startswith('view_')])
        consulta.permissions.set(consulta_permisos)
        gestion.permissions.set(gestion_permisos)
        for codigo, nombre, grupo in [('ROL-CONSULTA', 'Consulta SGR', consulta), ('ROL-GESTION', 'Gestión SGR', gestion)]:
            rol = Rol.objects.filter(codigo=codigo).first()
            if rol is None:
                # Puede existir un rol histórico con el mismo nombre y otro código.
                rol = Rol.objects.filter(nombre=nombre).first()
            if rol is None:
                rol = Rol.objects.create(codigo=codigo, nombre=nombre)
            if rol.nombre == nombre:
                rol.grupo = grupo
                rol.save(update_fields=['grupo'])
            else:
                raise ValueError(f'Código reservado {codigo} usado por otro rol; revisar manualmente.')
        self.stdout.write(self.style.SUCCESS('Permisos de los 17 módulos configurados para Consulta y Gestión.'))
