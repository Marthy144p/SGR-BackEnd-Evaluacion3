"""Rutas principales de la evaluación 3; el prototipo JSON permanece protegido."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from gestion import views as gestion_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/login/', auth_views.LoginView.as_view(template_name='registration/login.html', redirect_authenticated_user=True), name='login'),
    path('cuentas/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', gestion_views.inicio, name='inicio'),
    path('gestion/', include('gestion.urls')),
    path('organizacion/', gestion_views.area, {'area': 'organizacion'}, name='area_organizacion'),
    path('actividades/', gestion_views.area, {'area': 'actividades'}, name='area_actividades'),
    path('agenda/', gestion_views.area, {'area': 'agenda'}, name='area_agenda'),
    path('resultados/', gestion_views.area, {'area': 'resultados'}, name='area_resultados'),
    path('prototipo/organizacion/', include('organizacion.urls')),
    path('prototipo/actividades/', include('actividades.urls')),
    path('prototipo/agenda/', include('agenda.urls')),
    path('prototipo/resultados/', include('resultados.urls')),
]
