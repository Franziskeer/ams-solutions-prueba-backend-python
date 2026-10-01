# AMS Solutions - Prueba técnica backend Python

Servicio de notificaciones que hace de mediador entre los clientes y un proveedor externo. El enunciado está en [docs/prueba-tecnica.md](docs/prueba-tecnica.md).

## Versiones

- La solución para la prueba técnica ha sido desarrollada en la carpeta `app` con la versión 3.12 de Python.

## Cómo ejecutarlo

Es necesario tener instalado Docker.

Levantar el proveedor y la infraestructura de evaluación:

```bash
docker-compose up -d provider influxdb grafana
```

Levantar la aplicación:

```bash
docker-compose up -d --build app
```

Ejecutar el test de carga:

```bash
docker-compose run --rm load-test
```

Los resultados se ven en [Grafana](http://localhost:3000/d/backend-performance-scorecard/).

**NOTA:** Para agilizar el desarrollo y no tener que hacer rebuild de la aplicación constantemente he usado un entorno virtual de Python para tener levantado el servicio de uvicorn constantemente y aprovechar el hot reloading. El resto de servicios se manejan de la misma forma con Docker, pero el app lo lanzo en modo desarrollo así:

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate
cd app
uvicorn main:app --reload --port 5001
```

El puerto 5001 evita chocar con el 5000, que publica el contenedor del proveedor para la aplicación dockerizada y que es el que usa el test de carga.

## Decisiones de diseño

### Estructura por dominio

```text
app/
  main.py               # crea la app FastAPI y monta los routers bajo /v1
  config.py             # configuración leída del entorno
  notifications/
    router.py           # endpoints de /v1/requests
    provider.py         # cliente del proveedor externo
```

El código se agrupa por dominio y no por capas. Todo lo que tiene que ver con las notificaciones vive junto, y un dominio nuevo sería otra carpeta al mismo nivel.

### Configuración

`config.py` lee del entorno la URL y la API key del proveedor. Para la prueba técnica se asumen usar los valores configurados como valores por defecto, pero en un entorno real se consideraría información sensible y habría que protegerlas con variables de entorno o almacenes seguros.

| Variable            | Valor por defecto       |
| ------------------- | ----------------------- |
| `PROVIDER_BASE_URL` | `http://localhost:3001` |
| `PROVIDER_API_KEY`  | `test-dev-2026`         |

### Cliente del proveedor

`notifications/provider.py` es un adaptador sobre `POST /v1/notify`.

- Usa un único `httpx.AsyncClient` por instancia para reutilizar conexiones bajo carga.
- Devuelve el `provider_id` cuando la respuesta es 200.
- Cualquier otro resultado lanza `ProviderError`: los 401, 429 y 500 con su código HTTP, y los errores de red o el timeout de 5 segundos con `status_code=None`.
- No reintenta ni decide el estado final de la solicitud. Esa responsabilidad queda fuera del adaptador, en la capa que orquesta el procesamiento.
