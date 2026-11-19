# BIT-011 · `forge-presentation`: semántica y accesibilidad, comentarios y estructura de código

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-001](BIT-001-l10n-localizacion.md), [BIT-002](BIT-002-estrategia-de-pruebas.md), [BIT-004](BIT-004-skills-forge-health-y-upgrade.md), [BIT-009](BIT-009-modelo-y-esfuerzo.md), [BIT-010](BIT-010-linea-base-forge-metrics.md), [BIT-012](BIT-012-e2e-patrol-dispositivo-y-keys.md)

- **Tipo:** auditoría, mejora · **Estado:** pendiente · **Alta:** 2026-11-19
- **Origen:** auditoría de solo lectura de `forge-presentation` (2026-11-19), contrastada con la
  documentación de Flutter (accesibilidad, `flutter_test` guidelines, `SemanticsService`), WCAG 2.2
  (SC 2.5.8 y 1.4.4), *Effective Dart* y el *Flutter style guide*. No se modificó código.
  Las citas de *Effective Dart* y del style guide se hicieron de memoria: verificarlas en la fase 0.
- **Dónde mirar:** `plugins/flutter-forge/skills/forge-presentation/` (`SKILL.md`,
  `references/page-patterns.md`), `forge-architecture/references/{conventions,code-comments}.md`,
  `forge-audit/` (`references/checklist.md` §3, §10 y §14; `scripts/check_comments.py`),
  `forge-tests/references/widget-tests.md`, `forge-figma/references/design-template.md`,
  `forge-requirements/references/hu-template.md`, `forge-blueprint/references/blueprint-template.md`,
  `example/forge_demo/` (`transaction_tile.dart` y su test)

**Estado actual**
- La skill tiene una buena estructura (carga selectiva de referencias por gestor de estado), pero
  **no tiene scripts ni evals**; la `description` mide ~1 000 caracteres y mezcla alcance y triggers.
- **Política de Semantics actual:** una lista de 6 viñetas en `page-patterns.md` § Accessibility
  (tooltip o `Semantics(label:)` en botones solo con ícono, targets de 48×48, texto a 2.0, estado
  no solo por color, `ExcludeSemantics`/`MergeSemantics`, error junto al campo). Es declarativa,
  reactiva y manual; la verificación real es un smoke test opcional y la pregunta §10 del checklist.
- **Comentarios:** `code-comments.md` + `check_comments.py` son coherentes entre sí, pero sin fuente
  oficial citada y con `///` exigido solo en `domain/`.
- **Distribución:** capas bien definidas (`conventions.md` §1 a §8, `check_layers.py`); la única
  métrica interna de pantalla es `quality.max_build_lines` (120).

**Hallazgos**

*A. Semántica y accesibilidad*
- [ ] **Alta.** "Checked by forge-audit" no se cumple: no hay script de accesibilidad; solo la
      pregunta manual §10.
- [ ] **Alta.** `forge-tests/references/widget-tests.md:68` recomienda `meetsGuideline(...)` sin
      `tester.ensureSemantics()`: sin semántica activa las guías no miden nada. El ejemplo
      `forge_demo` sí la usa (`transactions_page_test.dart:85`).
- [ ] **Alta.** La accesibilidad no se pide aguas arriba: `hu-template.md` solo la cita como ejemplo
      de NFR; `forge-figma` no extrae etiquetas, orden de foco ni textos alternativos; el blueprint
      no tiene columna de semántica.
- [ ] **Media.** Cobertura incompleta: encabezados (`header`), orden de lectura (`sortKey`),
      etiquetas de campos y de estados de carga (`semanticsLabel`), anuncios asíncronos
      (`liveRegion`, `SemanticsService.announce` y `MediaQueryData.supportsAnnounce`; la API cambió
      y Android desaconseja los anuncios), lectura localizada de importes y fechas.
- [ ] **Media.** Falta `iOSTapTargetGuideline` (44 pt) junto a `androidTapTargetGuideline` (48 dp);
      WCAG 2.2 pide 24×24 como mínimo AA y 200 % de texto. La skill no cita ninguna fuente.
- [ ] **Media.** Choque no documentado: las restricciones de tamaño de `leading`/`trailing` en
      `ListTile` frente a los 48×48.
- [ ] **Media.** El ejemplo no cumple la política: `transaction_tile.dart` tiene `semanticLabel: null`,
      no excluye ni etiqueta el ícono, no usa `MergeSemantics` y el test solo cubre el estado de fallo.
- [ ] **Media.** El smoke test de texto grande solo detecta excepciones de overflow, no contenido
      truncado.
- [ ] **Media.** Cuatro skills hablan de accesibilidad (`presentation`, `audit`, `tests`, `figma`)
      sin una fuente de verdad: umbrales repetidos con riesgo de divergir.
- [ ] **Baja.** `ValidationFailure.serverMessage` se muestra tal cual: puede ser texto sin localizar
      ni pensado para lector de pantalla; depende de una regla del contrato que `forge-data-layer`
      no impone.

*B. Comentarios y documentación*
- [ ] **Alta.** La política no cita *Effective Dart* (Documentation) ni el *Flutter style guide*;
      coincide en espíritu pero no es auditable ni defendible.
- [ ] **Media.** `check_comments.py` exige `///` solo en `domain/`; los widgets compartidos lo piden
      en `forge-presentation` pero nadie lo verifica (valorar el lint `public_member_api_docs`).
