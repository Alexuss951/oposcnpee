---
name: temario-content
description: "Add or edit tema content in the Inspector CNP study app — update the TEMAS array in app/index.html, keep temario.csv in sync, add a resumen (one-page summary), fix BOE links, adjust dificultad, or add relaciones between temas. USE WHEN: 'añade el resumen del tema X', 'corrige el enlace BOE del tema Y', 'añade temas relacionados', 'el título del tema está mal', 'falta el área en el tema', 'genera resúmenes de los temas del bloque B', 'sincroniza el CSV con la app'. DO NOT USE FOR: adding a brand-new section/phase to the app (use app-add-section) or general code refactoring."
---

# Skill: temario-content

Workflow para añadir o editar contenido de los 81 temas en la app de oposición Inspector/a CNP.

## Cuándo usar

- Cambiar título, área, norma, palabras clave, relaciones, dificultad o enlaces de un tema.
- Añadir un campo `resumen` (fase 2) — texto denso de ~1 página por tema.
- Sincronizar [`temario.csv`](../../../temario.csv) con el array `TEMAS` de [`app/index.html`](../../../app/index.html).
- Corregir enlaces rotos o que apuntan a versión no consolidada del BOE.

## Cuándo NO usar

- Para añadir una sección nueva a la app (simulador, plan, físico) → usar `app-add-section`.
- Para refactorizar render, CSS o estructura general de la app.

## Reglas duras

1. **Fuente primaria de verdad**: [`documentos/ANEXO II.txt`](../../../documentos/ANEXO%20II.txt) y el PDF del BOE en [`documentos/`](../../../documentos/). El título oficial del tema gana siempre sobre lo que ya hay en la app.
2. **Enlace BOE = texto consolidado**. Formato `https://www.boe.es/buscar/act.php?id=BOE-A-AAAA-NNNNN`. Si solo conoces la URL del DOUE para reglamentos UE, usar `https://www.boe.es/buscar/doc.php?id=DOUE-L-AAAA-NNNNN`. **Nunca** inventar IDs.
3. **`temario.csv` y `TEMAS` deben coincidir** en los 12 campos. Si se edita uno, editar el otro en la misma entrega.
4. **Idioma**: títulos, áreas, normas, palabras clave y resúmenes en **español**. Comentarios del código en **inglés**.
5. **Resúmenes** (cuando aplique): plano, sin emojis, sin "En este tema vamos a ver…". Frases cortas. Datos concretos: artículos, plazos, plazas, requisitos. Si una norma se reformó (p.ej. LO 10/2022 sobre libertad sexual), citar la reforma.

## Pasos

### A) Editar un tema existente

1. Localizar el tema en el array `TEMAS` de [`app/index.html`](../../../app/index.html) (buscar `n:N,`).
2. Editar **solo los campos pedidos**. No tocar el resto.
3. Espejar el cambio en [`temario.csv`](../../../temario.csv) (delimitador `;`, columnas: `Nº;Bloque;Área;Subárea;Título resumido;Norma principal;Palabras clave;Relaciones (Nº);Peso;Dificultad (1-5);Enlace BOE / oficial;Enlace recurso`).
4. Si el cambio afecta a `rel` (relaciones), verificar que los temas citados existen (1–81) y considerar añadir el enlace inverso (si el tema 14 ahora se relaciona con el 7, el 7 quizá deba referenciar al 14).
5. Resumen al usuario: número de tema, qué se cambió, qué queda igual.

### B) Añadir el campo `resumen` (fase 2)

El campo `resumen` aún no existe en el modelo. Cuando se introduzca por primera vez:

1. **Coordinar con `app-add-section`** porque toca también `openTema()` para renderizar el resumen.
2. Formato propuesto del campo:
   ```js
   resumen: [
     "Párrafo 1 (3–6 frases). Conceptos núcleo y norma de referencia con artículo concreto.",
     "Párrafo 2. Procedimiento o clasificación. Plazos clave en negrita usando **markdown ligero**.",
     "Párrafo 3. Excepciones, jurisprudencia relevante, conexión con otros temas."
   ]
   ```
3. Render: añadir bloque `<div class="section"><h3>Resumen</h3>...</div>` en `openTema()`. Procesar `**texto**` → `<strong>` con un mini-parser, no usar librerías.
4. Densidad objetivo: **300–500 palabras por tema**. Bastante para una hoja A4, no tanto que sustituya al manual.

### C) Sincronizar CSV ↔ app

Si el CSV se editó manualmente y la app no, o viceversa:

1. Leer ambos.
2. Detectar diferencias campo a campo.
3. Mostrar al usuario una tabla de diferencias **antes** de aplicar.
4. Aplicar solo tras confirmación.

## Checklist antes de enviar

- [ ] Edité los **dos** sitios (`TEMAS` en la app y `temario.csv`) si el cambio afecta a datos estructurados.
- [ ] No introduje comillas sin escapar en los strings JS (cuidado con apóstrofes españoles: usar `"texto con 'comillas'"` o escapar).
- [ ] Los enlaces BOE son del texto **consolidado**, no del BOE original de publicación.
- [ ] Las relaciones (`rel`) apuntan a temas existentes (1–81).
- [ ] La app sigue abriendo correctamente (estructura JS válida, sin coma final colgante en el último objeto del array).
- [ ] No añadí comentarios narrativos ni "Aprendizaje:" dentro del código.

## Anti-patrones

- ❌ Generar resúmenes por LLM sin contrastar con la norma → enviar el artículo exacto.
- ❌ Usar `boe.es/diario_boe/txt.php?...` (texto del día) como enlace principal → debe ser el consolidado.
- ❌ Cambiar el orden de los campos del objeto tema → el render lee por nombre, pero la consistencia visual ayuda a auditar.
- ❌ Añadir analogías de infraestructura técnica para explicar conceptos jurídicos → la usuaria es abogada, las analogías van con derecho ecuatoriano (ver [AGENTS.md §5](../../../AGENTS.md)).
