# BIT-013 · Fidelidad visual frente a Figma: diferencias de maquetación

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-002](BIT-002-estrategia-de-pruebas.md), [BIT-009](BIT-009-modelo-y-esfuerzo.md), [BIT-011](BIT-011-forge-presentation-semantica.md), [BIT-012](BIT-012-e2e-patrol-dispositivo-y-keys.md)

- **Tipo:** auditoría, mejora · **Estado:** en curso (fase 0 hecha, fase 1 en la rama `feat/bit-013-figma-fidelidad`; ADR [0009](../adr/0009-visual-fidelity-responsive-first.md)) · **Alta:** 2026-11-19
- **Origen:** informe de solo lectura (2026-11-19) sobre diferencias de maquetación entre el diseño
  de Figma y el código generado, en la cadena `forge-figma` → `forge-presentation`. No se tocó
  código. **No es alcance de `forge-presentation`**: nace en cómo se traduce y se verifica el
  diseño. BIT-011 lo deja fuera de su alcance y lo remite a esta entrada.
- **Dónde mirar:** `plugins/flutter-forge/skills/forge-figma/` (`SKILL.md`,
  `references/{figma-mapping,design-template,css-mode,widget-catalog}.md`), `forge-deliver/`,
  `forge-audit/`, `forge-tests/` (`SKILL.md`, `references/{test-matrix,widget-tests}.md`),
  `forge-e2e/`, `forge-presentation/`, `forge-blueprint/`

**Hipótesis de causa raíz**
No hay una **fase de fidelidad visual con criterios y evidencia**, y la traducción a layouts
flexibles **no tiene una tolerancia declarada**. Ninguna skill cierra el ciclo
diseño → código → comparación.

**Hallazgos**
- [ ] **Alta. Las reglas de mapeo descartan medidas a propósito.** `figma-mapping.md` dice
      "Fixed width on a text container → remove; constrain by parent" (línea 13), "Fill container
      → `Expanded`" (línea 11) y "Hug contents → default sizing, no fixed width" (línea 12);
      `SKILL.md:105` repite "Fixed widths from the frame → Flexible layout + padding". Da layouts
      flexibles, pero cambia anchos, alineaciones y proporciones respecto al diseño. Es una decisión
      razonable que **no se declara como tolerancia**: nadie define cuánta diferencia es aceptable.
- [ ] **Alta. Nadie compara el resultado con el diseño.** `forge-deliver` no tiene fase de
      verificación visual; `forge-audit` no revisa fidelidad al diseño; `forge-tests` pide goldens
      "solo para componentes visuales estables" y como complemento (`SKILL.md:66`,
      `test-matrix.md:12-13`); `forge-e2e` no toma capturas comparables.
- [ ] **Alta. El contrato es un esquema, no una especificación.** `design.md` guarda "estructura
      solamente" (pseudocódigo con `spacing: 16`). `forge-presentation` implementa a partir de eso y
      no vuelve a ver el diseño: cualquier tamaño, alineación o jerarquía que no esté en el esquema
      se **infiere**.
- [ ] **Media. La captura de referencia es opcional.** `forge-figma` toma captura solo "when you
      need a visual target for a node you have not seen" (`SKILL.md:36`). No se guarda una captura
      de referencia por pantalla junto a `design.md`, así que tampoco hay contra qué comparar luego.
- [ ] **Media. Tokens ausentes.** Si un token no existe en el tema, se reporta como *gap* y no se
      reemplaza (`SKILL.md:49`, `design-template.md:13-15`). Protege el tema, pero deja el valor del
      diseño sin implementar y el componente queda con el valor por defecto de Material.
- [ ] **Media. Material por defecto frente a diseño personalizado.** El mapeo envía componentes de
      Figma a widgets Material (`FilledButton`, `ListTile`), que traen tamaños y espaciados propios
      que pueden diferir del diseño (p. ej. la restricción de `leading` y `trailing` de `ListTile`,
      ya citada en BIT-011 por los 48×48).

**Qué quiero saber / hacer** (a decidir; sin plan cerrado todavía)
- [ ] Declarar una **tolerancia de fidelidad** (qué se considera diferencia aceptable y cuál es un
      defecto), por tipo de medida: ancho, alineación, espaciado, tipografía, color.
- [ ] Decidir qué parte del diseño pasa de esquema a **especificación** en `design.md` (medidas y
      alineaciones que importan, no solo estructura) sin perder el layout flexible.
