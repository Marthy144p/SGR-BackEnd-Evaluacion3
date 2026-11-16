"""Registro explícito de las 17 entidades exigidas (Item no forma parte)."""
from dataclasses import dataclass
from django.apps import apps
from django.http import Http404


@dataclass(frozen=True)
class Recurso:
    slug: str
    aplicacion: str
    modelo: str
    area: str
    titulo: str
    descripcion: str

    @property
    def clase(self):
        return apps.get_model(self.aplicacion, self.modelo)

    def permiso(self, accion):
        modelo = self.clase
        return f'{modelo._meta.app_label}.{accion}_{modelo._meta.model_name}'


RECURSOS = (
    Recurso('delegaciones', 'organizacion', 'Delegacion', 'organizacion', 'Delegaciones', 'Sedes municipales y delegados'),
    Recurso('territorios', 'organizacion', 'Territorio', 'organizacion', 'Territorios', 'Sectores vinculados a delegaciones'),
    Recurso('funcionarios', 'organizacion', 'PerfilUsuario', 'organizacion', 'Usuarios funcionarios', 'Cuentas Django, cargos y roles'),
    Recurso('cargos', 'organizacion', 'Cargo', 'organizacion', 'Cargos', 'Funciones laborales'),
    Recurso('roles', 'organizacion', 'Rol', 'organizacion', 'Roles', 'Catálogo funcional; grupos controlados por Admin'),
    Recurso('vecinos', 'organizacion', 'Vecino', 'organizacion', 'Vecinos', 'Solicitantes y su territorio'),
    Recurso('juntas', 'organizacion', 'JuntaVecinos', 'organizacion', 'Juntas de vecinos', 'Organizaciones comunitarias'),
    Recurso('participaciones', 'organizacion', 'ParticipacionJunta', 'organizacion', 'Participaciones en junta', 'Membresías y dirigentes'),
    Recurso('hitos', 'agenda', 'Hito', 'agenda', 'Hitos', 'Fechas, territorios y responsables'),
    Recurso('actividades', 'actividades', 'Actividad', 'actividades', 'Actividades', 'Operaciones y avances'),
    Recurso('gestiones', 'actividades', 'GestionSocial', 'actividades', 'Gestiones sociales', 'Atenciones y beneficiarios'),
    Recurso('tipos-atencion', 'actividades', 'TipoAtencion', 'actividades', 'Tipos de atención', 'Clasificación de las atenciones'),
    Recurso('subtipos-atencion', 'actividades', 'SubAtencion', 'actividades', 'Subtipos de atención', 'Clasificación relacionada con un tipo'),
    Recurso('metas', 'resultados', 'Meta', 'resultados', 'Metas', 'Objetivos y unidades de medida'),
    Recurso('asignaciones', 'resultados', 'AsignacionMeta', 'resultados', 'Asignaciones de meta', 'Funcionario, meta y trimestre'),
    Recurso('evidencias', 'actividades', 'Evidencia', 'actividades', 'Evidencias', 'Metadatos de respaldo y verificación'),
    Recurso('trimestres', 'resultados', 'Trimestre', 'resultados', 'Trimestres', 'Períodos anuales de evaluación'),
)
RECURSOS_POR_SLUG = {recurso.slug: recurso for recurso in RECURSOS}
AREAS = {
    'organizacion': ('Organización', 'Personas, territorios y juntas de vecinos'),
    'actividades': ('Actividades', 'Solicitudes, servicios y evidencias'),
    'agenda': ('Agenda', 'Planificación de hitos y responsables'),
    'resultados': ('Resultados', 'Metas, asignaciones y trimestres'),
}


def obtener_recurso(slug):
    try:
        return RECURSOS_POR_SLUG[slug]
    except KeyError:
        raise Http404('El módulo solicitado no existe.')
