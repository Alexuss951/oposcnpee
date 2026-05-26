# Análisis de exámenes — CNP Ejecutiva

Datos: 553 preguntas oficiales (P34-Asc + P36 a P40, 2021-2025) etiquetadas a tema 1-81. Refresco: `python scripts/analyze_exams.py`.

## 1. Lo que cae no es lo que dice el temario

| Bloque | Real | Teórico | Lectura |
|---|---|---|---|
| A jurídicas | 70,3 % | 65 % | Cae **más** de lo previsto. Tu zona fuerte coincide con la zona que más puntúa. |
| B sociales | 13,4 % | 22 % | Cae **menos** de lo previsto. Mala noticia: la poca que cae es difícil (ver punto 2). |
| C técnicas | 16,3 % | 12 % | Cae **más**. Y es tu zona débil. |

→ **Decisión:** el plan prioriza dominio total de A (ya lo tienes a medias) y eleva el tiempo de C por encima de B.

## 2. Dificultad real por bloque

Ratio de preguntas media-difícil sobre el total del bloque:

- A: **39 %** — la mayoría son fáciles si te sabes la literalidad.
- B: **68 %** — caen pocas pero suelen ser conceptuales.
- C: **81 %** — casi todas son media-difícil. Sin base previa, no se improvisan.

→ **Decisión:** `PLAN_MIN_PER_TEMA = A:40, B:75, C:100`. No es arbitrario: refleja el ratio real de dificultad, no el peso porcentual del bloque. Un tema C te cuesta 2,5 × lo que cuesta uno A.

## 3. Los 10 temas calientes (★) — 30 % del examen

| Tema | B | % | Promos | Por qué cae siempre |
|---|---|---|---|---|
| T13 Min Interior · DGP | A | 5,4 | 6/6 | Organigrama de la casa. Lo preguntan literal. |
| T47 Pol Judicial · MF | A | 3,4 | 6/6 | Es el puente CP ↔ LECrim. Pilar del bloque procesal. |
| T14 LO 2/1986 FCS | A | 2,9 | 5/6 | Norma marco del cuerpo. Sin esto no hay temario. |
| T6 Cortes · CGPJ · TC | A | 2,9 | 6/6 | Arquitectura constitucional. Siempre 1-2 preguntas. |
| T72 Contabilidad | C | 2,9 | 5/6 | Único C con literalidad memorizable (cuentas, IVA). |
| T11 Ley 40/2015 AGE | A | 2,5 | 5/6 | Junto a 39/2015 forman el Derecho Admin básico. |
| T8 UE | A | 2,5 | 6/6 | Instituciones europeas + tratados. Memorización pura. |
| T19 LO 4/2015 LOPSC | A | 2,4 | 6/6 | Norma de seguridad ciudadana. Plazos y sanciones. |
| T73 Redes · OSI | C | 2,4 | 6/6 | Conceptos básicos de red, repetidos exámen tras examen. |
| T77 Ciberseguridad · ENS | C | 2,4 | 4/6 | Política nacional ciber, en auge desde 2022. |

→ **Decisión:** estos 10 multiplican su tiempo por 1,5 en el cálculo semanal (`PLAN_TEMA_HOT` en la app). Si cae un día sin tiempo, recortas un tema sin ★ — nunca uno con ★.

→ **Lectura:** 8 de 10 son Bloque A, así que la mayor parte del "30 % seguro" está en tu terreno. Solo necesitas literalidad. Los 3 de C (T72, T73, T77) son los que justifican el esfuerzo extra del bloque débil.

## 4. Top 25 = 52 % del examen

Suma top 10 + T16, T12, T74, T5, T7, T35, T75, T20, T15, T10, T65, T4, T81, T50, T3. Estos 25 cubren la mitad del examen. Los otros 56 temas se reparten la otra mitad → más diluido, menos peso por tema, pero ninguno descartable.

## 5. Cobertura: todos caen

Los 81 temas aparecieron ≥1 vez en las 6 promociones. No hay tema "que no cae nunca". Aun así, dedicar 100 min a un tema sin ★ y 40 a uno con ★ sería un mal uso del tiempo — de ahí el multiplicador.

## 6. Artículos del CP más citados (memoriza literal)

386 (moneda), 174 (tortura), 30 (autoría), 36 (penas), 28, 136, 148, 177 bis, 432, 457. También CE 17/86/146/148, LECrim 509/384 bis/276/579 bis, LOPSC 16/32/33/36/53.

→ **Por qué importa:** las preguntas no piden el espíritu del artículo, piden el número, el plazo o la pena exacta. 12 artículos memorizados literal rinden más que 50 leídos por encima.

## 7. Resumen accionable

1. **A es prioridad.** Es el 70 % real del examen y tu zona fuerte. Aquí solo hay que rematar literalidad española (no conceptos: la dogmática la traes de Ecuador).
2. **C antes que B en tiempo por tema.** B cae menos y aunque sea difícil, su peso total es bajo. C cae más y es más duro: 100 min mínimo por tema.
3. **Los 10 ★ son innegociables.** Si en una semana te quedas sin hora, primero caen los temas sin marcar.
4. **Literalidad > comprensión** para artículos CP/CE/LECrim/LOPSC. Memoriza los ~12 listados arriba al pie de la letra.
5. **Cero descartes.** Todos los temas han caído. Pasarse uno por encima en lugar de saltarlo.

**Truco examen:** entre repasar 1 tema ★ o 2 sin marcar en la misma hora, repasa el ★. La probabilidad de que caiga es 5-6 × mayor.