- [ ] Guardar una **captura de referencia por pantalla y estado** junto a `design.md`, no solo
      cuando falta un objetivo visual.
- [ ] Definir una **fase de verificación visual** con criterios y evidencia (¿en `forge-deliver`,
      en `forge-audit` o en ambos?) y su coste: medir antes de imponerla.
- [ ] Decidir cómo se cierra el ciclo: capturas comparables en `forge-e2e`, goldens ampliados en
      `forge-tests`, o una comparación guiada por el agente contra la captura de referencia.
- [ ] Política para tokens ausentes: seguir reportando el *gap*, pero dejar constancia visible de
      la diferencia resultante y quién decide (¿extensión del tema propuesta, valor provisional?).
- [ ] Política para widgets Material con medidas propias: cuándo se acepta el valor por defecto,
      cuándo se ajusta con parámetros y cuándo se crea un widget propio.

**Decisiones y criterio de hecho**
- Una tolerancia escrita en una sola fuente de verdad que las demás skills enlazan sin repetir
  umbrales (mismo criterio que BIT-011 y BIT-012).
- Una corrida de `forge-deliver` deja evidencia visual (captura de referencia y de resultado) y
  un veredicto de fidelidad; los *gaps* de tokens y las diferencias aceptadas quedan listados.
- Evals que cubran al menos: mapeo con ancho fijo, token ausente y componente Material con
  medidas distintas. ADR si la tolerancia se vuelve decisión de diseño, y entrada en `CHANGELOG`.

**Dependencias y límites**
- BIT-002 (estrategia de pruebas: goldens y capturas), BIT-012 (comparte con esta entrada la idea
  de "declarar en el blueprint" y la ejecución E2E donde podrían tomarse capturas), BIT-011
  (semántica y `ListTile`; separó esta entrada como fuera de su alcance).
- Los umbrales de tolerancia **no se suponen**: se calibran con diseños y proyectos reales
  (UNITED, `forge_demo`).

**Notas**
- Relación con BIT-011 (2026-11-19): la extracción de semántica desde Figma (etiquetas, orden de
  foco, textos alternativos) en `design-template.md` es **condicional a `a11y: on`**. Esta entrada
  trata la fidelidad visual y no depende de ese interruptor.
- Las referencias a líneas se comprobaron contra el árbol del 2026-11-19; reverificar si los
  archivos cambian antes de actuar.
- La causa raíz es una hipótesis: confirmarla con una comparación real diseño ↔ código de al menos
  una pantalla antes de fijar el plan.

## Fase 0 · Calibración con un caso real (2026-11-19)

**Caso:** UnitedApp, run `simulador-inversion` (plugin 0.7.0, Opus 5.5), Figma `nvBFVP60JHUgTiaJMcqBCK`
nodo `78627:22552` (resultado Control 16) contra el código de `lib/screens/investment_simulator/` en el
commit `84e1467` (worktree `UnitedApp-bit013`, rama `feat/bit-013-calibracion-figma`). Medidas leídas con
`get_design_context` y `get_metadata`; comparación estática más una sonda de layout desechable (no se
versiona) que renderiza el resultado a 6 tamaños × 3 escalas de texto × 3 variantes.

**Resultado sobre la hipótesis:** se confirma, con dos matices.
1. La pérdida de fidelidad ocurre en **dos capas**, no solo en `forge-figma`: `design.md` aplanó o
   calló medidas (separación de las filas, color por texto, borde de la nota) y `forge-presentation`
   además aplanó columnas anidadas que `design.md` sí describía bien (ver A).
2. La **responsividad es el defecto mayor** y nadie lo mide: 23 de 54 combinaciones tienen overflow.

