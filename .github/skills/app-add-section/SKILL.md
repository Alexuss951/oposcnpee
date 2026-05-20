---
name: app-add-section
description: "Add a new section/phase to the single-file Inspector CNP study app (app/index.html) — exam simulator, study plan view, physical training routines, or any other top-level area. Wires bottom navigation, view containers, route handling and a data array, all without breaking the offline single-file constraint. USE WHEN: 'añade el simulador de test', 'añade la pestaña del plan de estudio', 'crea la sección de físico', 'añade una sección nueva a la app', 'fase 3 / 4 / 5 de la app'. DO NOT USE FOR: editing tema content (use temario-content) or pure CSS tweaks on the existing temario view."
---

# Skill: app-add-section

Workflow para añadir una **fase nueva** a la app sin romper el patrón single-file offline.

## Cuándo usar

- Fase 2 — Resúmenes densos dentro del detalle de tema (cambio dentro de la sección existente, pero ver nota abajo).
- Fase 3 — Simulador de test (100 preguntas / 50 min, fórmula `(A − E/2)/10`).
- Fase 4 — Vista navegable del plan de estudio.
- Fase 5 — Rutinas de entrenamiento físico (agilidad, barra supina, 1000 m).
- Cualquier nueva pestaña principal.

> Nota: la fase 2 (resúmenes dentro del tema) toca también el modelo de datos — coordinar con [`temario-content`](../temario-content/SKILL.md).

## Cuándo NO usar

- Para cambiar contenido de un tema existente → `temario-content`.
- Para ajustes de estilo (colores, tipografías, espaciado) sin nueva sección.

## Reglas duras (no negociables)

1. **Sigue siendo un solo fichero**: [`app/index.html`](../../../app/index.html). Sin nuevos `.js`, `.css`, `.html`, sin imágenes externas, sin CDN.
2. **Offline real**. Nada de `fetch()` a internet en runtime.
3. **No introducir frameworks ni bundlers**. Vanilla JS, CSS y HTML.
4. **El temario sigue funcionando intacto** después del cambio (probar abriendo el fichero).
5. **Datos al final del `<script>`**, en arrays/objetos JS literales editables a mano.
6. **`localStorage` namespaced** con prefijo `opos-cnp:` (p.ej. `opos-cnp:test:resultados`, `opos-cnp:plan:tareas-hechas`).

## Patrón arquitectónico a respetar

```
<body>
  <header>             ← común a toda la app (1 vez)
  <nav class="bottom-nav">  ← (a introducir en fase 2+) botones de fases
  <main>
    <section id="view-temario" class="view active">...</section>
    <section id="view-test"    class="view">...</section>
    <section id="view-plan"    class="view">...</section>
    <section id="view-fisico"  class="view">...</section>
  </main>
  <script>
    const TEMAS = [...];       // ya existe
    const PREGUNTAS = [...];   // nueva en fase 3
    const PLAN = [...];        // nueva en fase 4
    const FISICO = [...];      // nueva en fase 5

    // router muy simple por hash o por click en nav
    function showView(id) { ... }
  </script>
```

Solo una `.view` lleva la clase `active` (display:block); las demás `display:none`. Bottom nav fija con `position: sticky; bottom: 0` y safe-area inset para iOS.

## Pasos

### 1. Diseñar primero, mostrar al usuario

- Boceto en texto: qué muestra la pantalla, cómo se navega, qué datos necesita, qué se persiste en localStorage.
- Estimar tamaño del array de datos (¿100 preguntas? ¿22 semanas? ¿3 rutinas?).
- **Confirmar con el usuario antes de tocar código.**

### 2. Implementar en orden

1. **Bottom nav** (solo si es la primera fase nueva que la introduce). 4 botones max, iconos con emojis o SVG inline pequeños.
2. **CSS** para `.view` y `.view.active`, más estilos específicos de la nueva sección. Reutiliza variables `--bg`, `--panel`, `--accent`, etc.
3. **Contenedor `<section id="view-X" class="view">`** vacío en el HTML.
4. **Array de datos** al final del script, con comentario en inglés indicando esquema.
5. **Función `render<Section>()`** que pinta la sección.
6. **Router**: ampliar la lógica del hash (`#temario`, `#test`, `#plan`, `#fisico`) para incluir la nueva.
7. **Persistencia localStorage** si aplica, siempre con prefijo `opos-cnp:`.

### 3. Detalles por fase

#### Simulador de test (fase 3)
- **Fórmula corrección oficial**: `nota = (A − E / (n − 1)) · 10 / P` donde `n = 3` alternativas y `P = 100` preguntas. Simplificada: `(A − E/2) / 10`.
- Mostrar nota final con 2 decimales. Aviso si nota < 3 ("eliminatorio").
- Cronómetro 50 minutos. Pausa al cambiar de pestaña del navegador → guarda estado en localStorage.
- Banco de preguntas: array de objetos `{ id, tema: N, enunciado, opciones: [a, b, c], correcta: 0|1|2, fuente: "url o referencia" }`.
- Permitir filtrar por bloque/tema antes de empezar.
- Al terminar: revisión pregunta a pregunta con explicación y enlace al tema relacionado.

#### Plan de estudio (fase 4)
- Parsear (o transcribir manualmente) [`plan-estudio.md`](../../../plan-estudio.md) a un array de semanas.
- Vista de timeline vertical: semana → bloques de estudio → checkboxes persistentes.
- Botón "semana actual" calculado contra la fecha del examen.

#### Físico (fase 5)
- 3 tarjetas (agilidad, barra supina, 1000 m) con:
  - Tabla de baremos mujeres (ver [AGENTS.md](../../../AGENTS.md) si se añade allí, o session memory).
  - Rutina semanal sugerida.
  - Registro de marcas personales (localStorage) con mini-gráfico ASCII o canvas sencillo.

## Checklist antes de enviar

- [ ] La app sigue siendo **un solo fichero**.
- [ ] No hay `fetch()`, `import`, `<script src=...>` ni `<link href=...>` externos.
- [ ] El temario sigue funcionando exactamente como antes (probado abriendo el fichero).
- [ ] La nueva sección funciona offline.
- [ ] `localStorage` con prefijo `opos-cnp:`.
- [ ] CSS reutiliza las variables del `:root` existente.
- [ ] Comentarios en inglés, UI en español.
- [ ] Sin librerías. Sin frameworks. Sin emojis decorativos en UI salvo si el usuario los pidió.
- [ ] Tamaño total del fichero todavía manejable (< 500 KB tras añadir datos; revisar si crece más).

## Anti-patrones

- ❌ Dividir en varios ficheros "para limpieza" → rompe el principio.
- ❌ Añadir un service worker / manifest sin confirmación → la app no es PWA hoy.
- ❌ Implementar el simulador con sólo 10 preguntas hardcodeadas y llamar a eso "fase 3 completa" → confirmar volumen con el usuario antes.
- ❌ Reescribir el render del temario "de paso" mientras se añade otra sección.
- ❌ Tocar el modelo de datos `TEMAS` desde esta skill → eso pertenece a `temario-content`.