- [ ] **Media.** Sin criterio de redacción del `///` (resumen de una frase, línea en blanco, detalle;
      `[Referencia]`, `{@template}`, ejemplos) ni ejemplos buenos y malos por capa.
- [ ] **Baja.** El idioma fijo (inglés) no tiene su razón registrada; si se mantiene, una ADR corta.

*C. Nomenclatura y distribución dentro de presentación*
- [ ] **Media.** `conventions.md` §8 no cubre nombres de páginas (`XPage`), widgets (`XTile`, `XCard`,
      `XSection`) ni archivos (`snake_case`, lint `file_names`).
- [ ] **Media.** Solo se limita `build`: no hay umbral por archivo, por anidamiento de widgets ni por
      clases por archivo. Una página de 600 líneas con widgets privados puede cumplir y seguir
      siendo ilegible.
- [ ] **Media.** Sin criterio de extracción ni de promoción de widget local a compartido (p. ej.
      "al usarlo una segunda feature"); hoy depende de lo que diga `design.md`.
- [ ] **Media.** Sin esqueleto recomendado de `pages/`, `widgets/`, `state/` ni regla para
      subcarpetas y secciones de pantallas largas.
- [ ] **Baja.** `TransactionsFailure` (estado) frente a `Failure<T>` (resultado) se confunde al leer.
- [ ] **Media.** `check_layers.py` solo valida importaciones; nada comprueba nombres, tamaño de
      archivo ni anidamiento.

*D. Evals*
- [ ] **Alta.** No hay ningún eval de `forge-presentation` (tampoco de `forge-tests`,
      `forge-data-layer` ni `forge-e2e`). Sin eval no cuenta como capacidad (criterio de BIT-004).

**Plan de implementación**

*Fase 0 · Decisiones y fuentes (bajo)*
- [ ] Verificar y fijar las fuentes: guía de accesibilidad de Flutter, `flutter_test` guidelines,
      WCAG 2.2 (2.5.8, 1.4.4), guías de tap target de Android e iOS, *Effective Dart* y style guide.
- [ ] Decidir la política de Semantics (obligatorio, recomendado, delegado) con **una sola fuente de
      verdad**; las demás skills la enlazan sin repetir umbrales.
- [ ] ADR corto: fuentes adoptadas, idioma de comentarios y alcance de `///`.

*Fase 1 · Contenido de `forge-presentation` (bajo a medio)*
- [ ] Crear `references/accessibility.md`: encabezados, orden de lectura, campos y formularios,
      estados de carga, anuncios con la API vigente (consultando `supportsAnnounce`), importes y
      fechas, y la nota de `ListTile`. Reducir `page-patterns.md` § Accessibility a un enlace.
- [ ] Añadir una referencia de estructura: nombres de página, widget y archivo; esqueleto de
      carpetas; criterios de extracción y de promoción a compartido; umbrales de tamaño por archivo
      y anidamiento (**valores a medir en proyectos reales, no a suponer**).
- [ ] Reescribir la `description` más corta, separando alcance y triggers.
- [ ] Plantilla de Riverpod 2.x en lugar de la nota en prosa.

*Fase 2 · Documentación y comentarios (medio)*
- [ ] Citar las fuentes oficiales en `code-comments.md` y añadir la guía de redacción de `///` con
      ejemplos buenos y malos por capa.
- [ ] Extender `check_comments.py`: `///` en widgets compartidos y contratos públicos (opción para
      activar `public_member_api_docs`); mantener el modo `--changed-from` de adopt.

*Fase 3 · Pruebas y auditoría (medio; toca otras skills, coordinar con BIT-002)*
- [ ] `widget-tests.md`: `ensureSemantics()` obligatorio, añadir `iOSTapTargetGuideline`, y una
      prueba de texto grande que compruebe contenido visible, no solo "sin excepción".
- [ ] Añadir un NFR de accesibilidad por defecto a `hu-template.md`, una sección de semántica a
      `design-template.md` y una columna al `blueprint-template.md`.
- [ ] Evaluar `check_a11y.py` en `forge-audit` (`IconButton` sin `tooltip`, `Icon` sin etiqueta,
      `Image` sin `semanticLabel`/`excludeFromSemantics`) y un chequeo de nombres y tamaños;
      decidirlo con datos de falsos positivos.

*Fase 4 · Evals y ejemplo (medio)*
- [ ] Evals: `presentation-sealed-state-and-disposal`, `presentation-a11y-semantics` y
      `presentation-naming-and-structure`, con el formato de los existentes.
- [ ] Corregir `forge_demo` (`transaction_tile.dart`) para que cumpla la política y ampliar su test
      a la lista cargada. Es un cambio de código: va como paso aparte.

**Criterio de cierre** (el de BIT-004): una referencia única de accesibilidad, tests que miden
semántica de verdad, evals pasando, una ADR y entrada en `CHANGELOG`.

**Dependencias y límites**
- BIT-001 (las etiquetas semánticas son texto localizable), BIT-002 (estrategia de pruebas, y
  coordinar la fase 3 sobre `forge-tests`), BIT-009 (modelo y esfuerzo). No interfiere con BIT-010.
- **Fuera de alcance:** las diferencias de maquetación frente a Figma se trazan en otra entrada
  (`forge-figma`, `forge-deliver`, `forge-audit`, `forge-tests`). Aquí solo se toca la parte de
  `forge-presentation` que no dependa de ella.

**Notas**
- Medir antes de fijar umbrales: tamaño de archivo, anidamiento y `max_build_lines` se calibran con
  los proyectos reales (UNITED, `forge_demo`) para no inventar números.
