import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required


from .models import Insumo, StockFarmCentral, StockMaletin, StockMaletinMov



@ensure_csrf_cookie
def home2(request):
    return render(request, 'stock/home.html')

@ensure_csrf_cookie
@login_required
def home(request):
    return render(request, 'auth/home.html')

# -------- Ventana 1: Farm Central --------

# --- etiquetas para vistas de 1 columna (Farm Central) ---
FARM_ONECOL_LABELS = {
    'cantidad_existente': 'Cantidad existente',
    'punto_pedido': 'Punto Pedido',
    'stock_ideal': 'Stock Ideal',
    'stock_critico': 'Stock Crítico',
}

@ensure_csrf_cookie
def farm_central_view(request):
    rows = []
    stocks = StockFarmCentral.objects.all()
    codigos = [s.fk_codigo_insumo for s in stocks]
    insumos = {i.codigo: i for i in Insumo.objects.filter(codigo__in=codigos)}
    for s in stocks:
        ins = insumos.get(s.fk_codigo_insumo)
        if ins:
            rows.append({
                'codigo': ins.codigo,
                'descripcion': ins.descripcion,
                'cantidad_existente': s.cantidad_existente,
                'punto_pedido': ins.punto_pedido or 0,
                'stock_ideal': ins.stock_ideal or 0,
                'stock_critico': ins.stock_critico or 0,
            })
    rows.sort(key=lambda x: x['descripcion'])
    return render(request, 'stock/farm_central.html', {'rows': rows})


