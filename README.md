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
