# Tierra Adentro · Posadas en Purmamarca

Sitio estático de Tierra Adentro, con las sedes Gorriti y Lavalle. La fuente editable es `src.html`; `build.py` genera `index.html` y el deploy listo para Netlify en `dist/`.

## Build y preview

Requiere Python 3 (solo biblioteca estándar):

```powershell
python -X utf8 build.py
python -m http.server 8000 --directory dist
```

El repositorio incluye los insumos del mapa y del logo, además de una copia versionada del widget usado por esta página, para que el build no dependa de una ruta privada de una computadora.

## Estado de publicación

- Preview actualmente disponible en `https://tierra-adentro-purmamarca.netlify.app/`.
- La preview lleva `noindex,nofollow`. No quitarlo ni añadir sitemap/canonical de producción hasta contar con el dominio oficial y la aprobación de publicación del cliente.
- Al confirmar el dominio, actualizar el origen Netlify en metadatos Open Graph/Twitter y JSON-LD; después habilitar indexación, crear `robots.txt` y `sitemap.xml`, conectar Search Console y enviar el sitemap.
- Las direcciones visibles del sitio y las fichas separadas están respaldadas por el listado oficial de alojamientos de Purmamarca. Confirmar con el cliente horarios, servicios, fotos y textos antes del lanzamiento definitivo.

## Créditos y datos

El mapa ilustrado usa datos de OpenStreetMap. Se conserva `work/osm.json` (ODbL) y se acredita OpenStreetMap junto al mapa. Las fotos y marcas pertenecen a sus titulares; confirmar autorización de uso para una publicación comercial.

El widget se encuentra en `assets/booking-widget-demo.html` como copia local del componente compartido de Operon usado al generar esta versión. Si el componente compartido cambia, sincronizar esta copia antes del siguiente build.
