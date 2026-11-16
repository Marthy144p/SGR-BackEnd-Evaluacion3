import json

from django.conf import settings
from django.http import Http404
from django.shortcuts import render


def cargar_datos():
    ruta_archivo = settings.BASE_DIR / 'datos' / 'organizacion.json'

    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        return json.load(archivo)


def lista_unidades(request):
    datos = cargar_datos()

    unidades = datos.get('unidades', [])
    personas = datos.get('personas', [])

    for unidad in unidades:
        responsable = next(
            (
                persona
                for persona in personas
                if persona['id'] == unidad['responsable_id']
            ),
            None
        )

        unidad['responsable'] = responsable

    contexto = {
        'titulo': 'Delegaciones Municipales',
        'unidades': unidades,
    }

    return render(
        request,
        'organizacion/lista_unidades.html',
        contexto
    )


def detalle_unidad(request, unidad_id):
    datos = cargar_datos()

    unidades = datos.get('unidades', [])
    personas = datos.get('personas', [])

    unidad = next(
        (
            unidad
            for unidad in unidades
            if unidad['id'] == unidad_id
        ),
        None
    )

    if unidad is None:
        raise Http404('La delegación solicitada no existe.')

    responsable = next(
        (
            persona
            for persona in personas
            if persona['id'] == unidad['responsable_id']
        ),
        None
    )

    funcionarios = [
        persona
        for persona in personas
        if persona['unidad_id'] == unidad_id
    ]

    contexto = {
        'titulo': 'Detalle de Delegación',
        'unidad': unidad,
        'responsable': responsable,
        'funcionarios': funcionarios,
    }

    return render(
        request,
        'organizacion/detalle_unidad.html',
        contexto
    )


def lista_personas(request):
    datos = cargar_datos()

    personas = datos.get('personas', [])
    unidades = datos.get('unidades', [])

    for persona in personas:
        unidad = next(
            (
                unidad
                for unidad in unidades
                if unidad['id'] == persona['unidad_id']
            ),
            None
        )

        persona['unidad'] = unidad

    contexto = {
        'titulo': 'Funcionarios',
        'personas': personas,
    }

    return render(
        request,
        'organizacion/lista_personas.html',
        contexto
    )


def detalle_persona(request, persona_id):
    datos = cargar_datos()

    personas = datos.get('personas', [])
    unidades = datos.get('unidades', [])

    persona = next(
        (
            persona
            for persona in personas
            if persona['id'] == persona_id
        ),
        None
    )

    if persona is None:
        raise Http404('El funcionario solicitado no existe.')

    unidad = next(
        (
            unidad
            for unidad in unidades
            if unidad['id'] == persona['unidad_id']
        ),
        None
    )

    contexto = {
        'titulo': 'Detalle de Funcionario',
        'persona': persona,
        'unidad': unidad,
    }

    return render(
        request,
        'organizacion/detalle_persona.html',
        contexto
    )