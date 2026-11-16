"""Carga FICTICIA, reproducible e idempotente de las 17 entidades.

No elimina ni modifica datos municipales previos. Usa el prefijo DEMO-E3.
Las contraseñas no se incluyen en el código ni en el ZIP.
"""
import os
import secrets
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from organizacion.models import (
    Cargo, Delegacion, PerfilUsuario, Rol, Territorio, Vecino,
    JuntaVecinos, ParticipacionJunta,
)
from resultados.models import Meta, Trimestre, AsignacionMeta
from agenda.models import Hito
from actividades.models import TipoAtencion, SubAtencion, Actividad, GestionSocial, Evidencia


class Command(BaseCommand):
    help = 'Crea dos ejemplos ficticios de cada entidad; cuentas Consulta y Gestión sin publicar contraseñas.'

    def add_arguments(self, parser):
        parser.add_argument('--restablecer-claves', action='store_true', help='Restablece las claves SOLO de las cuentas demo.')
        parser.add_argument('--silencioso', action='store_true', help='No imprime contraseñas en la consola (solo para pruebas automatizadas).')

    @transaction.atomic
    def handle(self, *args, **options):
        call_command('preparar_permisos_sgr', stdout=self.stdout)
        User = get_user_model()
        grupos = {'consulta': Group.objects.get(name='Consulta'), 'gestion': Group.objects.get(name='Gestión')}
        accesos = {}
        for i, tipo in enumerate(('consulta', 'gestion'), 1):
            username = f'sgr_demo_{tipo}'
            usuario, creado = User.objects.get_or_create(username=username, defaults={
                'first_name': f'Demo {tipo.capitalize()}', 'last_name': 'Ficticio',
                'email': f'{tipo}@example.test', 'is_active': True,
                'is_staff': False, 'is_superuser': False,
            })
            if usuario.is_staff or usuario.is_superuser:
                raise ValueError('Cuenta demo con privilegios administrativos inesperados: cancela.')
            clave_env = os.environ.get(f'SGR_{tipo.upper()}_PASSWORD')
            if creado or options['restablecer_claves']:
                clave = clave_env or secrets.token_urlsafe(16)
                usuario.set_password(clave)
                usuario.is_active = True
                usuario.save(update_fields=['password', 'is_active'])
                accesos[username] = clave
            usuario.groups.set([grupos[tipo]])
        datos = []
        for i in (1, 2):
            cod = f'DEMO-E3-{i}'
            d, _ = Delegacion.objects.get_or_create(codigo=f'DEL-{cod}', defaults={
                'nombre': f'Delegación ficticia {i}', 'direccion': f'Avenida Ficticia {i * 100}',
            })
            t, _ = Territorio.objects.get_or_create(codigo=f'TER-{cod}', defaults={
                'nombre': f'Territorio de prueba {i}', 'descripcion': 'Territorio ficticio', 'delegacion': d,
            })
            c, _ = Cargo.objects.get_or_create(codigo=f'CAR-{cod}', defaults={
                'nombre': f'Encargado ficticio {i}', 'descripcion': 'Rol laboral de ejemplo',
            })
            rol = Rol.objects.get(grupo=grupos['consulta' if i == 1 else 'gestion'])
            usuario = User.objects.get(username='sgr_demo_consulta' if i == 1 else 'sgr_demo_gestion')
            perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuario, defaults={
                'rol': rol, 'delegacion': d, 'cargo': c, 'rut': f'FICT-E3-F{i}',
            })
            perfil.roles.add(rol)
            if d.delegado_id is None:
                d.delegado = perfil
                d.save(update_fields=['delegado'])
            vecino, _ = Vecino.objects.get_or_create(rut=f'FICT-E3-V{i}', defaults={
                'nombres': f'Vecino Demo {i}', 'apellidos': 'Ficticio', 'telefono': f'90000000{i}',
                'correo': f'vecino{i}@example.test', 'direccion': f'Calle de prueba {i}', 'territorio': t,
                'activo': i != 2,
            })
            junta, _ = JuntaVecinos.objects.get_or_create(codigo=f'JUN-{cod}', defaults={
                'nombre': f'Junta ficticia {i}', 'direccion': f'Calle junta ficticia {i}',
                'delegacion': d, 'territorio': t, 'fecha_constitucion': date(2025, 1, i),
            })
            p, _ = ParticipacionJunta.objects.get_or_create(vecino=vecino, junta=junta, defaults={
                'es_dirigente': i == 1, 'cargo': 'Secretario' if i == 1 else '',
                'fecha_incorporacion': date(2025, 2, i),
            })
            tipo, _ = TipoAtencion.objects.get_or_create(codigo=f'TIP-{cod}', defaults={
                'nombre': f'Atención ficticia {i}', 'descripcion': 'Tipo usado en evaluación',
            })
            sub, _ = SubAtencion.objects.get_or_create(codigo=f'SUB-{cod}', defaults={
                'nombre': f'Subtipo ficticio {i}', 'tipo_atencion': tipo,
            })
            meta, _ = Meta.objects.get_or_create(codigo=f'MET-{cod}', defaults={
                'nombre': f'Meta ficticia {i}', 'descripcion': 'Meta de prueba', 'tipo': 'Gestión territorial',
                'unidad_medida': 'atenciones', 'requiere_evidencia': True,
            })
            tri, _ = Trimestre.objects.get_or_create(codigo=f'TRI-{cod}', defaults={
                'nombre': f'Trimestre de prueba {i}', 'anio': 2026, 'numero': i,
                'fecha_inicio': date(2026, 1 if i == 1 else 4, 1),
                'fecha_termino': date(2026, 3 if i == 1 else 6, 31 if i == 1 else 30),
            })
            asignacion, _ = AsignacionMeta.objects.get_or_create(
                funcionario=perfil, meta=meta, trimestre=tri, defaults={
                    'cantidad_objetivo': Decimal('10.00'), 'ponderacion': Decimal('50.00'),
                    'fecha_asignacion': date(2026, 1 if i == 1 else 4, 10),
                    'observacion': 'Asignación ficticia',
                },
            )
            hito, _ = Hito.objects.get_or_create(codigo=f'HIT-{cod}', defaults={
                'nombre': f'Hito ficticio {i}', 'descripcion': 'Planificación de prueba',
                'periodicidad': 'trimestral', 'fecha_inicio': date(2026, 1 if i == 1 else 4, 15),
                'fecha_termino': date(2026, 3 if i == 1 else 6, 15),
                'delegacion': d, 'territorio': t,
            })
            hito.responsables.add(perfil)
            actividad, _ = Actividad.objects.get_or_create(
                funcionario=perfil, asignacion_meta=asignacion, tipo=f'Actividad demo E3-{i}', defaults={
                    'fecha': date(2026, 1 if i == 1 else 4, 20), 'fecha_compromiso': date(2026, 2 if i == 1 else 5, 20),
                    'hito': hito, 'descripcion': f'Actividad ficticia {i}', 'origen': 'Prueba académica',
                    'solicitante': vecino, 'territorio': t, 'responsable': perfil,
                    'apoyo': 'Equipo de prueba', 'avance': 25 * i, 'estado': 'pendiente', 'resultado': 'Sin resultado',
                },
            )
            gestion, _ = GestionSocial.objects.get_or_create(
                beneficiario=vecino, asignacion_meta=asignacion, tipo_atencion=tipo, defaults={
                    'fecha_ingreso': date(2026, 2 if i == 1 else 5, 1),
                    'fecha_atencion': date(2026, 2 if i == 1 else 5, 5),
                    'subtipo_atencion': sub, 'visita': i == 1, 'actuaciones': 'Ejemplo de atención',
                    'derivacion': 'Ninguna', 'informe': 'Informe ficticio', 'beneficio': 'Apoyo ficticio',
                    'resultado': 'En trámite', 'estado': 'ingresada',
                },
            )
            evidencia, _ = Evidencia.objects.get_or_create(codigo=f'EVI-{cod}', defaults={
                'actividad': actividad if i == 1 else None, 'gestion_social': gestion if i == 2 else None,
                'tipo': 'Informe', 'referencia': f'documento_ficticio_{i}.pdf',
                'autor': perfil, 'fecha': date(2026, 3 if i == 1 else 6, 2),
                'observacion': 'Referencia de archivo ficticio', 'verificador': perfil,
            })
            datos.append((d,t,c,perfil,vecino,junta,p,tipo,sub,meta,tri,asignacion,hito,actividad,gestion,evidencia))
        # Todos los 17 modelos cuentan con al menos dos entradas DEMO (2 roles preexistentes del comando).
        self.stdout.write(self.style.SUCCESS('Datos ficticios de las 17 entidades creados o reutilizados.'))
        self.stdout.write('Cuentas de prueba (NO admin): sgr_demo_consulta y sgr_demo_gestion')
        if not options['silencioso']:
            for u, password in accesos.items():
                self.stdout.write(f'CLAVE GENERADA (solo esta vez) - {u}: {password}')
        if not accesos:
            self.stdout.write('Claves existentes conservadas. Usa --restablecer-claves o variables de entorno para renovarlas.')
