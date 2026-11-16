from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('<slug:slug>/', views.lista, name='lista'),
    path('<slug:slug>/nuevo/', views.formulario, name='crear'),
    path('<slug:slug>/<int:pk>/', views.detalle, name='detalle'),
    path('<slug:slug>/<int:pk>/editar/', views.formulario, name='editar'),
    path('<slug:slug>/<int:pk>/eliminar/', views.eliminar, name='eliminar'),
]
