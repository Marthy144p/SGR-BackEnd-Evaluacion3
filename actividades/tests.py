from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from agenda.models import Hito
from organizacion.models import Delegacion, PerfilUsuario, Rol, Territorio, Vecino
from resultados.models import AsignacionMeta, Meta, Trimestre
from .models import Actividad, Evidencia, GestionSocial, SubAtencion, TipoAtencion


class ActividadesModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        delegacion = Delegacion.objects.create(codigo='D1', nombre='Delegación ficticia')
        cls.territorio = Territorio.objects.create(
            codigo='T1', nombre='Territorio ficticio', delegacion=delegacion,
        )
        rol = Rol.objects.create(codigo='R1', nombre='Rol ficticio')
        user = get_user_model().objects.create_user(username='user1', password='solo-test')
        cls.perfil = PerfilUsuario.objects.create(usuario=user, delegacion=delegacion, rol=rol)
        cls.vecino = Vecino.objects.create(
            rut='FICTICIO-10', nombres='Vecino', apellidos='Prueba', telefono='123456',
            correo='vecino@example.test', direccion='Dirección ficticia', territorio=cls.territorio,
        )
        meta = Meta.objects.create(codigo='M1', nombre='Meta', tipo='Social', unidad_medida='Cantidad')
        trimestre = Trimestre.objects.create(
            codigo='TR1', nombre='Trimestre uno', anio=2026, numero=1,
            fecha_inicio=date(2026, 1, 1), fecha_termino=date(2026, 3, 31),
        )
        cls.asignacion = AsignacionMeta.objects.create(
            funcionario=cls.perfil, meta=meta, trimestre=trimestre,
            cantidad_objetivo=Decimal('3.00'), ponderacion=Decimal('50.00'),
            fecha_asignacion=date(2026, 1, 2),
        )
        cls.hito = Hito.objects.create(
            codigo='H1', nombre='Hito ficticio', periodicidad='unica',
            fecha_inicio=date(2026, 1, 1), fecha_termino=date(2026, 2, 28),
            delegacion=delegacion, territorio=cls.territorio,
        )
        cls.tipo = TipoAtencion.objects.create(codigo='TIP1', nombre='Atención social')
        cls.subtipo = SubAtencion.objects.create(
            codigo='SUB1', nombre='Consulta', tipo_atencion=cls.tipo,
        )
        cls.actividad = Actividad.objects.create(
            fecha=date(2026, 1, 10), funcionario=cls.perfil,
            asignacion_meta=cls.asignacion, hito=cls.hito, tipo='Visita',
            descripcion='Actividad ficticia', origen='Interno', solicitante=cls.vecino,
            territorio=cls.territorio, responsable=cls.perfil,
            fecha_compromiso=date(2026, 1, 12), avance=10,
        )

    def test_actividad_no_acepta_compromiso_anterior(self):
        actividad = self.actividad
        actividad.fecha_compromiso = date(2026, 1, 1)
        with self.assertRaises(ValidationError):
            actividad.full_clean()

    def test_subtipo_corresponde_al_tipo(self):
        otro_tipo = TipoAtencion.objects.create(codigo='TIP2', nombre='Otro tipo')
        gestion = GestionSocial(
            fecha_ingreso=date(2026, 1, 10), beneficiario=self.vecino,
            tipo_atencion=otro_tipo, subtipo_atencion=self.subtipo,
            asignacion_meta=self.asignacion,
        )
        with self.assertRaises(ValidationError):
            gestion.full_clean()
        gestion.tipo_atencion = self.tipo
        gestion.full_clean()

    def test_evidencia_tiene_un_solo_origen(self):
        evidencia = Evidencia(
            codigo='E1', tipo='Fotografía', referencia='archivo-ficticio.jpg',
            autor=self.perfil, fecha=date(2026, 1, 10),
        )
        with self.assertRaises(ValidationError):
            evidencia.full_clean()
        evidencia.actividad = self.actividad
        evidencia.full_clean()
        evidencia.gestion_social = GestionSocial.objects.create(
            fecha_ingreso=date(2026, 1, 10), beneficiario=self.vecino,
            tipo_atencion=self.tipo, subtipo_atencion=self.subtipo,
            asignacion_meta=self.asignacion,
        )
        with self.assertRaises(ValidationError):
            evidencia.full_clean()
