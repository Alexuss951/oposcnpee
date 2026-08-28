# Make — Agente de vigilancia BOE para oposición CNP

> Guía paso a paso para montar en **Make.com** un agente que vigila el BOE
> diariamente y te envía email solo cuando se reforma una norma de tu
> temario (Escala Ejecutiva, convocatoria [BOE-A-2026-15054](BOE-A-2026-15054.pdf)).
>
> Fuente de los IDs: [normativa-vigilancia-boe.md](normativa-vigilancia-boe.md)
> Tiempo estimado de setup: **30 minutos**.
> Mantenimiento esperado: **5 minutos al año** (ver sección de mantenimiento).

---

## Tabla de contenidos

1. [Resumen del agente](#resumen-del-agente)
2. [Pre-requisitos](#pre-requisitos)
3. [Diseño del escenario (versión real implementada)](#diseño-del-escenario-versión-real-implementada)
4. [Setup paso a paso](#setup-paso-a-paso)
5. [Lista de IDs `BOE-A-…` para el filtro principal](#lista-de-ids-boe-a-para-el-filtro-principal)
6. [Lista de palabras clave para el filtro "red de seguridad"](#lista-de-palabras-clave-para-el-filtro-red-de-seguridad)
7. [Plantilla del email](#plantilla-del-email)
8. [Alternativa: vigilar también otras secciones del BOE](#alternativa-vigilar-también-otras-secciones-del-boe)
9. [Lecciones aprendidas (errores a no repetir)](#lecciones-aprendidas-errores-a-no-repetir)
10. [Mantenimiento](#mantenimiento)
11. [Solución de problemas](#solución-de-problemas)

---

## Resumen del agente

| Aspecto | Valor |
|---|---|
| Plataforma | Make.com (free tier, 1000 ops/mes) |
| Frecuencia | 1 ejecución/día por escenario a las 10:00 CET |
| Coste ops/mes | ~300 con 2 escenarios activos (Sección I + II.B) |
| Fuentes | RSS oficiales BOE (catálogo en https://www.boe.es/rss/) |
| Salida | Email solo cuando hay matches (no spam) |
| Envío email | Gmail OAuth (no SMTP) |
| Estado actual | 2 escenarios activos: `BOE actualizaciones temario` (s=1) + `BOE Oposiciones CNP` (s=2B) |

**Qué dispara un email** (en cada escenario):
1. **Match por título** — el título del artículo contiene una palabra clave del temario (extranjería, seguridad ciudadana, código penal, escala ejecutiva, etc.).
2. **Match por link** — el link incluye uno de los ~40 IDs `BOE-A-…` de tus normas centrales (CE, LO 2/1986, LO 4/2015, etc.).

Filtro implementado como **una sola condición con OR rules**, no como Router con ramas separadas. Más simple, mismo resultado.

---

## Pre-requisitos

- Cuenta gratis en https://www.make.com/en/register.
- Cuenta de Gmail con 2FA activado.
- **Recomendado: módulo Gmail con OAuth** (lo que usamos). Te pide permisos una vez, listo. No tocas contraseñas ni App Passwords.
- Alternativa SMTP con App Password (https://myaccount.google.com/apppasswords): más pasos y peor entregabilidad (suele ir a spam). Solo si por alguna razón no puedes usar OAuth.

---

## Diseño del escenario (versión real implementada)

Una sola cadena lineal de 5 módulos + 2 filtros. Más simple que la versión inicial planeada con Router: un Router con 2 ramas (CRÍTICA/REVISAR) era innecesario porque el email final no diferencia visualmente entre ambos tipos. Si en el futuro quieres distinguirlos, se vuelve a meter el Router.

```
┌─────────────────────────────────────────────────────────────┐
│ 1. HTTP > Make a request    (con Schedule daily configurado │
│    GET https://www.boe.es/rss/boe.php?s=1     en el reloj   │
│    Headers: User-Agent + Accept             del módulo)     │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│ 2. XML > Parse XML                                          │
│    XML = {{1.data}}                                         │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│ 3. Flow Control > Iterator                                  │
│    Array = {{2.rss.channel[].item[]}}                       │
└──────────────┬──────────────────────────────────────────────┘
               │
               │  ⊘ Filter "Solo temario CNP"
               │     (OR rule 1): title MATCHES keywords regex
               │     (OR rule 2): link  MATCHES IDs regex
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Tools > Text aggregator                                  │
│    Source = Iterator [3]                                    │
│    Text = <li><a href="{{3.link[]}}">{{3.title[]}}</a></li> │
└──────────────┬──────────────────────────────────────────────┘
               │
               │  ⊘ Filter "Solo si hay matches"
               │     condition: {{4.text}} Exists
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Gmail > Send an Email     (OAuth, no SMTP)               │
│    Body type = Raw HTML                                     │
│    Content  = <h2>BOE Sección I — {{formatDate(now;         │
│                "DD/MM/YYYY")}}</h2><ul>{{4.text}}</ul>      │
└─────────────────────────────────────────────────────────────┘
```

### Escenarios activos en la cuenta Make

| Nombre | Sección | URL | Schedule |
|---|---|---|---|
| **BOE actualizaciones temario** | I (Disposiciones generales) | `boe.php?s=1` | Daily 10:00 CET |
| **BOE Oposiciones CNP** | II.B (Oposiciones y concursos) | `boe.php?s=2B` | Daily 10:00 CET |

Ambos usan el mismo patrón. Solo cambian:
- URL del HTTP (s=1 vs s=2B).
- Regex del filtro "Solo temario CNP" (palabras clave generales vs palabras enfocadas a la convocatoria).
- Subject del email.

---

## Setup paso a paso

> Esta sección refleja lo realmente construido. Si vas a montar un escenario nuevo (por ejemplo Sección III), clona uno existente en Make ("..." > Clone) y solo cambia URL + regex del filtro + subject del email. Es 10× más rápido que montar desde cero.

### Paso 1 — Crear el escenario

1. Login en Make → **Scenarios** → **Create a new scenario**.
2. Nombre descriptivo, NO "test" (vas a usarlo en producción). Ejemplos:
   - `BOE actualizaciones temario`
   - `BOE Oposiciones CNP`

### Paso 2 — HTTP > Make a request

1. Click en el círculo central → busca **HTTP** → elige **`Make a request`**.
2. **URL**: `https://www.boe.es/rss/boe.php?s=1` (Sección I). Para Sección II.B usa `s=2B`, para Sección III usa `s=3`.
3. **Method**: `GET`.
4. **Headers**: añade 2 cabeceras (click *Add* dos veces):
   - `User-Agent` → `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`
   - `Accept` → `application/rss+xml, application/xml;q=0.9, */*;q=0.8`
5. **Parse response**: `No` (lo parseamos en el siguiente módulo).
6. **OK**.

> **Por qué los headers**: aunque hoy el BOE responde sin ellos, los servicios públicos pueden bloquear clientes sin User-Agent reconocible. Mejor prevenir.

### Paso 3 — XML > Parse XML

1. Añade módulo **`XML > Parse XML`** detrás del HTTP.
2. **Data structure**: déjalo vacío (no es necesario crear estructura predefinida).
3. **XML**: click en el campo → panel derecho → `1. HTTP > Data`. Queda `{{1.data}}`.
4. **OK**.

> Si Make te avisa "no estás usando el output de este módulo", es solo un warning. Click *Run anyway*. Desaparece cuando conectes el siguiente módulo.

### Paso 4 — Flow Control > Iterator

1. Añade **`Flow Control > Iterator`**.
2. **Array**: click en el campo → panel derecho → navega `2. XML > rss > channel[] > 1 > item[]`. Queda algo como `{{2.rss.channel[].item[]}}`.
3. **OK**.

> **Trampa común**: iterar sobre `channel[]` da 1 bundle inútil (el canal entero). Hay que bajar un nivel más hasta `item[]` para obtener un bundle por artículo del BOE.

### Paso 5 — Filtro "Solo temario CNP" (entre Iterator y Aggregator)

1. Pasa el ratón por la línea que une Iterator con el siguiente módulo. Aparece un icono de llave inglesa 🔧. Click.
2. **Label**: `Solo temario CNP`.
3. **Condition 1**:
   - Field 1: `3. Iterator > title[]`.
   - Operator: `Text operators: Matches pattern (case insensitive)`.
   - Value: la **regex de palabras clave** (sección 6 de este documento).
4. Click **Add OR rule**:
   - Field 1: `3. Iterator > link[]`.
   - Operator: `Text operators: Matches pattern (case insensitive)`.
   - Value: la **regex de IDs** (sección 5).
5. **Save**.

> **OR rule** = pasa si CUALQUIERA de las dos condiciones es cierta. Atrapamos por palabras clave en el título O por ID de norma vigilada en el link.

### Paso 6 — Tools > Text aggregator

1. Añade **`Tools > Text aggregator`** detrás del filtro.
2. **Source Module**: `Iterator [3]`.
3. **Text**: pega tal cual:
   ```
   <li><a href="{{3.link[]}}">{{3.title[]}}</a></li>
   ```
   Insertar `{{3.link[]}}` y `{{3.title[]}}` desde el panel derecho.
4. **Save**.

### Paso 7 — Filtro "Solo si hay matches"

1. Línea entre Text aggregator y el módulo email → click en llave inglesa.
2. **Label**: `Solo si hay matches`.
3. **Condition**:
   - Field 1: `4. Text aggregator > Text`.
   - Operator: `Text operators: Exists` (o `Not equal to` con value vacío).
4. **Save**.

### Paso 8 — Gmail > Send an Email

1. Añade **`Gmail > Send an Email`** (no SMTP genérico).
2. **Connection**: click *Add*. Se abre OAuth de Google.
   - Elige tu cuenta.
   - En el aviso "Make hasn't been verified" → *Advanced* → *Go to make.com (unsafe)*. Es seguro, simplemente Google avisa de apps de terceros sin verificación pública.
   - **IMPORTANTE**: cuando Google muestre los permisos a conceder, **marca todas las casillas**. Si dejas alguna sin marcar, te dará error 403 "insufficient authentication scopes" al usar el módulo.
3. **To**: tu email.
4. **Subject**: `🚨 BOE Sección I - {{formatDate(now; "DD/MM/YYYY")}}`. Para insertar `formatDate(now;...)` usa el panel derecho > pestaña *Date and time*.
5. **Body type**: `Raw HTML` (NO "Collection of contents").
6. **Content**:
   ```html
   <h2>BOE Sección I — {{formatDate(now; "DD/MM/YYYY")}}</h2>
   <ul>
   {{4.text}}
   </ul>
   ```
7. **Save**.

### Paso 9 — Schedule diario

1. Click en el módulo HTTP [1] (el primero).
2. Click en el icono **reloj** debajo del módulo.
3. **Run scenario**: `Every day`. **Time**: `10:00` (BOE publica sobre 07:30-08:30; a las 09-10 ya está estable).
4. **OK**.

### Paso 10 — Activar el escenario

1. Toggle **OFF/ON** abajo a la izquierda del escenario (no del módulo). Cambia de gris a morado.
2. A partir de aquí corre solo.

---

## Lista de IDs `BOE-A-…` para el filtro principal

### Opción A — Regex de UNA SOLA LÍNEA *(recomendada)*

Pega esto tal cual en el campo *Value* del filtro principal cuando elijas operador `Matches pattern`:

```regex
(BOE-A-1978-31229|BOE-A-2015-10565|BOE-A-2015-10566|BOE-A-2015-11719|BOE-A-2020-8950|BOE-A-1986-6859|BOE-A-2015-7682|BOE-A-2010-8115|BOE-A-2000-544|BOE-A-2024-24099|BOE-A-2009-17242|BOE-A-2014-3649|BOE-A-2015-3442|BOE-A-2018-16673|BOE-A-2021-8806|BOE-A-2011-7630|BOE-A-2022-7191|BOE-A-2022-5575|BOE-A-1995-25444|BOE-A-1985-4816|BOE-A-2014-12029|BOE-A-1882-6036|BOE-A-2000-641|BOE-A-1984-11305|BOE-A-2015-4606|BOE-A-2004-21760|BOE-A-2007-6115|BOE-A-2022-14630|BOE-A-2023-5366|BOE-A-1995-24292|BOE-A-1997-1853|BOE-A-2006-1037|BOE-A-2010-1430|BOE-A-1992-28740|BOE-A-2014-12328|BOE-A-2015-11722|BOE-A-2003-23514|BOE-A-2009-19848|BOE-A-1993-6202|DOUE-L-2016-80807)
```

### Opción B — Mapa legible de los IDs

Para saber qué norma corresponde a cada ID cuando llegue el email:

| ID | Norma | Tema(s) |
|---|---|---|
| `BOE-A-1978-31229` | Constitución Española 1978 | T4-7, 43, 52, 55 |
| `BOE-A-2015-10565` | Ley 39/2015 PAC | T10 |
| `BOE-A-2015-10566` | Ley 40/2015 LRJSP | T10-11 |
| `BOE-A-2015-11719` | RDLeg 5/2015 EBEP | T12 |
| `BOE-A-2020-8950` | RD 734/2020 estructura Ministerio Interior | T13 |
| `BOE-A-1986-6859` | LO 2/1986 Fuerzas y Cuerpos de Seguridad | T14 |
| `BOE-A-2015-7682` | LO 9/2015 régimen personal Policía Nacional | T14 |
| `BOE-A-2010-8115` | LO 4/2010 régimen disciplinario CNP | T14 |
| `BOE-A-2000-544` | LO 4/2000 Extranjería | T15-16 |
| `BOE-A-2024-24099` | RD 1155/2024 Reglamento Extranjería | T15-16 |
| `BOE-A-2026-8284` | RD 316/2026 modifica el Reglamento de Extranjería | T15-16 |
| `BOE-A-2009-17242` | Ley 12/2009 Asilo | T17 |
| `BOE-A-2014-3649` | Ley 5/2014 Seguridad Privada | T18 |
| `BOE-A-2015-3442` | LO 4/2015 Seguridad Ciudadana | T19 |
| `DOUE-L-2016-80807` | Reglamento UE 2016/679 RGPD | T20 |
| `BOE-A-2018-16673` | LO 3/2018 LOPDGDD | T20 |
| `BOE-A-2021-8806` | LO 7/2021 datos personales fines penales | T20 |
| `BOE-A-2011-7630` | Ley 8/2011 PIC | T21 |
| `BOE-A-2022-7191` | RD 311/2022 ENS | T21, T77 |
| `BOE-A-2022-5575` | RDL 7/2022 ciberseguridad 5G | T21 |
| `BOE-A-1995-25444` | LO 10/1995 Código Penal | T22-44 |
| `BOE-A-1985-4816` | Ley 4/1985 Extradición Pasiva | T23 |
| `BOE-A-2014-12029` | LO 23/2014 reconocimiento mutuo penal UE | T24 |
| `BOE-A-1882-6036` | LECrim | T45-50 |
| `BOE-A-2000-641` | LO 5/2000 responsabilidad penal menores | T46 |
| `BOE-A-1984-11305` | LO 6/1984 Habeas Corpus | T46 |
| `BOE-A-2015-4606` | Ley 4/2015 Estatuto víctima | T51 |
| `BOE-A-2004-21760` | LO 1/2004 violencia género | T52 |
| `BOE-A-2007-6115` | LO 3/2007 igualdad | T52 |
| `BOE-A-2022-14630` | LO 10/2022 libertad sexual | T52 |
| `BOE-A-2023-5366` | LO 4/2023 LGTBI | T52 |
| `BOE-A-1995-24292` | Ley 31/1995 PRL | T53 |
| `BOE-A-1997-1853` | RD 39/1997 Reglamento Servicios Prevención | T53 |
| `BOE-A-2006-1037` | RD 2/2006 PRL en CNP | T53 |
| `BOE-A-2010-1430` | RD 67/2010 PRL en AGE | T53 |
| `BOE-A-1992-28740` | Ley 37/1992 IVA | T72 |
| `BOE-A-2014-12328` | Ley 27/2014 Impuesto Sociedades | T72 |
| `BOE-A-2015-11722` | RDLeg 6/2015 Tráfico y Seguridad Vial | T78-79 |
| `BOE-A-2003-23514` | RD 1428/2003 Reglamento Circulación | T78-80 |
| `BOE-A-2009-19848` | RD 818/2009 Reglamento Conductores | T78 |
| `BOE-A-1993-6202` | RD 137/1993 Reglamento de Armas | T81 |

**Total: 40 IDs.**

---

## Lista de palabras clave para el filtro "red de seguridad"

### Regex POSITIVO (inclusión) — v2

Pega en el filtro `Solo temario CNP` (campo *Value* con operador `Matches pattern`). Case-insensitive con `(?i)`. Usa `\b` (word boundary) para evitar matches parciales tipo "inseguridad" → "seguridad".

```regex
(?i)\b(cuerpo nacional de polic[ií]a|polic[ií]a nacional|polic[ií]a judicial|fuerzas y cuerpos de seguridad|escala ejecutiva|escala b[áa]sica|ley org[áa]nica|real decreto-ley|seguridad ciudadana|seguridad vial|seguridad privada|seguridad nacional|extranjer[ií]a|menores extranjeros|protecci[óo]n internacional|protecci[óo]n de datos|protecci[óo]n civil|asilo|c[óo]digo penal|enjuiciamiento criminal|infraestructuras cr[ií]ticas|ciberseguridad|esquema nacional de seguridad|NIS2|veh[ií]culo prioritario|violencia de g[ée]nero|libertad sexual|indemnidad sexual|LGTBI|personas trans|riesgos laborales|reglamento de armas|armas de fuego|tr[áa]fico de drogas|tr[áa]fico ilegal|v[ií]ctima del delito|defensor del pueblo|fiscal[ií]a europea|orden europea|reconocimiento mutuo|habeas corpus|trata de seres humanos|tribunal constitucional|derecho de reuni[óo]n|cuerpo policial)\b
```

**Cambios vs v1**:
- Quitado `extranjeros` suelto (matcheaba "inversiones extranjeras" de Hacienda).
- Quitado `tr[áa]fico` suelto (matcheaba tráfico marítimo, ferroviario, etc.). Sustituido por `seguridad vial`, `tr[áa]fico de drogas`, `tr[áa]fico ilegal`.
- Añadido **`ley org[áa]nica`** como sentinel — captura TODA LO nueva aunque no esté en los 40 IDs (toda LO se publica con esta frase en el título BOE).
- Añadido `real decreto-ley` — capta medidas urgentes que reforman penal/extranjería/seguridad.
- Añadido `polic[ií]a judicial`, `escala ejecutiva`, `escala b[áa]sica` (relevantes para convocatorias internas y oposición).
- Añadido `protecci[óo]n civil`, `indemnidad sexual`, `derecho de reuni[óo]n`, `tribunal constitucional`, `cuerpo policial`.

### Regex NEGATIVO (exclusión) — añadir como 2º filtro

Después del filtro positivo, encadena un segundo filtro llamado `Excluir ruido`. Operador: `Does not match pattern`. Field 1: `{{3.title[]}}`.

```regex
(?i)\b(pesca|pesquer[oa]s?|agricultura|agr[ií]cola|ganader[ií]a|alimentari[oa]s?|veterinari[oa]s?|fitosanitari[oa]s?|vinos?|denominaci[óo]n de origen|patrimonio hist[óo]rico|museo|biblioteca p[úu]blica|archivo hist[óo]rico|deportes?|fiestas? local|condecoraci[óo]n|distinci[óo]n honor[ií]fica|medio ambiente|residuos|emisiones|energ[ií]as renovables|hidrocarburos|miner[ií]a|telecomunicaciones|espectro radioel[ée]ctrico|farmac[ée]utic[oa]s?|biom[ée]dic[oa]s?|universidad|formaci[óo]n profesional|becas?|matr[ií]cula|investigaci[óo]n cient[ií]fica|aviaci[óo]n civil|transporte mar[ií]timo|transporte ferroviario|inversi[óo]n extranjera|comercio exterior|aduanas?|tabaco|turismo)\b
```

**Qué bloquea** (ejemplos reales de ruido frecuente):
- "Real Decreto sobre **seguridad alimentaria** en productos de **pesca**" → matchea positivo por "seguridad", pero "pesca" + "alimentaria" lo bloquean.
- "Orden de inversión **extranjera** en sectores estratégicos" → matchea por "extranjer", bloqueado.
- "Orden de **condecoración** al mérito policial" → matchea por "policial", bloqueado (es protocolo, no temario).

**Cuidado con `sanitari[oa]s`**: NO está incluido en exclusión porque matchearía "seguridad sanitaria" en contextos de emergencia (Tema 19). Si ves ruido por farmacia, ajusta a algo más específico como `medicament[oa]s?|productos sanitarios`.

### Estructura final del filtrado en Make

```
Iterator → [Filter 1: Solo temario CNP]  ← regex positivo OR IDs
        → [Filter 2: Excluir ruido]      ← Does NOT match exclusión
        → Text Aggregator
        → [Filter 3: Solo si hay matches] ← {{4.text}} Not equal to ""
        → Gmail
```

---

## Plantilla del email

Esto es lo que está desplegado en los dos escenarios activos. Es mucho más simple que el primer diseño con tags de criticidad y descripciones largas — en la práctica, una lista clickable basta.

### Text Aggregator (módulo 4)

- **Source Module**: Iterator [3]
- **Row separator**: New row
- **Text** (este es el template que se repite por cada item):

```html
<li><a href="{{3.link[]}}">{{3.title[]}}</a></li>
```

Resultado: el aggregator concatena un `<li>...</li>` por cada artículo que pasó el filtro y produce un único bloque de texto HTML.

### Gmail (módulo 5)

- **To**: tu email.
- **Subject**:
  ```
  BOE Sección I — {{formatDate(now; "DD/MM/YYYY")}}
  ```
  (en el escenario `BOE Oposiciones CNP` pon "Sección II.B" en vez de "Sección I").
- **Body type**: `Raw HTML` ← clave. No usar "Collection of contents".
- **Content**:
  ```html
  <h2>BOE Sección I — {{formatDate(now; "DD/MM/YYYY")}}</h2>
  <p>Novedades detectadas que afectan a tu temario CNP:</p>
  <ul>
    {{4.text}}
  </ul>
  <hr>
  <p style="font-size:11px;color:#888;">
    Agente automatizado · Make.com<br>
    Fuente: https://www.boe.es/rss/boe.php?s=1<br>
    Normas vigiladas: <code>documentos/normativa-vigilancia-boe.md</code>
  </p>
  ```
  Donde `4.text` es la salida del Text Aggregator (ajusta el número al ID real del aggregator en tu escenario, mira el círculo del módulo).

### Filtro empty-check entre módulos 4 y 5

Para que NO se envíe email cuando 0 items pasaron el filtro principal:

- **Label**: `Solo si hay matches`
- **Condition**: `{{4.text}}` → `Text operators > Not equal to` → (deja Value vacío)

Sin esto, el aggregator produce 1 bundle con string vacío y Gmail enviaría una lista en blanco cada día.

### Por qué este diseño y no el HTML maquetado anterior

- En móvil un `<ul><li><a>` se lee igual de bien que cualquier diseño con tarjetas y bordes de color.
- Menos campos custom = menos cosas que romper cuando el BOE cambie el feed.
- El filtro previo ya garantiza que TODO lo que llega es relevante — no necesitas distinguir "crítica" vs "revisar" en el email, el cerebro lo hace al leer el título.
- Si en el futuro quieres añadir el `description` del BOE o la fecha de publicación, el template del aggregator pasa a:
  ```html
  <li>
    <a href="{{3.link[]}}">{{3.title[]}}</a><br>
    <small>{{3.pubDate[]}}</small>
  </li>
  ```

---

## Alternativa: vigilar también otras secciones del BOE

Sección II.B (oposiciones) ya está implementada como escenario propio (`BOE Oposiciones CNP`, URL `s=2B`). Próximas a añadir:

### Sección III (recomendada, pendiente)

Aquí salen muchas Órdenes Ministeriales del Interior, instrucciones de la Secretaría de Estado de Seguridad, resoluciones DGP, baremos de pruebas físicas. Muy relevante para CNP.

1. En Make, sobre el escenario `BOE actualizaciones temario`, clic en *...* > **Clone**.
2. Renombra a `BOE Sección III - Otras disposiciones`.
3. Cambia la URL del HTTP por `https://www.boe.es/rss/boe.php?s=3`.
4. Cambia el Subject y el `<h2>` del email a "BOE Sección III".
5. Mantén el mismo regex de palabras clave + IDs (vale para los dos).
6. Schedule daily 10:00, activar.

Coste adicional: ~150 ops/mes. Total con 3 escenarios activos: ~450 ops/mes (de 1000 disponibles).

### Sección IV (opcional)

Administración de Justicia. Bajo volumen, ocasionalmente relevante para temas penales/procesales. Misma fórmula con `s=4`.

### Feeds por materia legislativa (precisión máxima, futuro)

El BOE publica además feeds enfocados por materia, con mucho menos ruido. URLs en https://www.boe.es/rss/. Ejemplos para CNP:

| Materia | URL |
|---|---|
| Derecho Penal | `https://www.boe.es/rss/canal_leg.php?l=l&c=113` |
| Derecho Constitucional | `https://www.boe.es/rss/canal_leg.php?l=l&c=111` |
| Derecho Administrativo | `https://www.boe.es/rss/canal_leg.php?l=l&c=109` |
| Extranjería | `https://www.boe.es/rss/canal_leg.php?l=l&c=135` |
| Seguridad y Defensa | `https://www.boe.es/rss/canal_leg.php?l=l&c=126` |
| Función Pública | `https://www.boe.es/rss/canal_leg.php?l=l&c=116` |
| Transportes y tráfico | `https://www.boe.es/rss/canal_leg.php?l=l&c=132` |

Trade-off: precisión alta pero se pierde lo no etiquetado en una materia concreta. Mejor mantenerlos como **complemento** a las secciones I y III, no como sustituto.

---

## Lecciones aprendidas (errores a no repetir)

> Esta sección documenta los fallos reales que cometimos al montar el agente y cómo se solucionaron. Sirve para no caer dos veces.

### 1. Verifica URLs RSS contra la fuente oficial, no contra memoria ni blogs

**Síntoma**: el HTTP devolvía respuesta vacía o 404 con `https://www.boe.es/rss/canal.php?c=seccion1` y con `https://www.boe.es/rss/seccion/?s=1`.

**Causa**: URLs antiguas / inventadas. El BOE cambió en algún momento la ruta.

**Solución**: la URL correcta es `https://www.boe.es/rss/boe.php?s=1`. Verificada en el catálogo oficial https://www.boe.es/rss/ que lista TODOS los feeds RSS reales del BOE en cada momento.

**Regla**: cualquier URL de API/RSS de un servicio público se valida primero abriéndola en navegador y/o consultando la página índice del propio servicio. Las URLs documentadas en blogs/tutoriales caducan; las del propio proveedor no.

### 2. Headers HTTP: User-Agent y Accept aunque no parezcan obligatorios

Algunos servicios bloquean clientes sin User-Agent identificable o con `Accept: */*` ambiguo. En nuestro caso no fue lo que rompía el flujo (era la URL), pero los headers se quedaron porque no cuestan nada y previenen bloqueos futuros si BOE endurece su política.

### 3. OAuth: marca TODAS las casillas de permisos a la primera

**Síntoma**: módulo Gmail mostraba `[403] Request had insufficient authentication scopes` en campos como Signature content y From.

**Causa**: en la pantalla de Google, durante el OAuth inicial, no se marcaron todas las casillas de permisos.

**Solución**: ir a *Connections* en Make → conexión Gmail → *Reauthorize* → marcar TODOS los checkboxes que Google muestre.

**Regla**: en OAuth, "menos permisos" no es más seguro si la app los necesita — simplemente rompe la funcionalidad. Concede todos los que la app pida y revoca la conexión entera si dejas de usarla (https://myaccount.google.com/permissions).

### 4. Iterator: profundidad del path importa

**Síntoma**: Iterator devolvía 1 bundle inútil con `title: "BOE - Boletín Oficial del Estado"` en vez de N bundles, uno por artículo.

**Causa**: el Array del Iterator apuntaba a `channel[]` (que solo tiene 1 elemento, el canal entero) en vez de `channel[].item[]` (los N artículos dentro).

**Solución**: bajar un nivel más en el árbol XML hasta llegar al array de items reales.

**Regla**: cuando un Iterator saca menos bundles de los esperados, casi siempre es porque el path está un nivel arriba del array que querías recorrer.

### 5. Email a spam la primera vez: normal, no es bug

**Síntoma**: el primer email llegó a Spam.

**Causa**: remitente OAuth de terceros sin reputación previa con la cuenta destino.

**Solución**: marcar "No es spam" + añadir a contactos. A partir del 2º envío va a Inbox.

### 6. Gmail Body type: usar `Raw HTML`, no `Collection of contents`

**Síntoma**: al elegir "Body type: Collection of contents" aparecían campos confusos (Content 1 con Text + Image vacíos) y el email salía mal formateado.

**Solución**: usar **Body type: `Raw HTML`** y meter directamente el HTML completo en Content. Es la opción "te paso ya el HTML maquetado, no lo toques".

### 7. Plain text en email: los saltos de línea se pierden

**Síntoma**: enviando el aggregator como texto plano, todos los items aparecían pegados en una línea muy larga.

**Causa**: Gmail renderiza plain text colapsando saltos de línea simples.

**Solución**: pasar a HTML (`<ul><li>...</li></ul>`) con Body type Raw HTML. Como bonus los links se vuelven clickables.

### 8. Filter empty-check antes del Email

**Síntoma**: cuando 0 items matcheaban el filtro principal, el aggregator producía 1 bundle con texto vacío y el email se enviaba igualmente vacío.

**Solución**: añadir un segundo filtro entre Aggregator y Gmail con condición `text Exists` (o `Not equal to ""`). Si el aggregator está vacío, Gmail no se ejecuta.

**Regla**: un Aggregator SIEMPRE produce 1 bundle (es su naturaleza). Si quieres condicionar el siguiente paso al contenido y no a la presencia, filtra explícitamente.

### 9. Regex en Make: el patrón va en *Value*, no el texto a buscar

**Confusión común**: poner en *Value* la frase a encontrar (por ejemplo el título literal de un BOE) en lugar del patrón regex. Resultado: 0 matches porque el motor busca ese texto literal dentro de cada item.

**Regla**: el patrón regex (la "plantilla") va en *Value* y se queda fijo. Make lo evalúa contra el contenido de *Field 1* en cada bundle. Para validar un regex contra textos de ejemplo: https://regex101.com/ (Flavor: ECMAScript, flags `gmi`).

### 10. Testing con datos sintéticos: aflojar el filtro temporalmente

Para verificar que toda la cadena (HTTP → … → Email) funciona sin esperar a que aparezca un BOE real con matches: cambiar el regex del filtro por `(.*)` (matchea todo) durante una ejecución, comprobar que llega email, restaurar regex bueno.

### 11. Naming: nombres descriptivos desde el principio

Empezamos con `BOE Test 01 - Hola Mundo` y tuvimos que renombrar a `BOE actualizaciones temario` cuando pasó a producción. Si vas a usarlo de verdad, nómbralo de verdad desde el día 1.

---

## Mantenimiento

### Cuándo actualizar la lista de IDs

| Disparador | Acción | Frecuencia esperada |
|---|---|---|
| Recibes un email "🟡 REVISAR" sobre una ley nueva relevante | Añade su ID al regex principal | 2-4 veces al año |
| Una norma vigilada es derogada y sustituida (ej. RD 557/2011 → RD 1155/2024) | Cambia el ID viejo por el nuevo | 0-2 veces hasta examen |
| Cambia la estructura DGP / Ministerio Interior | Actualiza `BOE-A-2020-8950` por el RD nuevo | 0-1 veces hasta examen |

### Cómo actualizar

1. Edita el regex de la sección 5 de este `.md`.
2. Copia el nuevo regex.
3. En Make → escenario → módulo del filtro principal → pega el regex.
4. Save.

> Como la lista vive **aquí** en el repo, mantienes el control de versiones
> con `git`. Make solo es el ejecutor.

### Cuándo apagar el escenario

- **El día después del examen** (oct-2026). Apaga el toggle ON/OFF para
  conservar las operaciones del free tier.

---

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| No llega ningún email en una semana | Ese día no hubo matches (es lo normal) | Mira el "History" del escenario en Make: si las ejecuciones aparecen en verde, todo va bien |
| Llegan emails vacíos | Falta el filtro "length > 0" tras el Aggregator | Revisa Paso 10 |
| Make da error "402 Operations limit reached" | Excediste 1 000 ops/mes | Reduce frecuencia a 1×/día (no 1×/hora). Cuenta: ~75 items × 30 días = 2 250 ops si haces iteración. Solución: filtra **antes** de iterar usando un módulo "Text > Match pattern" sobre el XML crudo |
| El BOE devuelve 503 | Caída temporal del servidor BOE | Make reintenta automáticamente. Si persiste, comprueba https://www.boe.es manualmente |
| Los caracteres con tilde aparecen como `&aacute;` | Encoding del RSS | Añade módulo `Tools > Compose a string` con función `decodeURL()` antes del email |
| El email se va a spam | Primer envío sin reputación previa | Marca "No es spam" + añadir remitente a contactos. A partir del 2º envío va a Inbox |
