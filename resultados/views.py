import json

from django.conf import settings
from django.http import Http404
from django.shortcuts import render


def cargar_datos():
    ruta_archivo = settings.BASE_DIR / 'datos' / 'resultados.json'

    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        return json.load(archivo)


def calcular_cumplimiento(meta):
    meta_periodo = meta.get('meta_periodo', 0)
    avance_aprobado = meta.get('avance_aprobado', 0)

    if meta_periodo == 0:
        return 0

    return round((avance_aprobado / meta_periodo) * 100, 1)


def obtener_semaforo(cumplimiento):
    if cumplimiento >= 90:
        return 'Verde'

    if cumplimiento >= 70:
        return 'Amarillo'

    return 'Rojo'


def preparar_meta(meta):
    cumplimiento = calcular_cumplimiento(meta)

    meta['cumplimiento'] = cumplimiento
    meta['semaforo'] = obtener_semaforo(cumplimiento)

    return meta


def lista_metas(request):
    datos = cargar_datos()

    metas = datos.get('metas', [])

    for meta in metas:
        preparar_meta(meta)

    contexto = {
        'titulo': 'Metas',
        'metas': metas,
    }

    return render(
        request,
        'resultados/lista_metas.html',
        contexto
    )


def detalle_meta(request, meta_id):
    datos = cargar_datos()

    metas = datos.get('metas', [])
    periodos = datos.get('periodos', [])

    meta = next(
        (
            meta
            for meta in metas
            if meta['id'] == meta_id
        ),
        None
    )

    if meta is None:
        raise Http404('La meta solicitada no existe.')

    preparar_meta(meta)

    periodo = next(
        (
            periodo
            for periodo in periodos
            if periodo['id'] == meta['periodo_id']
        ),
        None
    )

    contexto = {
        'titulo': 'Detalle de Meta',
        'meta': meta,
        'periodo': periodo,
    }

    return render(
        request,
        'resultados/detalle_meta.html',
        contexto
    )


def resultado_persona(request, persona_id):
    datos = cargar_datos()

    metas = datos.get('metas', [])

    metas_persona = [
        meta
        for meta in metas
        if meta['persona_id'] == persona_id
    ]

    if not metas_persona:
        raise Http404(
            'No existen resultados para el funcionario solicitado.'
        )

    total_cumplimiento = 0

    for meta in metas_persona:
        preparar_meta(meta)
        total_cumplimiento += meta['cumplimiento']

    promedio_cumplimiento = round(
        total_cumplimiento / len(metas_persona),
        1
    )

    semaforo_general = obtener_semaforo(
        promedio_cumplimiento
    )

    contexto = {
        'titulo': 'Resultado del Funcionario',
        'persona_id': persona_id,
        'metas': metas_persona,
        'promedio_cumplimiento': promedio_cumplimiento,
        'semaforo_general': semaforo_general,
    }

    return render(
        request,
        'resultados/resultado_persona.html',
        contexto
    )


def tablero_unidad(request, unidad_id):
    datos = cargar_datos()

    metas = datos.get('metas', [])

    metas_unidad = [
        meta
        for meta in metas
        if meta['unidad_id'] == unidad_id
    ]

    if not metas_unidad:
        raise Http404(
            'No existen resultados para la delegación solicitada.'
        )

    total_cumplimiento = 0

    for meta in metas_unidad:
        preparar_meta(meta)
        total_cumplimiento += meta['cumplimiento']

    promedio_cumplimiento = round(
        total_cumplimiento / len(metas_unidad),
        1
    )

    semaforo_general = obtener_semaforo(
        promedio_cumplimiento
    )

    contexto = {
        'titulo': 'Tablero de Delegación',
        'unidad_id': unidad_id,
        'metas': metas_unidad,
        'promedio_cumplimiento': promedio_cumplimiento,
        'semaforo_general': semaforo_general,
    }

    return render(
        request,
        'resultados/tablero_unidad.html',
        contexto
    )


def informe_resumen(request):
    datos = cargar_datos()

    metas = datos.get('metas', [])

    total_metas = len(metas)

    verdes = 0
    amarillas = 0
    rojas = 0

    total_cumplimiento = 0

    for meta in metas:
        preparar_meta(meta)

        total_cumplimiento += meta['cumplimiento']

        if meta['semaforo'] == 'Verde':
            verdes += 1

        elif meta['semaforo'] == 'Amarillo':
            amarillas += 1

        else:
            rojas += 1

    if total_metas > 0:
        promedio_general = round(
            total_cumplimiento / total_metas,
            1
        )
    else:
        promedio_general = 0

    semaforo_general = obtener_semaforo(
        promedio_general
    )

    contexto = {
        'titulo': 'Informe Resumen',
        'total_metas': total_metas,
        'verdes': verdes,
        'amarillas': amarillas,
        'rojas': rojas,
        'promedio_general': promedio_general,
        'semaforo_general': semaforo_general,
    }

    return render(
        request,
        'resultados/informe_resumen.html',
        contexto
    )