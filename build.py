# Arma index.html a partir de src.html:
#  1. inyecta el logo vectorizado (work/logo_final.svg) como <symbol id="ta-logo">
#  2. genera el cerro tejido (silueta + 7 estratos con motivos de aguayo)
#  3. inyecta la copia versionada del widget de Operon Reservas (assets/booking-widget-demo.html) SIN tocar
#     su lógica ni su CSS: solo CONFIG y el H3, que es lo que permite TEMATIZACION.md.
# Después copia index.html + img/ a dist/ para el deploy.
import os, pathlib, re, math, random, json, shutil

here = pathlib.Path(__file__).parent

# ---------- 1. Logo ----------
logo = (here / 'work/logo_final.svg').read_text(encoding='utf-8')
inner = logo[logo.index('>') + 1: logo.rindex('</svg>')].strip()
symbol = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">'
          '<symbol id="ta-logo" viewBox="0 0 3240 3240">' + inner + '</symbol></svg>')

# ---------- 2. Cerro tejido ----------
W, H = 1440, 320
random.seed(11)

def base(x):
    y = 302
    y -= 56 * math.exp(-((x - 140) / 150) ** 2)
    y -= 34 * math.exp(-((x - 430) / 120) ** 2)
    y -= 34 * math.exp(-((x - 690) / 90) ** 2)
    y -= 248 * math.exp(-((x - 840) / 215) ** 2)
    y -= 30 * math.exp(-((x - 1000) / 80) ** 2)
    y -= 126 * math.exp(-((x - 1300) / 140) ** 2)
    return y

ridge = [(0.0, base(0))]
x, up = 0.0, True
while x < W:
    x = min(W, x + random.uniform(9, 19))
    b = base(x)
    hf = max(0.0, (302 - b) / 250)
    amp = (1.5 + 15 * hf ** 1.25) * random.uniform(0.55, 1.2)
    ridge.append((x, b - amp * 0.5 if up else b + amp * 0.5))
    up = not up

def ridge_y(px):
    for (x0, y0), (x1, y1) in zip(ridge, ridge[1:]):
        if x0 <= px <= x1:
            return y0 + (y1 - y0) * ((px - x0) / (x1 - x0 or 1))
    return ridge[-1][1]

silhouette = 'M0 %d ' % (H + 2) + ' '.join('L%.1f %.1f' % p for p in ridge) + ' L%d %d Z' % (W, H + 2)

# límites de estratos (y en el centro), con inclinación y ondulación: capas finas y gruesas
CUTS = [-60, 96, 128, 152, 190, 214, 250, H + 40]
def cut_y(k, x):
    c = CUTS[k]
    if k in (0, len(CUTS) - 1):
        return c
    ph = k * 1.7
    return c - 0.062 * (x - 720) + 7 * math.sin(x / 96 + ph) + 3.2 * math.sin(x / 33 + ph * 2)

xs = list(range(0, W + 1, 16))
bands, centers = [], []
for k in range(7):
    top = [(x, cut_y(k, x)) for x in xs]
    bot = [(x, cut_y(k + 1, x)) for x in xs]
    d = 'M' + ' L'.join('%.1f %.1f' % p for p in top) + ' L' + ' L'.join('%.1f %.1f' % p for p in reversed(bot)) + ' Z'
    bands.append(d)
    cs = []
    for x in range(0, W + 1, 40):
        yt, yb = cut_y(k, x), cut_y(k + 1, x)
        yt = max(yt, ridge_y(x) + 4)
        cs.append([x, round((yt + min(yb, H)) / 2, 1)])
    centers.append(cs)
seams = []
for k in range(1, 7):
    seams.append('M' + ' L'.join('%.1f %.1f' % (x, cut_y(k, x)) for x in xs))

