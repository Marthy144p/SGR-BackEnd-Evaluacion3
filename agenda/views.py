import json

from django.conf import settings
from django.http import Http404
from django.shortcuts import render


def cargar_datos():
    ruta_archivo = settings.BASE_DIR / 'datos' / 'agenda.json'

    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        return json.load(archivo)


def lista_compromisos(request):
    datos = cargar_datos()

    compromisos = datos.get('compromisos', [])

    contexto = {
        'titulo': 'Agenda de Compromisos',
        'compromisos': compromisos,
    }

    return render(
        request,
        'agenda/lista_compromisos.html',
        contexto
    )


def detalle_compromiso(request, compromiso_id):
    datos = cargar_datos()

    compromisos = datos.get('compromisos', [])

    compromiso = next(
        (
            compromiso
            for compromiso in compromisos
            if compromiso['id'] == compromiso_id
        ),
        None
    )

    if compromiso is None:
        raise Http404('El compromiso solicitado no existe.')

    contexto = {
        'titulo': 'Detalle de Compromiso',
        'compromiso': compromiso,
    }

    return render(
        request,
        'agenda/detalle_compromiso.html',
        contexto
    )


def resumen_agenda(request):
    datos = cargar_datos()

    compromisos = datos.get('compromisos', [])

    total_compromisos = len(compromisos)

    ingresados = len(
        [
            compromiso
            for compromiso in compromisos
            if compromiso['estado'] == 'Ingresado'
        ]
    )

    pendientes = len(
        [
            compromiso
            for compromiso in compromisos
            if compromiso['estado'] == 'Pendiente'
        ]
    )

    en_proceso = len(
        [
            compromiso
            for compromiso in compromisos
            if compromiso['estado'] == 'En proceso'
        ]
    )

    realizados = len(
        [
            compromiso
            for compromiso in compromisos
            if compromiso['estado'] == 'Realizado'
        ]
    )

    contexto = {
        'titulo': 'Resumen de Agenda',
        'total_compromisos': total_compromisos,
        'ingresados': ingresados,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'realizados': realizados,
    }

    return render(
        request,
        'agenda/resumen_agenda.html',
        contexto
    )