@csrf_protect
@transaction.atomic
def farm_central_save_all(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    items = payload.get('items', [])
    if not isinstance(items, list):
        return JsonResponse({'ok': False, 'error': 'items debe ser lista'}, status=400)

    codigos = [it.get('codigo') for it in items if it.get('codigo')]
    if not codigos:
        return JsonResponse({'ok': False, 'error': 'Sin códigos'}, status=400)

    ins_map = {i.codigo: i for i in Insumo.objects.filter(codigo__in=codigos)}
    sfc_map = {s.fk_codigo_insumo: s for s in StockFarmCentral.objects.filter(fk_codigo_insumo__in=codigos)}

    updated = 0
    for it in items:
        codigo = it['codigo']
        ins = ins_map.get(codigo)
        sfc = sfc_map.get(codigo)
        if not ins or not sfc:
            continue

        def _to_int(val, default):
            try:
                return int(val)
            except (TypeError, ValueError):
                return default

        ce = _to_int(it.get('cantidad_existente'), sfc.cantidad_existente)
        pp = _to_int(it.get('punto_pedido'),    ins.punto_pedido or 0)
        si = _to_int(it.get('stock_ideal'),     ins.stock_ideal  or 0)
        sc = _to_int(it.get('stock_critico'),   ins.stock_critico or 0)

        changed = False
        if sfc.cantidad_existente != ce:
            sfc.cantidad_existente = ce
            sfc.save(update_fields=['cantidad_existente'])
            changed = True

        if (ins.punto_pedido != pp) or (ins.stock_ideal != si) or (ins.stock_critico != sc):
            ins.punto_pedido = pp
            ins.stock_ideal = si
            ins.stock_critico = sc
            ins.save(update_fields=['punto_pedido', 'stock_ideal', 'stock_critico'])
            changed = True

        if changed:
            updated += 1

    return JsonResponse({'ok': True, 'updated': updated})

@transaction.atomic
def farm_central_update_row(request, codigo):
    """
    Actualiza una fila de Farm Central:
      - StockFarmCentral.cantidad_existente
      - Insumo.punto_pedido / stock_ideal / stock_critico
    Devuelve el HTML de la fila renderizada (full o onecol), para HTMX.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # Lock de la fila de stock (y del insumo) para evitar condiciones de carrera
    try:
        stock = (StockFarmCentral.objects
                 .select_for_update()
                 .get(fk_codigo_insumo=codigo))
    except StockFarmCentral.DoesNotExist:
        return HttpResponseBadRequest('Registro de stock no encontrado')

    try:
        insumo = (Insumo.objects
                  .select_for_update()
                  .get(codigo=codigo))
    except Insumo.DoesNotExist:
        insumo = None

    def to_int(val, default):
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    # Valores actuales (con fallback por si no hay Insumo)
    cur_pp = getattr(insumo, 'punto_pedido', 0) if insumo else 0
    cur_si = getattr(insumo, 'stock_ideal', 0) if insumo else 0
    cur_sc = getattr(insumo, 'stock_critico', 0) if insumo else 0

    # Nuevos valores (si no vienen en el POST, se usan los actuales)
    new_ce = to_int(request.POST.get('cantidad_existente'), stock.cantidad_existente)
    new_pp = to_int(request.POST.get('punto_pedido'),      cur_pp)
    new_si = to_int(request.POST.get('stock_ideal'),       cur_si)
    new_sc = to_int(request.POST.get('stock_critico'),     cur_sc)

    # Actualizar STOCK_FARM_CENTRAL
    stock_changed = (new_ce != stock.cantidad_existente)
    if stock_changed:
        stock.cantidad_existente = new_ce
        stock.save(update_fields=['cantidad_existente'])

    # Actualizar INSUMO
    if insumo:
        insumo_update_fields = []
        if new_pp != cur_pp:
            insumo.punto_pedido = new_pp
            insumo_update_fields.append('punto_pedido')
        if new_si != cur_si:
            insumo.stock_ideal = new_si
            insumo_update_fields.append('stock_ideal')
        if new_sc != cur_sc:
            insumo.stock_critico = new_sc
            insumo_update_fields.append('stock_critico')

        if insumo_update_fields:
            insumo.save(update_fields=insumo_update_fields)

    # Data para re-renderizar la fila
    row = {
        'codigo': codigo,
        'descripcion': getattr(insumo, 'descripcion', codigo),
        'cantidad_existente': stock.cantidad_existente,
        'punto_pedido': getattr(insumo, 'punto_pedido', new_pp),
        'stock_ideal': getattr(insumo, 'stock_ideal', new_si),
        'stock_critico': getattr(insumo, 'stock_critico', new_sc),
    }

    onecol = request.GET.get('onecol')  # 'cantidad_existente'|'punto_pedido'|'stock_ideal'|'stock_critico'|None
    if onecol in ('cantidad_existente', 'punto_pedido', 'stock_ideal', 'stock_critico'):
        html = render_to_string('stock/_farm_central_onecol_row.html',
                                {'row': row, 'col': onecol},
                                request=request)
    else:
        html = render_to_string('stock/_farm_central_row.html',
                                {'row': row},
                                request=request)

    return HttpResponse(html)

@ensure_csrf_cookie
def farm_central_onecol_view(request, col):
    """
    Vista 'una sola columna' para Farm Central.
    col ∈ {'cantidad_existente','punto_pedido','stock_ideal','stock_critico'}
    """
    # validar columna
    if col not in FARM_ONECOL_LABELS:
        return redirect('farm_central')

    # join lógico StockFarmCentral + Insumo
    stocks = StockFarmCentral.objects.all()
    codigos = [s.fk_codigo_insumo for s in stocks]
    insumos = {i.codigo: i for i in Insumo.objects.filter(codigo__in=codigos)}

    rows = []
    for s in stocks:
        ins = insumos.get(s.fk_codigo_insumo)
        if not ins:
            continue
        rows.append({
            'codigo': ins.codigo,
            'descripcion': ins.descripcion,
            'cantidad_existente': s.cantidad_existente,
            'punto_pedido': ins.punto_pedido or 0,
            'stock_ideal': ins.stock_ideal or 0,
            'stock_critico': ins.stock_critico or 0,
        })

    # orden alfabético por descripción (opcional)
    rows.sort(key=lambda x: x['descripcion'])

    return render(request, 'stock/farm_central_onecol.html', {
        'rows': rows,
        'col': col,
        'col_label': FARM_ONECOL_LABELS[col],
    })

# -------- Ventana 2: Maletín --------

DEFAULT_FUNCION = getattr(settings, 'DEFAULT_FUNCION_MALETIN', '10') 

MALETIN_ONECOL_LABELS = {
    'cantidad_existente': 'Cantidad existente',
    'cantidad_ideal': 'Cantidad ideal',
}


@ensure_csrf_cookie
def maletin_view(request):
    # si no viene ?funcion=..., usamos la por defecto
    funcion = request.GET.get('funcion') or DEFAULT_FUNCION

    # si la función no existe en DB, caemos a la primera disponible (por seguridad)
    funciones_qs = (StockMaletin.objects
                    .values_list('funcion', flat=True)
                    .distinct().order_by('funcion'))
    funciones = list(funciones_qs)

    if funcion not in funciones:
        funcion = funciones[0] if funciones else DEFAULT_FUNCION

    # SIEMPRE filtramos por una función (nada de “todas”)
    qs = StockMaletin.objects.filter(funcion=funcion)

    # join lógico con Insumos
    codigos = [r.fk_codigo_insumo for r in qs]
    insumos = {i.codigo: i for i in Insumo.objects.filter(codigo__in=codigos)}

    rows = []
    for r in qs:
        ins = insumos.get(r.fk_codigo_insumo)
        if ins:
            rows.append({
                'codigo': ins.codigo,
                'descripcion': ins.descripcion,
                'funcion': r.funcion,
                'cantidad_existente': r.cantidad_existente,
                'cantidad_ideal': r.cantidad_ideal,
            })
    rows.sort(key=lambda x: x['descripcion'])

    return render(request, 'stock/maletin.html', {
        'rows': rows,
        'funcion': funcion,
        'funciones': funciones,  # seguimos mostrando el dropdown, pero sin “todas”
    })


@csrf_protect
@transaction.atomic
def maletin_save_all(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    items = payload.get('items', [])
    if not isinstance(items, list) or not items:
        return JsonResponse({'ok': False, 'error': 'items debe ser lista no vacía'}, status=400)

    # Claves compuestas (codigo+funcion)
    keys = [(it.get('codigo'), it.get('funcion')) for it in items if it.get('codigo') and it.get('funcion')]
    if not keys:
        return JsonResponse({'ok': False, 'error': 'Faltan códigos/funciones'}, status=400)

    codigos = list({k[0] for k in keys})
    # (insumos no son estrictamente necesarios, pero útil si luego validás)
    _ = {i.codigo: i for i in Insumo.objects.filter(codigo__in=codigos)}

    # Mapa (codigo, funcion) -> registro
    recs = {(r.fk_codigo_insumo, r.funcion): r
            for r in StockMaletin.objects.filter(fk_codigo_insumo__in=codigos)}

    changed_qty = 0
    changed_ideal = 0

    def _to_int(val, default):
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    username = getattr(request.user, 'username', None) or 'web'

    for it in items:
        codigo = it.get('codigo')
        funcion = it.get('funcion')
        rec = recs.get((codigo, funcion))
        if not rec:
            continue

        old_qty = rec.cantidad_existente
        new_qty = _to_int(it.get('cantidad_existente'), old_qty)
        new_ideal = _to_int(it.get('cantidad_ideal'), rec.cantidad_ideal)

        # Movimiento si cambió cantidad_existente
        if new_qty != old_qty:
            StockMaletinMov.objects.create(
                fk_codigo_insumo=codigo,
                fecha_mov=timezone.now(),
                funcion=funcion,
                fk_tipo_movimiento=1,  # 1 = ajuste manual web
                usuario_mod=username,
                descripcion='Ajuste masivo web',
                cantidad_operacion=new_qty - old_qty,
                cantidad_inicial=old_qty,
            )
            rec.cantidad_existente = new_qty
            changed_qty += 1

        if new_ideal != rec.cantidad_ideal:
            rec.cantidad_ideal = new_ideal
            changed_ideal += 1

        rec.save(update_fields=['cantidad_existente', 'cantidad_ideal'])

    return JsonResponse({'ok': True, 'changed_qty': changed_qty, 'changed_ideal': changed_ideal})

@transaction.atomic
def maletin_update_row(request, codigo, funcion):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # Bloqueamos la fila para evitar condiciones de carrera
    try:
        rec = (StockMaletin.objects
               .select_for_update()
               .get(fk_codigo_insumo=codigo, funcion=funcion))
    except StockMaletin.DoesNotExist:
        return HttpResponseBadRequest('Registro de maletín no encontrado')

    def to_int(val, default):
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    old_qty = rec.cantidad_existente
    new_ce = to_int(request.POST.get('cantidad_existente'), rec.cantidad_existente)
    new_ci = to_int(request.POST.get('cantidad_ideal'),     rec.cantidad_ideal)

    # Registrar movimiento si cambió la cantidad existente
    if new_ce != old_qty:
        username = getattr(request.user, 'username', None) or 'web'
        StockMaletinMov.objects.create(
            fk_codigo_insumo=codigo,
            fecha_mov=timezone.now(),
            funcion=funcion,
            fk_tipo_movimiento=1,           # 1 = ajuste manual web (ajustá si tenés catálogo)
            usuario_mod=username,
            descripcion='Ajuste manual web',
            cantidad_operacion=new_ce - old_qty,
            cantidad_inicial=old_qty,
        )
        rec.cantidad_existente = new_ce

    # Actualizar cantidad ideal si cambió
    if new_ci != rec.cantidad_ideal:
        rec.cantidad_ideal = new_ci

    rec.save(update_fields=['cantidad_existente', 'cantidad_ideal'])

    # Descripción del insumo (si no hay FK, la resolvemos por código)
    try:
        ins_desc = Insumo.objects.get(codigo=codigo).descripcion
    except Insumo.DoesNotExist:
        ins_desc = codigo

    row = {
        'codigo': codigo,
        'descripcion': ins_desc,
        'funcion': rec.funcion,
        'cantidad_existente': rec.cantidad_existente,
        'cantidad_ideal': rec.cantidad_ideal,
    }

    # Si venimos de una vista "onecol", devolvemos el parcial de una sola columna
    onecol = request.GET.get('onecol')  # 'cantidad_existente' | 'cantidad_ideal' | None
    if onecol in ('cantidad_existente', 'cantidad_ideal'):
        html = render_to_string('stock/_maletin_onecol_row.html',
                                {'row': row, 'col': onecol},
                                request=request)
    else:
        html = render_to_string('stock/_maletin_row.html',
                                {'row': row},
                                request=request)

    return HttpResponse(html)

@ensure_csrf_cookie
def maletin_onecol_view(request, col):
    # validar columna
    if col not in MALETIN_ONECOL_LABELS:
        return redirect('maletin')  # fallback

    # resolver función (si no viene, usar por defecto)
    funcion = request.GET.get('funcion') or DEFAULT_FUNCION

    # si la función no existe, caer a la primera disponible
    funciones = list(StockMaletin.objects.values_list('funcion', flat=True).distinct().order_by('funcion'))
    if not funciones:
        return render(request, 'stock/maletin_onecol.html', {'rows': [], 'funcion': funcion, 'funciones': [], 'col': col, 'col_label': MALETIN_ONECOL_LABELS[col]})
    if funcion not in funciones:
        funcion = funciones[0]

    # filas de esa función
    qs = StockMaletin.objects.filter(funcion=funcion)
    codigos = [r.fk_codigo_insumo for r in qs]
    insumos = {i.codigo: i for i in Insumo.objects.filter(codigo__in=codigos)}

    rows = []
    for r in qs:
        ins = insumos.get(r.fk_codigo_insumo)
        if not ins:
            continue
        rows.append({
            'codigo': ins.codigo,
            'descripcion': ins.descripcion,
            'funcion': r.funcion,
            'cantidad_existente': r.cantidad_existente,
            'cantidad_ideal': r.cantidad_ideal,
        })
    rows.sort(key=lambda x: x['descripcion'])

    return render(request, 'stock/maletin_onecol.html', {
        'rows': rows,
        'funcion': funcion,
        'funciones': funciones,
        'col': col,
        'col_label': MALETIN_ONECOL_LABELS[col],
    })