# colores de arriba (cresta) hacia abajo: tonos del logo; la última franja se funde con la sección pizarra
BAND = ['#C99A98', '#A8818D', '#E9CFC7', '#727682', '#8A5B6C', '#F3E4DF', '#353A47']
PATTERNS = [
    # rombos
    '<pattern id="pt0" width="18" height="18" patternUnits="userSpaceOnUse"><rect width="18" height="18" fill="{c}"/><path d="M9 3.5 14.5 9 9 14.5 3.5 9Z" fill="#FEFDEB" opacity=".32"/></pattern>',
    # zigzag
    '<pattern id="pt1" width="16" height="12" patternUnits="userSpaceOnUse"><rect width="16" height="12" fill="{c}"/><path d="M0 9 4 3 8 9 12 3 16 9" fill="none" stroke="#FEFDEB" stroke-width="1.5" opacity=".34"/></pattern>',
    # puntos
    '<pattern id="pt2" width="12" height="12" patternUnits="userSpaceOnUse"><rect width="12" height="12" fill="{c}"/><circle cx="6" cy="6" r="1.7" fill="#8A5B6C" opacity=".35"/></pattern>',
    # dientes
    '<pattern id="pt3" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="14" height="14" fill="{c}"/><path d="M0 12 7 4 14 12Z" fill="#E9CFC7" opacity=".26"/></pattern>',
    # rayas finas
    '<pattern id="pt4" width="8" height="7" patternUnits="userSpaceOnUse"><rect width="8" height="7" fill="{c}"/><rect y="3" width="8" height="1.3" fill="#E9CFC7" opacity=".3"/></pattern>',
    # rombos calados
    '<pattern id="pt5" width="16" height="16" patternUnits="userSpaceOnUse"><rect width="16" height="16" fill="{c}"/><path d="M8 3 13 8 8 13 3 8Z" fill="none" stroke="#8A5B6C" stroke-width="1.2" opacity=".32"/></pattern>',
    # base lisa
    '<pattern id="pt6" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="{c}"/></pattern>',
]
defs = ['<clipPath id="cerro-clip"><path d="%s"/></clipPath>' % silhouette]
defs += [p.replace('{c}', c) for p, c in zip(PATTERNS, BAND)]
defs += ['<clipPath id="bc%d"><rect class="bc" x="0" y="-80" width="%d" height="%d"/></clipPath>' % (k, W, H + 160) for k in range(7)]
body = []
for k in range(6, -1, -1):  # de abajo hacia arriba, como en el telar
    seam = ('<path class="seam" d="%s"/>' % seams[k - 1]) if k >= 1 else ''
    body.append('<g clip-path="url(#bc%d)"><path d="%s" fill="url(#pt%d)"/>%s</g>' % (k, bands[k], k, seam))
shuttle = ('<g class="shuttle" opacity="0"><path d="M-17 0Q0-7.5 17 0Q0 7.5-17 0Z" fill="#FEFDEB" stroke="#353A47" stroke-width="1.4"/>'
           '<circle r="2.2" fill="#353A47"/></g>')
cerro = ('<svg class="cerro" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false" data-centers=\'%s\'>'
         '<defs>%s</defs><g clip-path="url(#cerro-clip)">%s%s</g>'
         '<path class="ridge" d="%s" fill="none"/></svg>') % (
    W, H, json.dumps(centers, separators=(',', ':')), ''.join(defs), ''.join(body), shuttle,
    'M' + ' L'.join('%.1f %.1f' % p for p in ridge))

# ---------- 2b. Mapa ilustrado (calles reales de OpenStreetMap, dibujadas con la paleta) ----------
# Sin tiles ni API keys, y sin los nombres de otros alojamientos que traen los mapas genéricos.
osm = json.loads((here / 'work/osm.json').read_text(encoding='utf-8'))['elements']
MW, MH, MPP = 1200, 620, 0.78                  # metros por px
LAT0, LON0 = -23.74700, -65.49905              # centro: deja las posadas a la derecha (la tarjeta va a la izquierda)
KX = 111320 * math.cos(math.radians(LAT0)) / MPP
KY = 110540 / MPP
def proj(lat, lon):
    return (MW / 2 + (lon - LON0) * KX, MH / 2 - (lat - LAT0) * KY)
def path_of(geom, close=False):
    pts = [proj(g['lat'], g['lon']) for g in geom]
    return 'M' + ' L'.join('%.1f %.1f' % p for p in pts) + (' Z' if close else '')
ROAD_W = {'trunk': 15, 'primary': 14, 'secondary': 12, 'tertiary': 11, 'unclassified': 9, 'residential': 9,
          'pedestrian': 8, 'service': 5, 'track': 4}