| # | Tipo | Diseño | Código | Veredicto propuesto | Origen |
|---|---|---|---|---|---|
| A | espaciado | importe → barra de niveles: 24 (columna anidada) | 16 (columna plana + `SizedBox(8)` en otro punto) | defecto | presentation (`design.md` lo tenía bien) |
| B | espaciado | filas del resumen: 8 entre ellas | 16 | defecto | `design.md` calla |
| C | espaciado | divisor ↔ flecha: 4 | 0 | defecto menor | `design.md` calla |
| D | alineación/espaciado | importe y divisa: 8, alineados abajo | 4, centrados (`AmountInput` compartido) | defecto | `design.md` calla |
| E | color | "Ganarías" y su importe: `On Primary Container` | `onSurfaceVariant` y `primary` | defecto | `design.md` calla (color por texto) |
| F | tipografía (rol) | etiqueta 12 (`body/small`), valor 16 (`title/medium`) | `bodyMedium` 14, `titleSmall` 14 | defecto | `design.md` calla |
| G | borde | nota con borde 1 px al 16 % | `hasBorder: false` | defecto | `design.md` calla |
| H | color (valor) | `State Layers/Primary/Opacity-16` = `#8D4E2A` al 16 % | `primary` (`#FF7E2B`) al 16 % | **decisión**: equivalencia por nombre con valor distinto; se resolvió "por convención" sin avisar | `design.md` (D-1 mal descrito) |
| I | color | divisores: variable `Outline Variant` `#D7C2B9` presente en el nodo | `primary` al 16 % | probable defecto; verificar | `design.md` no lo cita |
| J | fuente | `title/*` y `label large` en Montserrat | `DMSans` (Montserrat no está en `assets/fonts`) | **gap global** (hoy solo una "Observación") | tema del proyecto |
| K | tamaño | selector de divisa 34 px de alto | caja de 48 px (área táctil) | decisión (no es `a11y`) | presentation |
| L | espaciado | barra → etiqueta: 12 (marco de 12 con pista de 4) | 8 | aceptable (≤4 px) | — |
| M | alineación | etiquetas con `space-between` | centradas por tramo (≤5 px) | aceptable por flexibilidad | — |
| N | ancho | nota 326, tarjeta `min-w 300`, subrayado 268 | estiran; la tarjeta no impone 300; subrayado fijo 268 | aceptable (gana la responsividad); el subrayado fijo no se adapta | — |

**Responsividad (sonda, 54 combinaciones: 31 correctas, 23 con overflow).**
- Con importes grandes y escala 1.0: overflow a 320 dp (54 px) y 360 dp (14 px).
- Teléfonos (12 combinaciones por escala): fallan 2 con escala 1.0, 9 con 1.5 y 12 con 2.0. Tablet y
  horizontal no fallan en ninguna.
- Los dos puntos son `simulation_result_card.dart:30` (fila título/importe) y `:89` (`_ResultRow`):
  un `Text` sin `Flexible` junto a un `Expanded`. Es el patrón que `check_responsive.py` debe marcar.
- `design.md` no declara ningún comportamiento responsivo, y el diseño en sí (`min-w 300`) no cabe en 320 dp.

**Implicaciones para el plan**
- `design.md` debe fijar **espaciado entre hermanos, color y rol tipográfico por elemento**, y conservar
  la jerarquía de columnas anidadas; `forge-presentation` no debe aplanarlas (A).
- Las equivalencias de token se declaran con **valor** y con quién decide (H); `theme_tokens.py` compara
  el valor, no solo el nombre.
- Una diferencia de familia tipográfica es un gap de diseño con decisión, no una observación (J).
- La matriz responsiva (tamaños × escala de texto × importe largo) detecta lo que ninguna skill ve hoy.

**Control de modelo (2026-11-19).** Subagente Sonnet 5.5 sin acceso al run ni a la pantalla existente, mismo nodo
(`78627:22552`), 5 llamadas de Figma, siguiendo `forge-figma` tal cual. **Limitación:** mi prompt le pidió medidas
por elemento, color por texto y gaps anidados sin aplanar; la skill hoy no lo pide, así que no es un control
neutro. Una sola corrida, un solo nodo, sin estados.
- Su `design.md` recoge **todas** las diferencias A a G que el de Opus callaba: gaps anidados (24 / 8 / 4),
  separación de filas 8, importe y divisa a 8 alineados abajo, `On Primary Container` en "Ganarías", roles
  `bodySmall`/`titleMedium` en las filas, borde de la nota, y marca H (valor de la capa de estado) y J (Montserrat)
  como gaps con decisión. Solo dudó en colores de vectores (los marcó `[por confirmar]`).
- Conclusión provisional: **en la fase de diseño el modelo no explica la diferencia**; la omisión de Opus nace de
  que el contrato de `design.md` no exige esas medidas. Con el contrato explícito, Sonnet entrega la
  especificación completa. Las discrepancias vistas en otras sesiones de Sonnet quedan sin explicar y apuntan a
  la fase de `forge-presentation` (aplanar columnas, ignorar medidas), que **no se repitió** aquí.
