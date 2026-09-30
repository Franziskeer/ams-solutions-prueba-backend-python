# AGENTS.md

Prueba técnica: servicio de notificaciones en Python que media entre los clientes y un proveedor externo. El enunciado está en `docs/prueba-tecnica.md`. El README explica cómo ejecutar el proyecto.

## Aplicación

- El código de la aplicación vive en `app/` y escucha en el puerto 5000.
- La aplicación comparte red con el contenedor del proveedor, así que el proveedor está en `http://localhost:3001` y su Swagger en `/docs`.
- `provider/`, `platform/` y `docker-compose.yaml` forman parte de la evaluación y no se modifican.

## Git

- `main` es la rama troncal. Una rama corta por hito: `chore/...` o `feat/...`.
- Un pull request por hito y rebase and merge a `main`.
- Conventional Commits en inglés, sin scope.

## Asistencia al programador

No desarrolles código ni hagas modificaciones a no ser que se solicite expresamente o mediante un plan de desarrollo. Asiste investigando recursos externos, analizando las propuestas y apoyándote en el código y los requerimientos generados.
