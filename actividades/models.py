"""Operaciones SGR: actividades, gestiones, atenciones y evidencias.

Item, TipoAtencion y SubAtencion conservan sus tablas de Evaluación 2.
"""
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Q


class Item(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Ítem'
        verbose_name_plural = 'Ítems'
        ordering = ['nombre']


class TipoAtencion(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de atención'
        verbose_name_plural = 'Tipos de atención'
        ordering = ['nombre']


class SubAtencion(models.Model):
    """Modelo conservado con su nombre original; corresponde al Subtipo de atención."""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    tipo_atencion = models.ForeignKey(
        TipoAtencion, on_delete=models.PROTECT, related_name='subatenciones',
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Subtipo de atención'
        verbose_name_plural = 'Subtipos de atención'
        ordering = ['nombre']


class Actividad(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_ejecucion', 'En ejecución'),
        ('finalizada', 'Finalizada'),
        ('anulada', 'Anulada'),
    ]
    fecha = models.DateField()
    funcionario = models.ForeignKey(
        'organizacion.PerfilUsuario', on_delete=models.PROTECT, related_name='actividades_registradas',
    )
    asignacion_meta = models.ForeignKey(
        'resultados.AsignacionMeta', on_delete=models.PROTECT, related_name='actividades',
    )
    hito = models.ForeignKey(
        'agenda.Hito', on_delete=models.PROTECT, related_name='actividades',
        null=True, blank=True,
    )
    tipo = models.CharField(max_length=100)
    descripcion = models.TextField()
    origen = models.CharField(max_length=150)
    solicitante = models.ForeignKey(
        'organizacion.Vecino', on_delete=models.PROTECT, related_name='actividades_solicitadas',
        null=True, blank=True,
    )
    territorio = models.ForeignKey(
        'organizacion.Territorio', on_delete=models.PROTECT, related_name='actividades',
    )
    responsable = models.ForeignKey(
        'organizacion.PerfilUsuario', on_delete=models.PROTECT, related_name='actividades_responsable',
    )
    fecha_compromiso = models.DateField()
    apoyo = models.TextField(blank=True)
    avance = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    resultado = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if self.fecha and self.fecha_compromiso and self.fecha_compromiso < self.fecha:
            raise ValidationError({'fecha_compromiso': 'No puede ser anterior a la fecha de ingreso.'})
        if self.hito_id and self.territorio_id and self.hito.territorio_id != self.territorio_id:
            raise ValidationError({'hito': 'El hito debe pertenecer al territorio de la actividad.'})
        if self.solicitante_id and self.territorio_id:
            if self.solicitante.territorio_id != self.territorio_id:
                raise ValidationError({'solicitante': 'El solicitante no pertenece al territorio.'})
        if self.asignacion_meta_id and self.funcionario_id:
            if self.asignacion_meta.funcionario_id != self.funcionario_id:
                raise ValidationError({'asignacion_meta': 'La asignación pertenece a otro funcionario.'})

    def __str__(self):
        return f'Actividad #{self.pk or "nueva"} - {self.tipo}'

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['-fecha']


class GestionSocial(models.Model):
    ESTADOS = [
        ('ingresada', 'Ingresada'),
        ('en_atencion', 'En atención'),
        ('resuelta', 'Resuelta'),
        ('anulada', 'Anulada'),
    ]
    fecha_ingreso = models.DateField()
    fecha_atencion = models.DateField(null=True, blank=True)
    beneficiario = models.ForeignKey(
        'organizacion.Vecino', on_delete=models.PROTECT, related_name='gestiones_sociales',
    )
    tipo_atencion = models.ForeignKey(
        TipoAtencion, on_delete=models.PROTECT, related_name='gestiones_sociales',
    )
    subtipo_atencion = models.ForeignKey(
        SubAtencion, on_delete=models.PROTECT, related_name='gestiones_sociales',
    )
    asignacion_meta = models.ForeignKey(
        'resultados.AsignacionMeta', on_delete=models.PROTECT, related_name='gestiones_sociales',
    )
    visita = models.BooleanField(default=False)
    actuaciones = models.TextField(blank=True)
    derivacion = models.TextField(blank=True)
    informe = models.TextField(blank=True)
    beneficio = models.TextField(blank=True)
    resultado = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ingresada')

    def clean(self):
        super().clean()
        if self.fecha_ingreso and self.fecha_atencion and self.fecha_atencion < self.fecha_ingreso:
            raise ValidationError({'fecha_atencion': 'No puede ser anterior al ingreso.'})
        if self.tipo_atencion_id and self.subtipo_atencion_id:
            if self.subtipo_atencion.tipo_atencion_id != self.tipo_atencion_id:
                raise ValidationError({'subtipo_atencion': 'El subtipo no corresponde al tipo seleccionado.'})

    def __str__(self):
        return f'Gestión #{self.pk or "nueva"} de {self.beneficiario}'

    class Meta:
        verbose_name = 'Gestión social'
        verbose_name_plural = 'Gestiones sociales'
        ordering = ['-fecha_ingreso']


class Evidencia(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('verificada', 'Verificada'),
        ('rechazada', 'Rechazada'),
        ('anulada', 'Anulada'),
    ]
    codigo = models.CharField(max_length=20, unique=True)
    actividad = models.ForeignKey(
        Actividad, on_delete=models.PROTECT, related_name='evidencias', null=True, blank=True,
    )
    gestion_social = models.ForeignKey(
        GestionSocial, on_delete=models.PROTECT, related_name='evidencias', null=True, blank=True,
    )
    tipo = models.CharField(max_length=100)
    referencia = models.CharField(
        max_length=255, help_text='Ubicación o nombre de archivo ficticio; no se exige carga real.',
    )
    autor = models.ForeignKey(
        'organizacion.PerfilUsuario', on_delete=models.PROTECT, related_name='evidencias_autor',
    )
    fecha = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    observacion = models.TextField(blank=True)
    verificador = models.ForeignKey(
        'organizacion.PerfilUsuario', on_delete=models.PROTECT,
        related_name='evidencias_verificador', null=True, blank=True,
    )

    def clean(self):
        super().clean()
        if bool(self.actividad_id) == bool(self.gestion_social_id):
            raise ValidationError('La evidencia debe relacionarse exactamente con una actividad o una gestión social.')

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'
        ordering = ['-fecha']
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(actividad__isnull=False, gestion_social__isnull=True)
                    | Q(actividad__isnull=True, gestion_social__isnull=False)
                ),
                name='sgr_evidencia_un_solo_origen',
            ),
        ]
