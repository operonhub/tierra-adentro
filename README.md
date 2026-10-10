# Tierra Adentro · Posadas en Purmamarca

Sitio estático de Tierra Adentro, con las sedes Gorriti y Lavalle. La fuente editable es `src.html`; `build.py` genera `index.html` y el deploy en `dist/`.

## Build y preview

Requiere Python 3 (solo biblioteca estándar):

```powershell
python -X utf8 build.py
python -m http.server 8000 --directory dist
```

El repositorio incluye los insumos del mapa y del logo, además de una copia versionada del widget usado por esta página, para que el build no dependa de una ruta privada de una computadora.

## Plataformas y publicación

- El sitio se publica en Vercel (proyecto `tierra-adentro`): cada push a `main` despliega producción. Mientras no haya dominio propio, la dirección es `https://tierra-adentro-drab.vercel.app/`. `vercel.json` construye `dist/` con Python.
- El sitio lleva `noindex,nofollow`. No quitarlo ni habilitar indexación hasta confirmar el dominio oficial y la aprobación de publicación del cliente.
- El build usa `PUBLIC_SITE_URL` si está definida; en Vercel puede usar `VERCEL_PROJECT_PRODUCTION_URL` para las URLs sociales y JSON-LD. Vercel provee esa variable de sistema en sus builds ([documentación](https://vercel.com/docs/environment-variables/system-environment-variables)).
- El canonical solo se genera con `PUBLIC_SITE_URL`, que debe ser el dominio oficial verificado. Así las previews y el dominio técnico de Vercel no se convierten por accidente en la URL canónica.
- Cuando se apruebe el lanzamiento en el dominio final, configurar `PUBLIC_SITE_URL` solo para Production, retirar `noindex,nofollow`, desplegar y verificar el canonical. Después crear `robots.txt` y `sitemap.xml`, conectar Search Console y enviar el sitemap.
- Las direcciones visibles del sitio y las fichas separadas están respaldadas por el listado oficial de alojamientos de Purmamarca. Confirmar con el cliente horarios, servicios, fotos y textos antes del lanzamiento definitivo.

El widget de reservas es el real de Operon Reservas, conectado al complejo `tierraadentro`: las unidades, tarifas y disponibilidad salen del panel, y las reservas caen ahí. `build.py` solo completa `ORG_SLUG` y `WA_NUMBER`.

## Créditos y datos

El mapa ilustrado usa datos de OpenStreetMap. Se conserva `work/osm.json` (ODbL) y se acredita OpenStreetMap junto al mapa. Las fotos y marcas pertenecen a sus titulares; confirmar autorización de uso para una publicación comercial.

El widget se encuentra en `assets/booking-widget.html` como copia local de la plantilla de Operon Reservas (`operon-reservas/src/lib/widget/booking-widget.html`). Si la plantilla cambia, sincronizar esta copia antes del siguiente build.
