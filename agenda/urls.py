from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', login_required(permission_required('agenda.view_hito', raise_exception=True)(views.lista_compromisos)), name='lista_compromisos'),
    path('<int:compromiso_id>/', login_required(permission_required('agenda.view_hito', raise_exception=True)(views.detalle_compromiso)), name='detalle_compromiso'),
    path('resumen/', login_required(permission_required('agenda.view_hito', raise_exception=True)(views.resumen_agenda)), name='resumen_agenda'),
]