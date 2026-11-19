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