- Si tras la fase 1 la presentación con Sonnet sigue divergiendo con la misma especificación, se deriva a BIT-009
  con esa evidencia. Hasta entonces BIT-009 no cambia.

## Fase 1 · `forge-figma` (2026-11-19, rama `feat/bit-013-figma-fidelidad`)

**Hecho:** `references/fidelity.md` (prioridad, tolerancia inicial, políticas, veredicto, capturas) y
`references/modes.md` (feature, standalone, delta, verify, css; con o sin HU; con o sin `forge-deliver`);
`SKILL.md` reescrito y con `description` más corta; `design-template.md` como especificación (valor del
token, gaps con valor / más cercano / diferencia / quién decide, medidas por elemento, comportamiento
responsivo, referencias, veredicto); `figma-mapping.md` y `css-mode.md` sin "quitar anchos" y con gaps
anidados; claves opcionales `design.screenshots` y `design.fidelity.*` en `profile-schema.md`;
`scripts/theme_tokens.py` y `scripts/lint_design.py` con 16 tests (112 en total); 5 evals; ADR 0009 y
`CHANGELOG`. BIT-009 enlazada en ambos sentidos.

**Evals** (`claude plugin eval`, con y sin plugin, 1 corrida por brazo salvo donde se indica; indicio, no medida
estable; coste total ≈ 4,0 USD con las tres rondas):
- Primera ronda: 0/5 en ambos brazos. Las respuestas eran buenas; fallaron mis criterios (exigían artefactos
  propios de la skill) y la skill no se invocaba. Corregido: criterios de tres puntos de comportamiento,
  prompts que nombran `forge-figma` y un grader `skill-used` por caso.
- Segunda ronda con el plugin: `figma-standalone-delta` pasa (sin plugin: 0), `figma-material-component-measures`
  y `figma-missing-token-gap` pasan (sin plugin también pasan), `figma-responsive-priority` pasa en criterios
  (sin plugin también; la skill no se invocó) y `figma-fixed-width-mapping` falló por un criterio incoherente con
  el prompt (la paleta no traía `onPrimaryContainer`). Corregido y repetido 2 veces: con plugin 2/2, sin plugin 0/2.
- **Lectura honesta:** discriminan bien `standalone-delta` y `fixed-width-mapping`; los otros tres los resuelve
  también el modelo sin plugin, así que miden poco. `responsive-priority` no dispara la skill. Pendiente:
  endurecerlos con casos que dependan de las reglas propias (veredicto, tabla de gaps con quién decide) y
  repetir con más corridas.

**Pendiente de la fase 1:** ninguna capacidad nueva. La verificación con Figma MCP real de los modos
standalone y delta (corrida completa sobre la pantalla UNITED) queda para después de la fase 2, cuando
`forge-presentation` pueda aplicar un `delta.md`.

## Fase 2 · Consumidores (2026-11-19, misma rama; ADR [0010](../adr/0010-responsive-matrix-independent-of-a11y.md))

**Hecho:**
- `forge-presentation`: `references/responsive.md` (única fuente: objetivos, reglas, cómo construir desde las
  Medidas sin aplanar gaps); `SKILL.md`, `page-patterns.md` y `accessibility.md` solo enlazan.
- `forge-tests`: matriz responsiva siempre activa (`widget-tests.md`, helper `pumpAppAt` en `helpers.md`,
  `test-matrix.md`, `SKILL.md`). **Enmienda a ADR 0008:** la prueba de texto grande deja de depender de `a11y`.
- `forge-audit`: `scripts/check_responsive.py` (8 pruebas), checklist § 15, mapa de severidades, `flutter-reviewer`
  y un paso en CI. `forge_demo` salió marcado por la regla (saldo sin `Flexible` junto a un `Expanded`) y se corrigió.
- `forge-deliver`: verificación visual al cierre de la fase de presentación si hay `design.md`, bloque
  `design` opcional en `state.json` y `result.json`, plantilla de informe. Sin fase nueva (las métricas no cambian).
- `forge-blueprint` y `forge-requirements`: una línea cada uno.

**Calibración del script en UNITED (solo lectura):** 276 archivos, 50 hallazgos (18 `row-text-no-flex`, 18
`fixed-height-text`, 7 `row-texts-no-flex`, 4 `media-query-of`, 3 `fixed-width`); marca las dos filas que
desbordaban en la pantalla del simulador. Falsos positivos probables: etiquetas cortas junto a un `Flexible`
(p. ej. el código de divisa de `AmountInput`). En `adopt`/`improve` todo es `warn`.