parks, water, casings, roads, paths, labels = [], [], [], [], [], []
for e in osm:
    t, g = e['tags'], e.get('geometry') or []
    if len(g) < 2:
        continue
    if t.get('leisure') in ('park', 'garden') or t.get('place') == 'square':
        parks.append('<path d="%s" fill="url(#m-plaza)" stroke="#C99A98" stroke-width="1.5"/>' % path_of(g, True))
    elif t.get('leisure') == 'pitch':
        parks.append('<path d="%s" fill="#EAD3CC" stroke="#DCC0B8"/>' % path_of(g, True))
    elif t.get('waterway') == 'river':
        water.append('<path d="%s" fill="none" stroke="#C3CAD4" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" opacity=".7"/>' % path_of(g))
    elif t.get('waterway'):
        water.append('<path d="%s" fill="none" stroke="#C3CAD4" stroke-width="4" stroke-linecap="round" opacity=".8"/>' % path_of(g))
    elif t.get('highway') in ROAD_W:
        w_ = ROAD_W[t['highway']]
        d_ = path_of(g)
        casings.append('<path d="%s" stroke-width="%d"/>' % (d_, w_ + 3))
        roads.append('<path d="%s" stroke-width="%d"/>' % (d_, w_))
        name = t.get('name')
        if name and t['highway'] in ('residential', 'tertiary', 'trunk', 'unclassified', 'pedestrian') and name != 'Avenida San Martín':
            pts = [proj(p['lat'], p['lon']) for p in g]
            def safe(s):
                (x0, y0), (x1, y1) = s
                mx, my = (x0 + x1) / 2, (y0 + y1) / 2
                in_card = mx < 440 and my > 250          # zona de la tarjeta de visita (escritorio)
                return 60 < mx < MW - 60 and 105 < my < MH - 50 and not in_card
            segs = [s for s in zip(pts, pts[1:]) if safe(s)]
            if segs:
                best = max(segs, key=lambda s: math.dist(*s))
                if math.dist(*best) > 60:
                    (x0, y0), (x1, y1) = best
                    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
                    if ang > 90: ang -= 180
                    if ang < -90: ang += 180
                    labels.append((name, (x0 + x1) / 2, (y0 + y1) / 2, ang, math.dist(*best)))
    elif t.get('highway') in ('path', 'footway', 'steps'):
        paths.append('<path d="%s"/>' % path_of(g))
seen, lab_svg = set(), []
for name, x, y, a, ln in sorted(labels, key=lambda l: -l[4]):   # por calle, el tramo visible más largo
    if name in seen or name.startswith('Camino') or name.startswith('Paseo'):
        continue
    seen.add(name)
    lab_svg.append('<text x="%.1f" y="%.1f" transform="rotate(%.1f %.1f %.1f)" dy="4" text-anchor="middle">%s</text>' % (x, y, a, x, y, name.upper()))
pins = [('Posada Gorriti', -23.7473993, -65.4980732, 'r'), ('Posada Lavalle', -23.7469406, -65.4984512, 'r')]
# la plaza va en el centroide del polígono real de OSM (el punto de Google cae ~40 m al norte)
plaza_geom = next(e['geometry'] for e in osm if e['tags'].get('name') == 'Plaza 9 de Julio' and e.get('geometry'))
pp = [proj(g['lat'], g['lon']) for g in plaza_geom]
plaza = (sum(p[0] for p in pp) / len(pp), sum(p[1] for p in pp) / len(pp))
pin_svg = []
for name, la, lo, side in pins:
    x, y = proj(la, lo)
    lw = 118
    lx = x + 30 if side == 'r' else x - 30 - lw
    pin_svg.append(
        '<g class="m-pin" transform="translate(%.1f %.1f)"><path d="M0 0 -9 -16 9 -16Z" fill="#FFFDF8"/>'
        '<circle cy="-44" r="30" fill="#FFFDF8" filter="url(#m-sh)"/>'
        '<svg x="-26" y="-70" width="52" height="52" viewBox="0 0 3240 3240"><use href="#ta-logo"/></svg></g>'
        '<g class="m-tag"><rect x="%.1f" y="%.1f" width="%d" height="30" rx="8" fill="#353A47"/>'
        '<text x="%.1f" y="%.1f" fill="#FBF5E7" text-anchor="middle">%s</text></g>'
        % (x, y, lx, y - 59, lw, lx + lw / 2, y - 39, name))
