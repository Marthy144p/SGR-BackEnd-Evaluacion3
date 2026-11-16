"""Metas, trimestres y asignaciones del SGR.

El objetivo y la ponderación pertenecen a AsignacionMeta (no a Meta).
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Meta(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=100)
    unidad_medida = models.CharField(max_length=60)
    requiere_evidencia = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas'
        ordering = ['nombre']


class Trimestre(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    anio = models.PositiveSmallIntegerField('Año')
    numero = models.PositiveSmallIntegerField(
        'Número de trimestre', validators=[MinValueValidator(1), MaxValueValidator(4)],
    )
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    activo = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.fecha_inicio and self.fecha_termino and self.fecha_termino < self.fecha_inicio:
            raise ValidationError({'fecha_termino': 'No puede ser anterior a la fecha de inicio.'})

    def __str__(self):
        return f'{self.nombre} ({self.anio})'

    class Meta:
        verbose_name = 'Trimestre'
        verbose_name_plural = 'Trimestres'
        ordering = ['-anio', 'numero']
        constraints = [
            models.UniqueConstraint(fields=['anio', 'numero'], name='sgr_trimestre_anio_num_unico'),
        ]


class AsignacionMeta(models.Model):
    funcionario = models.ForeignKey(
        'organizacion.PerfilUsuario', on_delete=models.PROTECT, related_name='asignaciones_meta',
    )
    meta = models.ForeignKey(Meta, on_delete=models.PROTECT, related_name='asignaciones')
    trimestre = models.ForeignKey(
        Trimestre, on_delete=models.PROTECT, related_name='asignaciones',
    )
    cantidad_objetivo = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
    )
    ponderacion = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
    )
    fecha_asignacion = models.DateField()
    observacion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.funcionario} / {self.meta} / {self.trimestre}'

    class Meta:
        verbose_name = 'Asignación de meta'
        verbose_name_plural = 'Asignaciones de meta'
        ordering = ['-fecha_asignacion']
