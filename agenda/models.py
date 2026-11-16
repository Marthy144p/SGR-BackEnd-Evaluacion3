"""Hitos del SGR. La agenda JSON original se conserva en sus vistas."""
from django.core.exceptions import ValidationError
from django.db import models


class Hito(models.Model):
    PERIODICIDADES = [
        ('unica', 'Única'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
    ]
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_ejecucion', 'En ejecución'),
        ('finalizado', 'Finalizado'),
        ('anulado', 'Anulado'),
    ]
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    periodicidad = models.CharField(max_length=20, choices=PERIODICIDADES)
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    delegacion = models.ForeignKey(
        'organizacion.Delegacion', on_delete=models.PROTECT, related_name='hitos',
    )
    territorio = models.ForeignKey(
        'organizacion.Territorio', on_delete=models.PROTECT, related_name='hitos',
    )
    responsables = models.ManyToManyField(
        'organizacion.PerfilUsuario', related_name='hitos_responsable',
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def clean(self):
        super().clean()
        if self.fecha_inicio and self.fecha_termino and self.fecha_termino < self.fecha_inicio:
            raise ValidationError({'fecha_termino': 'No puede ser anterior a la fecha de inicio.'})
        if self.territorio_id and self.delegacion_id:
            if self.territorio.delegacion_id != self.delegacion_id:
                raise ValidationError({'territorio': 'No pertenece a la delegación seleccionada.'})

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Hito'
        verbose_name_plural = 'Hitos'
        ordering = ['fecha_inicio', 'nombre']
