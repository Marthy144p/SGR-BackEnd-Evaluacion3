from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.urls import path
from . import views

app_name = 'resultados'

urlpatterns = [
    path('', login_required(permission_required('resultados.view_meta', raise_exception=True)(views.lista_metas)), name='lista_metas'),
    path('<int:meta_id>/', login_required(permission_required('resultados.view_meta', raise_exception=True)(views.detalle_meta)), name='detalle_meta'),
    path('persona/<int:persona_id>/', login_required(permission_required('resultados.view_meta', raise_exception=True)(views.resultado_persona)), name='resultado_persona'),
    path('unidad/<int:unidad_id>/', login_required(permission_required('resultados.view_meta', raise_exception=True)(views.tablero_unidad)), name='tablero_unidad'),
    path('informe/', login_required(permission_required('resultados.view_meta', raise_exception=True)(views.informe_resumen)), name='informe_resumen'),
]