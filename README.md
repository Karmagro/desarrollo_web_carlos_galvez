# Tarea 3 – CC5002 – Desarrollo de Aplicaciones Web

Este repositorio contiene la extension de la Tarea 2 del curso CC5002, en donde se incorpora:

- Estadísticas dinamicas obtenidas desde la base de datos.
- Comentarios en cada actividad, con formulario para ingresar uno nuevo.

Ambas funcionalidades se integran en la aplicación ya desarrollada con Flask y MySQL.

---

## Decisiones de implementación

### Estadísticas

- Se implementaron tres rutas en Flask que llaman a la base de datos:
  - `/api/estadisticas/actividades-por-dia`
  - `/api/estadisticas/actividades-por-tipo`
  - `/api/estadisticas/actividades-por-mes-y-horario`
- Los datos se procesan en el servidor con SQLAlchemy.
- En el cliente, se utiliza `fetch()` para cargar los datos via AJAX y generar graficos con `Chart.js`.
- Se incluyeron mensajes de “cargando” y manejo de errores visibles en cada grafico.

### Comentarios

- Se agrego soporte completo para comentar actividades.
  - Formulario de comentario con validación en JS y Python.
  - Envio async usando `fetch()` (`POST` a `/api/comentarios/<id>`).
  - Listado de comentarios cargado dinamicamente desde la ruta `GET /api/comentarios/<id>`.
- Protección contra XSS usando `escapeHtml()` en el frontend.
- En el backend se usan funciones auxiliares como `verify_comment_name` y `verify_comment_text` para verificar que los datos cumplan los requisitos.

### Otros detalles

- Se mantuvo la estructura modular con `routes.py`, `models.py`, `templates/`, etc...
- Todas las nuevas rutas de API siguen una convención clara (`/api/...`).
- Se reutilizaron estilos, layout y navegacion existentes para integrar las nuevas secciones.

---

Desarrollado por: Carlos Galvez Romo

Curso: CC5002 – Desarrollo de Aplicaciones Web – 2025-1

Profesor: José Urzúa
