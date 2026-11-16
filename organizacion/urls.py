from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.urls import path
from . import views

app_name = 'organizacion'

urlpatterns = [
    path('', login_required(permission_required('organizacion.view_delegacion', raise_exception=True)(views.lista_unidades)), name='lista_unidades'),
    path('unidad/<int:unidad_id>/', login_required(permission_required('organizacion.view_delegacion', raise_exception=True)(views.detalle_unidad)), name='detalle_unidad'),
    path('personas/', login_required(permission_required('organizacion.view_delegacion', raise_exception=True)(views.lista_personas)), name='lista_personas'),
    path('persona/<int:persona_id>/', login_required(permission_required('organizacion.view_delegacion', raise_exception=True)(views.detalle_persona)), name='detalle_persona'),
]