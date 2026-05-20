# Oposición Inspector/a CNP — App de estudio

Aplicación **offline** de estudio para la oposición **Escala Ejecutiva (Inspector/a) del Cuerpo Nacional de Policía** (España, convocatoria BOE 11-ago-2025, ~150 plazas, examen previsto ~octubre 2026).

La usuaria es **abogada formada en Ecuador**. La app es personal, no es producto comercial.

---

## 1. Intención (no romper)

- **Un único archivo HTML** ([app/index.html](app/index.html)), sin build, sin dependencias, sin red.
- Debe abrirse haciendo doble clic en Windows **y** desde el navegador del móvil (subir a OneDrive/Drive → descargar → abrir).
- **Mobile-first**. Tap targets grandes, tema oscuro por defecto.
- **UI en español**. **Comentarios y nombres de variables en inglés**.
- Datos embebidos en arrays JS al final del fichero (fácil de ampliar a mano).
- `localStorage` para progreso (cuando se añada). Nada en backend, nada en cookies.

Si una propuesta rompe alguno de estos puntos (build tools, npm, fetch a APIs externas, frameworks, multi-archivo con `import`), **pídeme confirmación antes**.

---

## 2. Estado por fases

| Fase | Estado | Contenido |
|------|--------|-----------|
| 1 — Temario | ✅ entregada | Lista 81 temas, buscador, filtro por bloque, detalle por tema, enlaces BOE, navegación entre temas relacionados |
| 2 — Resúmenes densos | ⏳ pendiente | Resumen ~1 página por tema dentro del detalle |
| 3 — Simulador test | ⏳ pendiente | 100 preguntas / 50 min, fórmula `(A − E/2)/10`, banco ampliable |
| 4 — Plan de estudio | ⏳ pendiente | Vista navegable de [plan-estudio.md](plan-estudio.md) |
| 5 — Físico | ⏳ pendiente | Rutinas para las 3 pruebas (agilidad, barra supina, 1000 m) |

Trabajamos **una fase a la vez**. No mezcles fases en la misma entrega salvo que se pida.

---

## 3. Arquitectura de la app

[app/index.html](app/index.html) — único entregable. Estructura interna:

```
<head>
  <style>  → CSS inline. Variables CSS en :root. Mobile-first, breakpoints 720px y 1100px.
<body>
  <header>          → título + subtítulo
  <div.toolbar>     → buscador + chips filtro (Todos / A / B / C)
  <main><div#list>  → grid de tarjetas
  <div#detail>      → overlay full-screen para vista detalle (se desliza desde la derecha)
  <script>
    const TEMAS = [ /* 81 objetos */ ];   ← fuente de datos
    // helpers: escapeHtml, renderList, openTema, closeDetail
    // event wiring al final
```

**Modelo de datos de un tema** (no cambiar campos sin actualizar render):

```js
{
  n: 14,              // número 1-81
  b: "A",             // bloque "A" | "B" | "C"
  a: "Organización policial",   // área (string corto)
  t: "LO 2/1986 ...", // título del tema
  norma: "LO 2/1986", // norma principal (string)
  keys: ["FCS", ...], // palabras clave (array)
  rel: [7, 13, 18],   // números de temas relacionados
  d: 4,               // dificultad 1-5
  boe: "https://...", // URL oficial (BOE consolidado preferido)
  rec: "https://..."  // URL recurso complementario (puede ser "")
}
```

Cuando llegue la fase 2, se añadirá un campo `resumen` (string Markdown ligero o array de párrafos). Ver [temario-content skill](.github/skills/temario-content/SKILL.md).

---

## 4. Fuentes de datos (orden de autoridad)

1. [documentos/ANEXO II.txt](documentos/ANEXO%20II.txt) y [documentos/BOE-A-2025-16611.pdf](documentos/BOE-A-2025-16611.pdf) — **fuente primaria** del temario. Si hay duda, gana esto.
2. [temario.csv](temario.csv) — versión estructurada de los 81 temas con enlaces BOE. **Debe mantenerse sincronizado con el array `TEMAS` de la app.**
3. [plan-estudio.md](plan-estudio.md) — plan de 22 semanas (futura fase 4).
4. [recursos.md](recursos.md) — enlaces oficiales por bloque (BOE, AEPD, INCIBE, CCN-CERT, DGT, Guardia Civil).
5. [examenes/fuentes-exams.txt](examenes/fuentes-exams.txt) — fuentes de exámenes pasados (futura fase 3).

---

## 5. Convenciones de contenido

- **Enlaces a leyes**: siempre usar el **texto consolidado** del BOE (`boe.es/buscar/act.php?id=...`), no la versión publicada el día X.
- **Idioma del usuario en chat**: responde en **español** (cambia a inglés sólo si la usuaria escribe en inglés).
- **Analogías**: usa derecho **ecuatoriano** para explicar conceptos españoles (COIP ↔ CP, COGEP ↔ LECrim, Constitución Montecristi 2008 ↔ CE 1978, acción de protección ↔ recurso de amparo, LOSEP ↔ EBEP, Consejo de la Judicatura ↔ CGPJ, Defensoría del Pueblo ↔ Defensor del Pueblo). **No** uses analogías de infraestructura / sysadmin con esta usuaria — es abogada, no ingeniera.
- **Sin jerga policial sin explicar** la primera vez (FCS, DGP, SES, AEPD, CNPIC, ENS, OEDE…).
- **Sin frases de IA**: no "Ahora vamos a…", no "Una vez tengamos una ejecución verde…", no narrar el proceso de razonamiento dentro del código ni de los resúmenes.

---

## 6. Convenciones de código (revisar antes de enviar)

- HTML5, CSS y JS vanilla. **Cero dependencias externas**, cero `<link>` o `<script src=...>` a CDN.
- Comentarios y nombres de variables en **inglés**, cortos, explican el *qué* o el *por qué*, no la historia.
- Renderizado de strings de datos → **siempre** vía `escapeHtml()`. Los datos pueden contener `<`, `&`, comillas.
- Selectores con `id` para nodos únicos, `data-*` para hooks de evento delegado.
- Sin frameworks. Sin TypeScript. Sin transpiler.
- No usar `innerHTML += ...` en bucles; construir string y asignar una vez.
- LocalStorage namespaced: prefijo `opos-cnp:` (p.ej. `opos-cnp:leidos`, `opos-cnp:test:v1`).

---

## 7. Tareas comunes → skill correspondiente

| Quieres… | Usa |
|----------|-----|
| Añadir/editar contenido de un tema (resúmenes, enlaces, relaciones) | [temario-content](.github/skills/temario-content/SKILL.md) |
| Añadir una nueva sección/fase a la app (simulador, plan, físico) | [app-add-section](.github/skills/app-add-section/SKILL.md) |

---

## 8. Qué **no** hacer

- ❌ Convertir la app a React/Vue/Svelte/Next.
- ❌ Añadir `package.json`, bundler, build step.
- ❌ Llamar a APIs externas en runtime (fetch a la AEPD, BOE, etc.). Los enlaces se abren en pestaña nueva, no se consumen.
- ❌ Crear un nuevo `.md` para "documentar el cambio" salvo que se pida explícitamente.
- ❌ Inventar URLs de leyes. Si no tienes el ID BOE, déjalo vacío y avísame.
- ❌ Cambiar la estructura de un objeto tema sin actualizar `renderList` y `openTema` a la vez.
