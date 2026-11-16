from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from .models import (
    Cargo, Delegacion, JuntaVecinos, ParticipacionJunta,
    PerfilUsuario, Rol, Territorio, Vecino,
)


class OrganizacionModelosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.delegacion = Delegacion.objects.create(
            codigo='DEL-01', nombre='Delegación ficticia', direccion='Calle de prueba 1',
        )
        cls.otra_delegacion = Delegacion.objects.create(
            codigo='DEL-02', nombre='Otra delegación ficticia',
        )
        cls.territorio = Territorio.objects.create(
            codigo='TER-01', nombre='Territorio ficticio', delegacion=cls.delegacion,
        )
        cls.rol = Rol.objects.create(codigo='ROL-PRUEBA', nombre='Rol de prueba')
        cls.cargo = Cargo.objects.create(codigo='CAR-01', nombre='Cargo ficticio')
        cls.usuario = get_user_model().objects.create_user(
            username='funcionario_prueba', password='solo-pruebas-123',
            first_name='Nombre', last_name='Prueba', email='funcionario@example.test',
        )
        cls.perfil = PerfilUsuario.objects.create(
            usuario=cls.usuario, rol=cls.rol, delegacion=cls.delegacion,
            cargo=cls.cargo, rut='FICTICIO-01',
        )
        cls.vecino = Vecino.objects.create(
            rut='FICTICIO-02', nombres='Vecino', apellidos='Ficticio',
            telefono='999999999', correo='vecino@example.test', direccion='Calle de prueba 2',
            territorio=cls.territorio,
        )
        cls.junta = JuntaVecinos.objects.create(
            codigo='JUN-01', nombre='Junta ficticia', direccion='Calle de prueba 3',
            delegacion=cls.delegacion, territorio=cls.territorio,
            fecha_constitucion=date(2025, 1, 1),
        )

    def test_campos_funcionario_desde_user_django(self):
        self.assertEqual(self.perfil.nombres, 'Nombre')
        self.assertEqual(self.perfil.correo, 'funcionario@example.test')
        self.assertTrue(self.perfil.activo)
        self.assertEqual(self.perfil.ultimo_acceso, self.usuario.last_login)

    def test_junta_rechaza_territorio_de_otra_delegacion(self):
        junta = JuntaVecinos(
            codigo='JUN-02', nombre='Junta incoherente', direccion='Calle 4',
            delegacion=self.otra_delegacion, territorio=self.territorio,
            fecha_constitucion=date(2025, 1, 2),
        )
        with self.assertRaises(ValidationError):
            junta.full_clean()

    def test_participacion_de_dirigente_exige_cargo(self):
        participacion = ParticipacionJunta(
            vecino=self.vecino, junta=self.junta, es_dirigente=True,
            fecha_incorporacion=date(2025, 1, 2),
        )
        with self.assertRaises(ValidationError):
            participacion.full_clean()
        participacion.cargo = 'Secretario'
        participacion.full_clean()

    def test_relacion_protegida_no_permite_borrar_territorio(self):
        with self.assertRaises(ProtectedError):
            self.territorio.delete()

    def test_delegado_pertenece_a_delegacion(self):
        self.otra_delegacion.delegado = self.perfil
        with self.assertRaises(ValidationError):
            self.otra_delegacion.full_clean()
