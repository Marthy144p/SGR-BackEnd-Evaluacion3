import json

from django.conf import settings
from django.http import Http404
from django.shortcuts import render


def cargar_datos():
    ruta_archivo = settings.BASE_DIR / 'datos' / 'actividades.json'

    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        return json.load(archivo)


def lista_actividades(request):
    datos = cargar_datos()

    actividades = datos.get('actividades', [])

    contexto = {
        'titulo': 'Actividades',
        'actividades': actividades,
    }

    return render(
        request,
        'actividades/lista_actividades.html',
        contexto
    )


def detalle_actividad(request, actividad_id):
    datos = cargar_datos()

    actividades = datos.get('actividades', [])
    evidencias = datos.get('evidencias', [])

    actividad = next(
        (
            actividad
            for actividad in actividades
            if actividad['id'] == actividad_id
        ),
        None
    )

    if actividad is None:
        raise Http404('La actividad solicitada no existe.')

    evidencias_actividad = [
        evidencia
        for evidencia in evidencias
        if evidencia['actividad_id'] == actividad_id
    ]

    contexto = {
        'titulo': 'Detalle de Actividad',
        'actividad': actividad,
        'evidencias': evidencias_actividad,
    }

    return render(
        request,
        'actividades/detalle_actividad.html',
        contexto
    )


def lista_evidencias(request):
    datos = cargar_datos()

    evidencias = datos.get('evidencias', [])
    actividades = datos.get('actividades', [])

    for evidencia in evidencias:
        actividad = next(
            (
                actividad
                for actividad in actividades
                if actividad['id'] == evidencia['actividad_id']
            ),
            None
        )

        evidencia['actividad'] = actividad

    contexto = {
        'titulo': 'Evidencias',
        'evidencias': evidencias,
    }

    return render(
        request,
        'actividades/lista_evidencias.html',
        contexto
    )


def detalle_evidencia(request, evidencia_id):
    datos = cargar_datos()

    evidencias = datos.get('evidencias', [])
    actividades = datos.get('actividades', [])

    evidencia = next(
        (
            evidencia
            for evidencia in evidencias
            if evidencia['id'] == evidencia_id
        ),
        None
    )

    if evidencia is None:
        raise Http404('La evidencia solicitada no existe.')

    actividad = next(
        (
            actividad
            for actividad in actividades
            if actividad['id'] == evidencia['actividad_id']
        ),
        None
    )

    contexto = {
        'titulo': 'Detalle de Evidencia',
        'evidencia': evidencia,
        'actividad': actividad,
    }

    return render(
        request,
        'actividades/detalle_evidencia.html',
        contexto
    )