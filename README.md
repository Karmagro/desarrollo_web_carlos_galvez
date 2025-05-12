# Tarea 2 – CC5002 – Desarrollo de Aplicaciones Web

Este repositorio contiene la implementación de la Tarea 2 del curso CC5002 (Desarrollo de Aplicaciones Web), desarrollada con **Flask + MySQL**. El objetivo fue extender el prototipo de la Tarea 1 e implementar una aplicación funcional con formularios validados, almacenamiento en base de datos y navegación completa. Todavia falta la implementacion de las estadisticas.

## Decisiones de implementación

### Estructura del proyecto

- El proyecto usa la estructura recomendada para aplicaciones Flask modulares.
- Se separaro en carpetas: `app/` contiene templates, modelos y rutas, mientras que `run.py` y `config.py` están en la raíz.
- Se creó un `Blueprint` principal (`main`) para registrar todas las rutas.
- Se utilizó un único archivo CSS (`styles.css`) para mantener el diseño centralizado y limpio.

### Reutilización de componentes

- Se implementó un sistema de plantillas con `layout.html` y `_header.html`, permitiendo reutilizar elementos comunes en todas las páginas como el menú de navegación.
- Se evitó la duplicación de código HTML en los templates.

### Validaciones (HTML, JS + Backend)

- Todas las validaciones del formulario están implementadas con funciones individuales en JS, dentro del mismo archivo HTML (`agregar.html`), separando responsabilidades para cada campo (correo, teléfono, redes sociales, fechas, temas, fotos, etc.).
- Las validaciones del lado servidor están implementadas como funciones auxiliares (`verify_*`) en `routes.py`, asegurando consistencia y claridad.

### Base de datos

- Los modelos están definidos en `models.py`.
- Para evitar dependencias circulares, la instancia de SQLAlchemy se declaró en `extensions.py`.
- Se usaron `Enum` para los campos de contacto (`ContactosEnum`) y tema (`TemaEnum`), asegurando consistencia entre los datos del frontend y la base de datos.
- Se implementaron relaciones entre las tablas (`Actividad`, `ActividadTema`, `Foto`, `ContactarPor`) con `relationship()` y `lazy='joined'` para mejorar la eficiencia con joins.

### Manejo de fotos

- Los archivos se renombran con un `UUID` único más el nombre original usando `secure_filename` para evitar colisiones.
- Las imágenes se almacenan en `static/uploads`.

### Interfaz dinámica

- La carga de comunas según la región se realiza en el navegador usando un objeto JSON (`comunas_json`) generado desde Flask y embebido en el HTML.
- No se crearon archivos `.js` separados, todo el JavaScript está dentro de los templates para mantener el prototipo autocontenido y claro.

---

Desarrollado por: Carlos Galvez Romo

Curso: CC5002 – Desarrollo de Aplicaciones Web – 2025-1

Profesor: José Urzúa
