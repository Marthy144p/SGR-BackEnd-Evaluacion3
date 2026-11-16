"""Comprobaciones funcionales de las 17 entidades y seguridad HTTP (sin AWS)."""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.exceptions import ValidationError

from gestion.forms import formulario_para
from gestion.registro import RECURSOS


class FlujoIntegradoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_demo_sgr', verbosity=0, silencioso=True)
        cls.consulta = get_user_model().objects.get(username='sgr_demo_consulta')
        cls.gestion = get_user_model().objects.get(username='sgr_demo_gestion')

    def _valores_edicion(self, recurso, obj):
        Form = formulario_para(recurso.clase)
        formulario = Form(instance=obj)
        datos = {}
        for nombre in formulario.fields:
            value = formulario[nombre].value()
            if value is None:
                continue
            if isinstance(value, (list, tuple)):
                datos[nombre] = [str(v) for v in value]
            elif isinstance(value, bool):
                if value:
                    datos[nombre] = 'on'
            else:
                datos[nombre] = str(value)
        if obj._meta.model_name == 'perfilusuario':
            u = obj.usuario
            datos.update({'username':u.username, 'nombres':u.first_name, 'apellidos':u.last_name,
                          'correo':u.email, 'activo_funcionario':'on'})
        return datos

    def _valores_creacion(self, recurso, obj):
        datos = self._valores_edicion(recurso, obj)
        campo_nuevo = f'TEST-{recurso.slug[:5].upper()}-99'
        if 'codigo' in datos:
            datos['codigo'] = campo_nuevo
        if 'nombre' in datos:
            datos['nombre'] = f'Registro {campo_nuevo}'
        if 'rut' in datos:
            datos['rut'] = f'FICT-T-{recurso.slug[:4]}'
        if recurso.slug == 'delegaciones':
            datos.pop('delegado', None)  # Primero se crea la delegación; luego se vincula su delegado.
        if recurso.slug == 'funcionarios':
            datos.update({'username':'usuario_demo_nuevo99', 'clave':'ClavePruebaRobusta#99',
                          'confirmar_clave':'ClavePruebaRobusta#99', 'activo_funcionario':'on'})
        if recurso.slug == 'trimestres':
            datos['anio'] = '2027'
        return datos

    def test_cobertura_exacta_17_y_datos_demo(self):
        self.assertEqual(len(RECURSOS), 17)
        for r in RECURSOS:
            with self.subTest(r=r.slug):
                self.assertGreaterEqual(r.clase.objects.count(), 2, r.titulo)

    def test_navegacion_y_consulta_17_sin_mantenimiento(self):
        cliente = Client()
        cliente.force_login(self.consulta)
        self.assertEqual(cliente.get(reverse('inicio')).status_code, 200)
        for r in RECURSOS:
            obj = r.clase.objects.first()
            with self.subTest(r=r.slug):
                self.assertEqual(cliente.get(reverse('gestion:lista', args=[r.slug])).status_code, 200)
                self.assertEqual(cliente.get(reverse('gestion:detalle', args=[r.slug, obj.pk])).status_code, 200)
                self.assertEqual(cliente.get(reverse('gestion:crear', args=[r.slug])).status_code, 403)
                self.assertEqual(cliente.get(reverse('gestion:editar', args=[r.slug, obj.pk])).status_code, 403)
                self.assertEqual(cliente.post(reverse('gestion:eliminar', args=[r.slug, obj.pk])).status_code, 403)

    def test_visitante_login_directo_y_logout_post(self):
        cliente = Client()
        r = RECURSOS[0]
        url = reverse('gestion:lista', args=[r.slug])
        self.assertEqual(cliente.get(url).status_code, 302)
        self.assertIn('login', cliente.get(url)['Location'])
        self.assertEqual(cliente.post(reverse('login'), {'username':'noexiste','password':'noexiste'}).status_code, 200)
        cliente.force_login(self.consulta)
        self.assertEqual(cliente.get(reverse('logout')).status_code, 405)
        self.assertEqual(cliente.post(reverse('logout')).status_code, 302)
        self.assertEqual(cliente.get(url).status_code, 302)

    def test_gestion_crud_17_y_cancelacion(self):
        cliente = Client()
        cliente.force_login(self.gestion)
        for r in RECURSOS:
            with self.subTest(r=r.slug):
                obj = r.clase.objects.order_by('pk').first()
                original_pk = obj.pk
                url_edicion = reverse('gestion:editar', args=[r.slug, original_pk])
                self.assertEqual(cliente.get(url_edicion).status_code, 200)
                datos = self._valores_edicion(r, obj)
                resp = cliente.post(url_edicion, datos)
                self.assertEqual(resp.status_code, 302, resp.context['formulario'].errors.as_json() if resp.status_code == 200 else '')
                self.assertTrue(r.clase.objects.filter(pk=original_pk).exists())
                # POST con campos obligatorios vacíos no puede modificar el registro.
                resp = cliente.post(url_edicion, {})
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(r.clase.objects.filter(pk=original_pk).exists())
                datos = self._valores_creacion(r, obj)
                resp = cliente.post(reverse('gestion:crear', args=[r.slug]), datos)
                self.assertEqual(resp.status_code, 302, f"{r.slug}: {resp.context['formulario'].errors.as_json() if resp.status_code == 200 else ''}")
                nuevo = r.clase.objects.order_by('-pk').first()
                self.assertNotEqual(nuevo.pk, original_pk)
                link = reverse('gestion:eliminar', args=[r.slug, nuevo.pk])
                valor_antes = (nuevo.usuario.is_active if nuevo._meta.model_name == 'perfilusuario' else getattr(nuevo, 'activo', getattr(nuevo, 'estado', None)))
                self.assertEqual(cliente.get(link).status_code, 200)
                nuevo.refresh_from_db()
                valor_despues = (nuevo.usuario.is_active if nuevo._meta.model_name == 'perfilusuario' else getattr(nuevo, 'activo', getattr(nuevo, 'estado', None)))
                self.assertEqual(valor_antes, valor_despues, f'La confirmación GET modificó {r.slug}')
                self.assertEqual(cliente.post(link).status_code, 302)
                nuevo.refresh_from_db()
                if nuevo._meta.model_name == 'perfilusuario':
                    self.assertFalse(nuevo.usuario.is_active)
                elif hasattr(nuevo, 'activo'):
                    self.assertFalse(nuevo.activo)
                else:
                    self.assertIn(nuevo.estado, ('anulada','anulado'))

    def test_404_y_csrf_en_formularios(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.gestion)
        r = RECURSOS[0]
        self.assertEqual(cliente.get(reverse('gestion:detalle', args=[r.slug, 987654])).status_code, 404)
        obj = r.clase.objects.first()
        self.assertEqual(cliente.post(reverse('gestion:eliminar', args=[r.slug, obj.pk])).status_code, 403)
        obj.refresh_from_db()
        self.assertTrue(obj.activo)

    def test_sin_autoasignacion_de_privilegios(self):
        f = formulario_para(RECURSOS[2].clase)()
        self.assertFalse({'is_superuser','is_staff','groups','user_permissions','usuario'} & set(f.fields))
        f = formulario_para(RECURSOS[4].clase)()
        self.assertNotIn('grupo', f.fields)

    def test_cuenta_sin_grupo_no_puede_consultar(self):
        sin_permiso = get_user_model().objects.create_user('sin_grupo_demo', password='PruebaSegura!23')
        client = Client()
        client.force_login(sin_permiso)
        for r in RECURSOS:
            with self.subTest(r=r.slug):
                self.assertEqual(client.get(reverse('gestion:lista', args=[r.slug])).status_code, 403)

    def test_carga_demo_es_idempotente(self):
        antes = {r.slug: r.clase.objects.count() for r in RECURSOS}
        call_command('cargar_demo_sgr', verbosity=0, silencioso=True)
        despues = {r.slug: r.clase.objects.count() for r in RECURSOS}
        self.assertEqual(antes, despues)

    def test_prototipo_heredado_exige_sesion(self):
        client = Client()
        for url in ('/prototipo/organizacion/', '/prototipo/actividades/', '/prototipo/agenda/', '/prototipo/resultados/'):
            with self.subTest(url=url):
                respuesta = client.get(url)
                self.assertEqual(respuesta.status_code, 302)
                self.assertIn('login', respuesta['Location'])
