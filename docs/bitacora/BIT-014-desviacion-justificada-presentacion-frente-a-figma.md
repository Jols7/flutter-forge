# BIT-014 · Desviación justificada del código de presentación frente al diseño

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-002](BIT-002-estrategia-de-pruebas.md), [BIT-012](BIT-012-e2e-patrol-dispositivo-y-keys.md), [BIT-013](BIT-013-fidelidad-visual-frente-a-figma.md)

- **Tipo:** mejora · **Estado:** pendiente · **Prioridad:** baja · **Alta:** 2026-11-19
- **Origen:** pregunta posterior al cierre de la revisión de `forge-figma` (BIT-013), 2026-11-19: ¿cuándo puede el
  código de presentación apartarse de la estructura del diseño para ser más claro, ordenado y escalable (por
  ejemplo, la distribución de `Column` y `Row` en listas)? Análisis de solo lectura; no se cambió nada.
- **Por qué prioridad baja:** la implementación actual de `forge-figma` y `forge-presentation` es útil
  (en la pantalla de UNITED encontró 13 defectos y 3 decisiones; tras aplicarlos, el overflow bajó de 23 a 0 de 54
  combinaciones), funcional (122 pruebas, evals que discriminan con y sin plugin, corrida real con Figma) y segura
  en la dirección conservadora: **el riesgo medido fue de falta de fidelidad, no de exceso de estructura**. Abrir
  la puerta a desvíos sin datos podría reintroducir el defecto que BIT-013 corrigió.
- **Dónde mirar:** `plugins/flutter-forge/skills/forge-presentation/` (`SKILL.md`, `references/{responsive,structure}.md`),
  `forge-figma/references/{fidelity,design-template,modes}.md`, `forge-blueprint/`, `forge-audit/`

**Estado actual (verificado 2026-11-19)**
- **No existe una convención de desviación por claridad.** Lo más cercano: `structure.md` § *Extract and promote*
  (cuándo extraer un widget), el reuse ladder (qué widget), y las diferencias aceptadas de `fidelity.md` § 1 y 6,
  que solo cubren lo forzado por **responsividad** o tolerancia.
- **La regla vigente va en sentido contrario:** "nunca aplanar columnas anidadas" (`responsive.md`,
  `forge-presentation/SKILL.md`, `design-template.md`, `modes.md`). Nació del defecto A de UNITED (gap 40 en vez
  de 24), que era un **valor** equivocado, no la forma del árbol. La invariante correcta es "se cumplen los valores
  de la tabla de Medidas", no "el árbol se parece al de Figma".

**Propuesta (a decidir; no se implementa todavía)**
- [ ] **Sin skill nueva ni regla abierta.** `forge-figma` dice qué se ve; `forge-presentation` dice cómo se compone.
- [ ] Un **catálogo cerrado** de transformaciones que no cambian el resultado visual, en `forge-presentation`:
      - *siempre, con registro:* hermanos repetidos → bucle, `ListView.builder` o `separated`; `SizedBox` → `spacing:`;
        contenedores del mismo eje con el mismo gap y sin decoración → fusionados; frame de Figma que solo agrupa
        (sin padding, relleno ni efecto, mismo gap que su padre) → eliminado; bloque repetido → widget extraído;
        medida repetida 3 o más veces → tema o widget compartido; optimizaciones sin efecto visible (`const`, carga perezosa);
      - *con registro y comprobación:* separadores como `separatorBuilder`; `Stack` → `Row`/`Column`; widget Material
        por defecto dentro de tolerancia;
      - *nunca:* colores, roles tipográficos, radio, borde, orden, relación de alineación.
- [ ] Reformular "nunca aplanar" como **"nunca cambiar valores"**, sin abrir desvíos libres.
- [ ] Registro: columna *Tipo* (tolerancia, responsivo, estructura) en las diferencias aceptadas de `design.md`,
      para que verify y delta no marquen como defecto un desvío legítimo.
- [ ] Declarar los desvíos previstos en el **blueprint** (Gate 2, con aprobación humana), y que `forge-figma` marque
      en el layout los elementos repetidos como "×N, dato".
- [ ] **Verificación por geometría**, no por forma del árbol: un test que mida distancias entre elementos con claves
      contra las Medidas. Depende de las keys de BIT-012. Hasta que exista, mantener el catálogo mínimo.
- [ ] Orden de prioridades para "eficiente": contrato visual → responsividad → convención del proyecto (en
      `adopt`/`improve` gana la feature canónica) → claridad → coste de ejecución.

**Riesgos**
- Un agente que aplana mal (caso A) y que justifica con texto barato; Sonnet y Opus pueden ser desiguales.
- Verificar equivalencia exige renderizar y medir; sin eso, delta y la verificación estática dan falsos defectos o
  dejan pasar los malos.
- Se pierde la trazabilidad nodo → widget en las actualizaciones de diseño (valorar un mapa estilo Code Connect).
- Cuatro textos hoy dicen "nunca aplanar": reescribirlos a medias deja reglas contradictorias.
- Una referencia más que cargar en cada corrida.

**Puntos ciegos a tener en cuenta**
- Los ejemplos de Figma no son datos: una lista suele mostrar 3 filas con contenido o estado distinto; un bucle
  pierde esas variaciones. Faltan también los estados vacío y de un solo elemento.
- Bordes de lista (margen entre ítems frente al padding del primero y el último; divisores de ancho completo o con sangría).
- Con 3 a 10 ítems estáticos una `Column` es más clara que un `builder`: el catálogo necesita un umbral.
- En la pantalla de UNITED casi todo lo repetido ya era un bucle: el beneficio medido es modesto.

**Cuándo subir la prioridad (disparadores)**
- Dos o más casos reales donde un agente propone desviarse y no hay norma, o donde un `delta.md` marca como defecto
  un desvío razonable.
- La sonda de geometría o las keys de BIT-012 ya existen.
- La calibración con más proyectos (ver BIT-013, protocolo de calibración) muestra listas con envoltorios o
  repeticiones que el código hoy no resuelve bien.

**Decisiones y criterio de hecho**
- Catálogo y reformulación escritos una sola vez en `forge-presentation`, enlazados desde `forge-figma` sin repetir
  reglas; un eval que muestre que acepta una fusión válida (lista → builder) y rechaza un aplanado que cambia un
  valor; el modo delta no marca como defecto lo registrado como estructura. ADR si se vuelve decisión de diseño, y
  entrada en `CHANGELOG`.
- **Antes de implementar, medir:** un caso con una lista y envoltorios anidados con ambos modelos, contando los
  desvíos propuestos, los correctos y los que rompen valores.

**Dependencias y límites**
- BIT-013 (cierra primero; esta entrada parte de su fidelidad y de la regla "nunca aplanar"), BIT-012 (keys y
  `builder` para listas; geometría), BIT-002 (pruebas de geometría y goldens). No afecta a BIT-009 ni a BIT-010.

**Notas**
- El análisis completo es una conversación del 2026-11-19; las cifras de UNITED están en BIT-013 (fase 0 y pruebas
  posteriores). Nada de esto está probado: es una propuesta.
