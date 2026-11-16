"""Catálogos, funcionarios y organización territorial del SGR.

La ampliación conserva Delegacion, Rol y PerfilUsuario de la Evaluación 2.
Los campos opcionales agregados a esas tres tablas permiten mantener sus filas
históricas hasta que puedan completarse con datos ficticios válidos.
"""
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models


class Delegacion(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255, blank=True)
    delegado = models.ForeignKey(
        'PerfilUsuario', on_delete=models.PROTECT, related_name='delegaciones_dirigidas',
        null=True, blank=True,
    )
    activo = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.delegado_id and self.delegado.delegacion_id != self.pk:
            raise ValidationError({'delegado': 'El delegado debe pertenecer a esta delegación.'})

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Delegación'
        verbose_name_plural = 'Delegaciones'
        ordering = ['nombre']


class Territorio(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='territorios')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Territorio'
        verbose_name_plural = 'Territorios'
        ordering = ['nombre']


class Cargo(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['nombre']


class Rol(models.Model):
    # Se completa mediante una migración de datos para los roles históricos.
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    grupo = models.OneToOneField(
        Group, on_delete=models.PROTECT, related_name='rol_sgr', null=True, blank=True,
        help_text='El grupo de Django administra los permisos reales de este rol.',
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']


class PerfilUsuario(models.Model):
    """Funcionario: conserva su cuenta, delegación y rol principal originales."""
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_sgr',
    )
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name='perfiles')
    delegacion = models.ForeignKey(
        Delegacion, on_delete=models.PROTECT, related_name='perfiles',
    )
    rut = models.CharField(
        'RUT ficticio', max_length=15, unique=True, null=True, blank=True,
        help_text='Dejar vacío en los perfiles históricos hasta completar sus datos.',
    )
    cargo = models.ForeignKey(
        Cargo, on_delete=models.PROTECT, related_name='funcionarios',
        null=True, blank=True,
    )
    roles = models.ManyToManyField(
        Rol, related_name='funcionarios_con_rol', blank=True,
        help_text='Roles adicionales. El campo rol conserva el rol principal de Evaluación 2.',
    )

    @property
    def nombres(self):
        return self.usuario.first_name

    @property
    def apellidos(self):
        return self.usuario.last_name

    @property
    def correo(self):
        return self.usuario.email

    @property
    def ultimo_acceso(self):
        return self.usuario.last_login

    @property
    def activo(self):
        return self.usuario.is_active

    def __str__(self):
        return f'Perfil de {self.usuario.username}'

    class Meta:
        verbose_name = 'Usuario funcionario (perfil)'
        verbose_name_plural = 'Usuarios funcionarios (perfiles)'
        ordering = ['usuario__username']


class Vecino(models.Model):
    rut = models.CharField('RUT ficticio', max_length=15, unique=True)
    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    telefono = models.CharField(max_length=25)
    correo = models.EmailField()
    direccion = models.CharField(max_length=255)
    territorio = models.ForeignKey(
        Territorio, on_delete=models.PROTECT, related_name='vecinos',
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'

    class Meta:
        verbose_name = 'Vecino'
        verbose_name_plural = 'Vecinos'
        ordering = ['apellidos', 'nombres']


class JuntaVecinos(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255)
    delegacion = models.ForeignKey(
        Delegacion, on_delete=models.PROTECT, related_name='juntas_vecinos',
    )
    territorio = models.ForeignKey(
        Territorio, on_delete=models.PROTECT, related_name='juntas_vecinos',
    )
    fecha_constitucion = models.DateField()
    activo = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.territorio_id and self.delegacion_id:
            if self.territorio.delegacion_id != self.delegacion_id:
                raise ValidationError({'territorio': 'El territorio no pertenece a la delegación.'})

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Junta de vecinos'
        verbose_name_plural = 'Juntas de vecinos'
        ordering = ['nombre']


class ParticipacionJunta(models.Model):
    vecino = models.ForeignKey(
        Vecino, on_delete=models.PROTECT, related_name='participaciones',
    )
    junta = models.ForeignKey(
        JuntaVecinos, on_delete=models.PROTECT, related_name='participaciones',
    )
    es_dirigente = models.BooleanField(default=False)
    cargo = models.CharField(
        'Cargo en la junta', max_length=100, blank=True,
        help_text='Por ejemplo, presidente o secretario; no es el cargo laboral del funcionario.',
    )
    fecha_incorporacion = models.DateField()
    activo = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.vecino_id and self.junta_id:
            if self.vecino.territorio_id != self.junta.territorio_id:
                raise ValidationError({'junta': 'La junta debe corresponder al territorio del vecino.'})
        if self.es_dirigente and not self.cargo.strip():
            raise ValidationError({'cargo': 'Indica el cargo del dirigente en la junta.'})

    def __str__(self):
        return f'{self.vecino} - {self.junta}'

    class Meta:
        verbose_name = 'Participación en junta'
        verbose_name_plural = 'Participaciones en junta'
        ordering = ['-fecha_incorporacion']