map_svg = (
    '<svg class="mapa" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice" role="img" '
    'aria-label="Mapa del centro de Purmamarca con la Plaza 9 de Julio y las dos posadas: Gorriti y Lavalle">'
    '<defs><pattern id="m-plaza" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="14" height="14" fill="#E9CFC7"/>'
    '<path d="M7 3 11 7 7 11 3 7Z" fill="#FFFDF8" opacity=".55"/></pattern>'
    '<pattern id="m-bg" width="22" height="22" patternUnits="userSpaceOnUse"><rect width="22" height="22" fill="#F1E1DA"/><circle cx="11" cy="11" r="1" fill="#DCC3BA"/></pattern>'
    '<filter id="m-sh" x="-50%%" y="-50%%" width="200%%" height="200%%"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#353A47" flood-opacity=".35"/></filter></defs>'
    '<rect width="%d" height="%d" fill="url(#m-bg)"/>'
    '%s%s'
    '<g fill="none" stroke="#E3CBC2" stroke-linecap="round" stroke-linejoin="round">%s</g>'
    '<g fill="none" stroke="#FFFDF8" stroke-linecap="round" stroke-linejoin="round">%s</g>'
    '<g fill="none" stroke="#A8818D" stroke-width="1.6" stroke-dasharray="5 5" stroke-linecap="round" opacity=".7">%s</g>'
    '<g class="m-lab">%s</g>'
    '<g class="m-plaza-lab"><circle cx="%.1f" cy="%.1f" r="7" fill="#8A5B6C" stroke="#FFFDF8" stroke-width="3"/>'
    '<text x="%.1f" y="%.1f" text-anchor="middle">Plaza 9 de Julio</text></g>'
    '<text class="m-cerro" x="44" y="118">← Cerro de los Siete Colores</text>'
    '%s'
    '<g class="m-escala" transform="translate(%d %d)"><path d="M0 0v6h%.1fV0" fill="none" stroke="#5E6270" stroke-width="1.6"/>'
    '<text x="%.1f" y="-6" text-anchor="middle">100 m</text></g>'
    '<g class="m-norte" transform="translate(%d 104)"><circle r="17" fill="#FFFDF8" opacity=".9"/><path d="M0-11 5 5 0 2-5 5Z" fill="#353A47"/>'
    '<text y="-22" text-anchor="middle">N</text></g>'
    '</svg>') % (MW, MH, MW, MH, ''.join(parks), ''.join(water), ''.join(casings), ''.join(roads), ''.join(paths),
                 ''.join(lab_svg), plaza[0], plaza[1], plaza[0], plaza[1] - 16, ''.join(pin_svg),
                 MW - 170, MH - 34, 100 / MPP, 50 / MPP, MW - 46)

# ---------- 3. Widget de reservas ----------
asset = here / 'assets/booking-widget-demo.html'
w = asset.read_text(encoding='utf-8')
w = re.sub(r'<!--.*?-->\s*', '', w, count=1, flags=re.S)  # saca el comentario de instrucciones
w = w.replace("WA_NUMBER: '549XXXXXXXXXX',", "WA_NUMBER: '5493885081631',")
w = re.sub(r"UNITS: \[.*?\]", """UNITS: [
      { name: 'Habitación doble · Posada Gorriti', capacity: 2 },
      { name: 'Habitación triple · Posada Gorriti', capacity: 3 },
      { name: 'Doble o twin · Posada Lavalle', capacity: 2 },
      { name: 'Cuádruple · Posada Lavalle', capacity: 4 },
      { name: 'Familiar · Posada Lavalle', capacity: 5 },
      { name: 'Departamento en planta baja · Posada Lavalle', capacity: 6 }
    ]""", w, flags=re.S)
w = w.replace('<h3>Reservá online</h3>', '<h3>Elegí tus fechas</h3>')
assert "5493885081631" in w and "Departamento en planta baja" in w and "Elegí tus fechas" in w
assert 'Vista previa · demo' in w and 'no son datos reales' in w and 'SHOW_EXAMPLE_PRICES: false' in w

# ---------- Ensamblado ----------
src = (here / 'src.html').read_text(encoding='utf-8')
default_site_url = 'https://tierra-adentro-purmamarca.netlify.app'
site_url = (os.environ.get('PUBLIC_SITE_URL')
            or os.environ.get('VERCEL_PROJECT_PRODUCTION_URL')
            or os.environ.get('VERCEL_URL')
            or default_site_url).strip().rstrip('/')
if not site_url.startswith(('https://', 'http://')):
    site_url = 'https://' + site_url
out = src.replace(default_site_url, site_url)
canonical_url = os.environ.get('PUBLIC_SITE_URL') or os.environ.get('VERCEL_PROJECT_PRODUCTION_URL')
if canonical_url:
    canonical_url = canonical_url.strip().rstrip('/')
    if not canonical_url.startswith(('https://', 'http://')):
        canonical_url = 'https://' + canonical_url
    out = out.replace('</head>', f'<link rel="canonical" href="{canonical_url}/">\n</head>', 1)
for key, val in (('<!--LOGO_SYMBOL-->', symbol), ('<!--CERRO-->', cerro), ('<!--MAPA-->', map_svg), ('<!--BOOKING_WIDGET-->', w)):
    assert key in out, key
    out = out.replace(key, val)
(here / 'index.html').write_text(out, encoding='utf-8')

dist = here / 'dist'
if dist.exists():
    shutil.rmtree(dist)
shutil.copytree(here / 'img', dist / 'img')
shutil.copy(here / 'index.html', dist / 'index.html')
print('index.html OK', len(out) // 1024, 'KB')
