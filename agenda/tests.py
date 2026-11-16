from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from organizacion.models import Delegacion, Territorio
from .models import Hito


class HitoModelTests(TestCase):
    def test_fechas_y_territorio(self):
        delegacion = Delegacion.objects.create(codigo='DEL-A', nombre='Delegación A')
        territorio = Territorio.objects.create(
            codigo='TER-A', nombre='Territorio A', delegacion=delegacion,
        )
        hito = Hito(
            codigo='HIT-01', nombre='Hito ficticio', periodicidad='mensual',
            fecha_inicio=date(2026, 2, 10), fecha_termino=date(2026, 2, 1),
            delegacion=delegacion, territorio=territorio,
        )
        with self.assertRaises(ValidationError):
            hito.full_clean()
        hito.fecha_termino = date(2026, 2, 20)
        hito.full_clean()
