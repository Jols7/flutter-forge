# BIT-013 · Fidelidad visual frente a Figma: diferencias de maquetación

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-002](BIT-002-estrategia-de-pruebas.md), [BIT-011](BIT-011-forge-presentation-semantica.md), [BIT-012](BIT-012-e2e-patrol-dispositivo-y-keys.md)

- **Tipo:** auditoría, mejora · **Estado:** pendiente · **Alta:** 2026-11-19
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
