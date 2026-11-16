"""CRUD propio, autenticado y autorizado por permisos reales del ORM Django."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import FuncionarioForm, formulario_para
from .registro import AREAS, RECURSOS, obtener_recurso


def _autorizacion(request, recurso, accion):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    if not request.user.has_perm(recurso.permiso(accion)):
        raise PermissionDenied('Tu cuenta no tiene permisos para esta operación.')
    return None


def _contexto(request, recurso, **otros):
    return {
        'recurso': recurso,
        'puede_crear': request.user.has_perm(recurso.permiso('add')),
        'puede_editar': request.user.has_perm(recurso.permiso('change')),
        'puede_eliminar': request.user.has_perm(recurso.permiso('delete')),
        **otros,
    }


def _detalle_campos(objeto):
    """Solo muestra información de negocio; nunca hashes de contraseñas."""
    campos = []
    for field in objeto._meta.fields:
        if field.name in ('password',):
            continue
        valor = getattr(objeto, field.name)
        if field.is_relation and field.many_to_one:
            valor = getattr(objeto, field.name)
        elif field.choices:
            valor = getattr(objeto, f'get_{field.name}_display')()
        campos.append((field.verbose_name.capitalize(), valor))
    for field in objeto._meta.many_to_many:
        valores = list(getattr(objeto, field.name).all())
        campos.append((field.verbose_name.capitalize(), ', '.join(map(str, valores)) or 'Sin asignar'))
    if objeto._meta.model_name == 'perfilusuario':
        user = objeto.usuario
        campos.extend([
            ('Nombres', user.first_name), ('Apellidos', user.last_name),
            ('Correo', user.email), ('Último acceso', user.last_login),
            ('Activo', 'Sí' if user.is_active else 'No'),
        ])
    return campos


@login_required
def inicio(request):
    areas = []
    for codigo, (titulo, descripcion) in AREAS.items():
        recursos = [
            {'recurso': r, 'cantidad': r.clase.objects.count()}
            for r in RECURSOS if r.area == codigo and request.user.has_perm(r.permiso('view'))
        ]
        if recursos:
            areas.append({'codigo': codigo, 'titulo': titulo, 'descripcion': descripcion, 'recursos': recursos})
    return render(request, 'gestion/inicio.html', {'areas': areas})


@login_required
def area(request, area):
    if area not in AREAS:
        raise Http404('Área no encontrada.')
    recursos = [r for r in RECURSOS if r.area == area and request.user.has_perm(r.permiso('view'))]
    return render(request, 'gestion/area.html', {
        'area': area, 'titulo': AREAS[area][0], 'descripcion': AREAS[area][1], 'recursos': recursos,
    })


def lista(request, slug):
    recurso = obtener_recurso(slug)
    error = _autorizacion(request, recurso, 'view')
    if error:
        return error
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    objetos = recurso.clase.objects.all()[:300]
    return render(request, 'gestion/lista.html', _contexto(request, recurso, objetos=objetos))


def detalle(request, slug, pk):
    recurso = obtener_recurso(slug)
    error = _autorizacion(request, recurso, 'view')
    if error:
        return error
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    objeto = get_object_or_404(recurso.clase, pk=pk)
    return render(request, 'gestion/detalle.html', _contexto(
        request, recurso, objeto=objeto, campos=_detalle_campos(objeto),
    ))


def _perfil_administrativo(objeto):
    return objeto._meta.model_name == 'perfilusuario' and (
        objeto.usuario.is_superuser or objeto.usuario.is_staff
    )


def formulario(request, slug, pk=None):
    recurso = obtener_recurso(slug)
    accion = 'change' if pk is not None else 'add'
    error = _autorizacion(request, recurso, accion)
    if error:
        return error
    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(['GET', 'POST'])
    objeto = get_object_or_404(recurso.clase, pk=pk) if pk is not None else None
    if objeto and _perfil_administrativo(objeto):
        raise PermissionDenied('Las cuentas administrativas solo pueden modificarse desde Django Admin.')
    Form = formulario_para(recurso.clase)
    kwargs = {'instance': objeto} if objeto else {}
    if Form is FuncionarioForm:
        kwargs['actor'] = request.user
    if request.method == 'POST':
        form = Form(request.POST, **kwargs)
        if form.is_valid():
            with transaction.atomic():
                nuevo = form.save()
            messages.success(request, 'Registro guardado correctamente.')
            return redirect('gestion:detalle', slug=slug, pk=nuevo.pk)
        messages.error(request, 'Revisa los campos señalados; no se guardaron cambios.')
    else:
        form = Form(**kwargs)
    return render(request, 'gestion/formulario.html', _contexto(
        request, recurso, formulario=form, objeto=objeto,
        titulo='Editar' if objeto else 'Crear',
    ))


def _desactivar(objeto):
    """Desactivación histórica en vez de DELETE físico, justificable en el README."""
    if objeto._meta.model_name == 'perfilusuario':
        usuario = objeto.usuario
        if usuario.is_superuser or usuario.is_staff:
            raise PermissionDenied('No se permite desactivar una cuenta administrativa desde el CRUD.')
        usuario.is_active = False
        usuario.save(update_fields=['is_active'])
        return
    if hasattr(objeto, 'activo'):
        objeto.activo = False
        objeto.save(update_fields=['activo'])
        return
    if hasattr(objeto, 'estado'):
        opciones = {c[0] for c in objeto._meta.get_field('estado').choices}
        estado = 'anulado' if 'anulado' in opciones else 'anulada'
        if estado not in opciones:
            raise PermissionDenied('No existe un estado de anulación configurado.')
        objeto.estado = estado
        objeto.save(update_fields=['estado'])
        return
    raise PermissionDenied('Este registro no tiene estrategia de desactivación.')


def eliminar(request, slug, pk):
    recurso = obtener_recurso(slug)
    error = _autorizacion(request, recurso, 'delete')
    if error:
        return error
    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(['GET', 'POST'])
    objeto = get_object_or_404(recurso.clase, pk=pk)
    if _perfil_administrativo(objeto):
        raise PermissionDenied('No se permite desactivar administradores desde este módulo.')
    if objeto._meta.model_name == 'perfilusuario' and objeto.usuario_id == request.user.pk:
        raise PermissionDenied('No puedes desactivar tu propia cuenta.')
    if request.method == 'POST':
        with transaction.atomic():
            _desactivar(objeto)
        messages.success(request, 'Registro desactivado/anulado; su historial se conserva.')
        return redirect('gestion:lista', slug=slug)
    return render(request, 'gestion/confirmar.html', _contexto(request, recurso, objeto=objeto))
