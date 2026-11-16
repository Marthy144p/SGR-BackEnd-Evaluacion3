from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from organizacion.models import Delegacion, PerfilUsuario, Rol
from .models import AsignacionMeta, Meta, Trimestre


class ResultadosModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        delegacion = Delegacion.objects.create(codigo='D1', nombre='Delegación')
        rol = Rol.objects.create(codigo='R1', nombre='Rol')
        usuario = get_user_model().objects.create_user(username='user1', password='solo-test')
        cls.perfil = PerfilUsuario.objects.create(usuario=usuario, delegacion=delegacion, rol=rol)
        cls.meta = Meta.objects.create(
            codigo='M1', nombre='Meta ficticia', tipo='Social', unidad_medida='Gestiones',
        )
        cls.trimestre = Trimestre.objects.create(
            codigo='T1', nombre='Primer trimestre', anio=2026, numero=1,
            fecha_inicio=date(2026, 1, 1), fecha_termino=date(2026, 3, 31),
        )

    def test_numero_trimestre_entre_uno_y_cuatro(self):
        self.trimestre.numero = 5
        with self.assertRaises(ValidationError):
            self.trimestre.full_clean()

    def test_asignacion_valida_metas_positivas_y_ponderacion(self):
        asignacion = AsignacionMeta(
            funcionario=self.perfil, meta=self.meta, trimestre=self.trimestre,
            cantidad_objetivo=Decimal('0.00'), ponderacion=Decimal('101.00'),
            fecha_asignacion=date(2026, 1, 1),
        )
        with self.assertRaises(ValidationError):
            asignacion.full_clean()
        asignacion.cantidad_objetivo = Decimal('5.00')
        asignacion.ponderacion = Decimal('100.00')
        asignacion.full_clean()
