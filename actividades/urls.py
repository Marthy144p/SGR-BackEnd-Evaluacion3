from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.urls import path
from . import views

app_name = 'actividades'

urlpatterns = [
    path('', login_required(permission_required('actividades.view_actividad', raise_exception=True)(views.lista_actividades)), name='lista_actividades'),
    path('<int:actividad_id>/', login_required(permission_required('actividades.view_actividad', raise_exception=True)(views.detalle_actividad)), name='detalle_actividad'),
    path('evidencias/', login_required(permission_required('actividades.view_actividad', raise_exception=True)(views.lista_evidencias)), name='lista_evidencias'),
    path('evidencia/<int:evidencia_id>/', login_required(permission_required('actividades.view_actividad', raise_exception=True)(views.detalle_evidencia)), name='detalle_evidencia'),
]