**Evals de la fase 2** (2 corridas por brazo): `presentation-responsive-layout` 2/2 con plugin y 0/2 sin él;
`audit-responsive-overflow` 2/2 con plugin y 0/2 sin él. Siguen siendo indicio, no medida estable.

**Coordinación con otras BIT:** BIT-002 no debe reintroducir la prueba de texto grande como condicional a `a11y`
(nota añadida allí); BIT-012 no se ve afectada (las keys siguen independientes). Los hooks del plugin no se
entregan (ADR 0009).

**Pendiente:** prueba de extremo a extremo con Figma real (standalone y delta) sobre UNITED, y repetir la
presentación con Sonnet para decidir si BIT-009 recibe evidencia; umbral de `fixed-height-text` por afinar con
más proyectos; fase 3 (goldens y capturas en E2E) sigue condicionada a datos.

## Prueba con Figma real (2026-11-19, tras la fase 2)

Un agente Sonnet ejecutó `forge-figma` en modo **standalone** y luego **delta** sobre la pantalla del simulador
(nodos `78627:22552` resultado y `80362:35721` cargando), sin HU ni `forge-deliver`, escribiendo solo en
`.flutter-forge/design/simulador-resultado/` del worktree. 10 llamadas al MCP (1 guía, 1 variables, 2 metadata,
2 contexto de diseño —pantalla completa y solo el nodo que cambia—, 3 capturas, una redundante), ≈ 3,5 minutos,
`lint_design.py` sin errores.

**Resultado:** `delta.md` encontró 13 defectos y 3 decisiones y recuperó todas las diferencias de la fase 0
(A a J: gap 24 aplanado, color de "Ganarías" e importe, roles de las filas, borde de la nota, capa de estado
`#8D4E2A`, Montserrat) y añadió cinco que yo no había visto: la relación de alineación de las etiquetas de nivel
(`space-between` frente a centradas), el espacio título↔subtítulo de la nota (0 frente a 4), el subrayado fijo de
268, el color probable de divisores y subrayado, y las dos filas sin `Flexible` (`check_responsive.py` coincide).
El estado cargando salió `pass-with-accepted`. Corrección a la tabla de la fase 0: la fila M (alineación) pasa de
"aceptable" a **defecto**, porque la tolerancia de 8 dp solo vale cuando la relación es la misma.

**Fricciones registradas y corregidas** (14 puntos del informe del agente):
- Tamaño de captura (el MCP devuelve el marco con margen: 410×864 para un 390×844): se documenta, no se recorta.
- `theme_tokens.py` daba `DM Sans` como faltante frente a `DMSans`: ahora normaliza (test); solo se pasan al script
  las familias de los nodos en alcance (nunca las del chrome, como Roboto).
- Color de vectores sin token (divisor, subrayado, track): `fidelity.md` § 8 (variable del nodo → muestreo de la
  captura con alpha → `[por confirmar]`); columna *Source* en Medidas.
- Tokens que solo aparecen en otro estado: se leen del contexto de ese nodo, sin repetir variables.
- Empate o coincidencia solo por valor (`On Primary` = `white`): gap *aliased*, lo decide el agente, no bloquea.
- Familia distinta con mismo tamaño y peso: nunca `pass`, es gap. Rol parcheado con `copyWith(fontSize:)`: gap de rol
  faltante si no existe rol, defecto si existe.
- La palabra "gap" se usaba para dos cosas: la columna de Medidas ahora se llama *Spacing*.
- Dónde va el veredicto en modo delta (`delta.md`), estados que comparten layout (columna *Shares layout with*,
  defectos heredados una vez), columnas *Weight* y *Evidence* en la tabla delta, catálogo en solo lectura (filas
  propuestas bajo Components).
- `lint_design.py`: cuenta `[inferido: motivo]` y la celda `inferido`; el aviso de hex fuera de Tokens se documentó.
- Los scripts no eran ejecutables y `SKILL.md` los invocaba sin `python3`: ahora `chmod +x` y `python3 scripts/…`.

**Pendiente:** repetir la presentación (no solo el diseño) con Sonnet aplicando ese `delta.md` para decidir si
BIT-009 recibe evidencia; cerrar la fase de decisión de umbrales con más proyectos.
