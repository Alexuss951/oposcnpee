# Checklist de verificación rápida

Úsala antes y después de cambios en `docs/index.html`. La prueba debe realizarse
tanto abriendo `docs/index.html` mediante `file://` como desde GitHub Pages.
Emplea datos ficticios y conserva antes una exportación del progreso real.

## Comprobaciones automáticas

- [ ] `wsl -d Ubuntu python3 scripts/compile_preguntas.py --check`
- [ ] `wsl -d Ubuntu python3 scripts/sanitize_fase0.py --dry-run`
- [ ] El banco contiene 1.177 preguntas y 81 temas.
- [ ] No quedan referencias activas a normativa derogada fuera de preguntas
  históricas claramente advertidas.

## Recorrido funcional

- [ ] Inicio carga estadísticas, racha y objetivo diario sin errores visibles.
- [ ] Las nueve vistas abren desde la barra lateral y la navegación móvil.
- [ ] Un tema abre resumen, tips, flashcards, notas y enlaces oficiales.
- [ ] Búsqueda localiza temas y preguntas; filtros y navegación funcionan.
- [ ] Examen real inicia, responde, deja blancos, finaliza y guarda historial.
- [ ] Un examen interrumpido puede reanudarse sin perder respuestas ni tiempo.
- [ ] Fallos, marcadas, etiquetas y repetición espaciada conservan su estado.
- [ ] El plan permite marcar tareas y exportar un calendario ICS válido.
- [ ] El psicotécnico permite responder, revisar y guardar el resultado.
- [ ] El plan físico registra marcas y sesiones; voz y Wake Lock fallan de forma
  segura cuando el navegador no los soporta.

## Persistencia y compatibilidad

- [ ] Exportar progreso produce JSON descargable con todas las claves
  `opos-cnp:`.
- [ ] Importar ese JSON en un perfil de prueba restaura exactamente el estado.
- [ ] Cancelar una importación no modifica el progreso existente.
- [ ] Tema claro/oscuro y navegación siguen funcionando después de recargar.
- [ ] La aplicación funciona sin red y no realiza peticiones necesarias para
  arrancar o estudiar.

## Contenido jurídico

- [ ] Convocatoria, temario y baremos citan el BOE vigente.
- [ ] Cada dato jurídico modificado se contrastó con el texto consolidado del
  BOE y se anotó la fecha de revisión.
- [ ] Los enunciados de exámenes anteriores se conservan; si la respuesta o la
  terminología quedó obsoleta, la explicación muestra la regla vigente.

## Línea base del 27-ago-2026

- Compilador: 1.177 preguntas, 140 explicaciones, 10 sin tema; `--check` OK.
- Saneamiento fase 0: 0 ficheros y 0 cambios pendientes.
- Temario: 81 epígrafes, coincidentes con el Anexo II de BOE-A-2026-15054.
- Chrome/localhost: carga correcta y sin errores de consola visibles en el arranque.
- Enlaces profundos: las nueve vistas y `#tema-15` conservan la ruta tras recargar.
- Navegación desde `#tema-15` a `#examenes`: correcta; el detalle se cierra sin
  sobrescribir el destino.
- Psicotécnico: recorrido de cinco preguntas completado; revisión, penalización,
  blancos e historial comprobados. Se corrigió el refresco inmediato del historial
  al cerrar el resultado.
- Exportación/importación: la descarga JSON v1 contiene ajustes e historiales; la
  misma copia restaura meta, tema e historial. Un JSON corrupto se rechaza sin
  modificar la meta existente.
- Vista móvil (390 × 844): `#examenes` carga sin desbordamiento horizontal y mantiene
  accesibles modos, cabecera y navegación inferior.
- Consola del navegador: sin errores ni avisos durante los recorridos anteriores.
- Examen oficial: pausa, recarga, reanudación y finalización verificadas; conserva
  respuesta, marca y etiqueta. El fallo aparece en el cuaderno y habilita Fallos,
  Marcadas y SRS también después de recargar.
- Plan: marcado de tema persistente e ICS descargado y validado (1.513 eventos,
  cabecera/cierre VCALENDAR y examen estimado).
- Físico: marca de 1000 m y sesión diaria persistentes; sesión guiada probada con
  voz, silencio, pausa, avance y cierre, sin errores de consola ni de Wake Lock.
- Ayuda: glosario corregido a 9 modos y meta inicial de 20 preguntas.
- Offline: estructura autocontenida confirmada (sin scripts, CSS, imágenes ni
  peticiones de red necesarias). La apertura automatizada por `file://` queda
  pendiente de comprobación manual porque la política del navegador de pruebas
  bloquea ese esquema.
