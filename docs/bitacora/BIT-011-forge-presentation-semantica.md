# BIT-011 · `forge-presentation`: semántica y accesibilidad (opt-in), comentarios y estructura de código

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-001](BIT-001-l10n-localizacion.md), [BIT-002](BIT-002-estrategia-de-pruebas.md), [BIT-004](BIT-004-skills-forge-health-y-upgrade.md), [BIT-009](BIT-009-modelo-y-esfuerzo.md), [BIT-010](BIT-010-linea-base-forge-metrics.md), [BIT-012](BIT-012-e2e-patrol-dispositivo-y-keys.md), [BIT-013](BIT-013-fidelidad-visual-frente-a-figma.md)

- **Tipo:** auditoría, mejora · **Estado:** hecho (cerrada 2026-11-19; rama `feat/bit-011-presentation-a11y-optin`; ADR [0008](../adr/0008-accessibility-opt-in.md); `CHANGELOG` Unreleased) · **Alta:** 2026-11-19
- **Origen:** auditoría de solo lectura de `forge-presentation` (2026-11-19), contrastada con la
  documentación de Flutter (accesibilidad, `flutter_test` guidelines, `SemanticsService`), WCAG 2.2
  (SC 2.5.8 y 1.4.4), *Effective Dart* y el *Flutter style guide*. No se modificó código.
  Las citas de *Effective Dart* y del style guide se hicieron de memoria: verificarlas en la fase 0.
- **Dónde mirar:** `plugins/flutter-forge/skills/forge-presentation/` (`SKILL.md`,
  `references/page-patterns.md`), `forge-architecture/references/{conventions,code-comments}.md`,
  `forge-audit/` (`references/checklist.md` §3, §10 y §14; `scripts/check_comments.py`),
  `forge-tests/references/widget-tests.md`, `forge-figma/references/design-template.md`,
  `forge-requirements/references/hu-template.md`, `forge-blueprint/references/blueprint-template.md`,
  `forge-profile/references/profile-schema.md`, `example/forge_demo/` (`transaction_tile.dart`)

## Decisión de política (2026-11-19): la semántica es opt-in

La intención es **no trabajar accesibilidad por ahora y dejar lista la estructura** para
implementarla bien más adelante. Por eso se invierte el modelo actual (semántica siempre exigida):

- **Interruptor `a11y: off | on`.** Lo fija `forge-requirements` en el brief a partir de la HU o de
  los requisitos y `forge-deliver` lo propaga a blueprint, presentation, tests y audit.
  Si nada lo pide, hereda `accessibility.default: off` de `.flutter-forge/profile.yaml`.
  Los nombres `a11y` y `accessibility.default` están confirmados.
- **Con `off`: ninguna regla de semántica.** Ni la skill, ni el blueprint, ni los tests, ni la
  auditoría la exigen ni la reportan (confirmado, aun sabiendo que no se verían casos básicos como
  un `IconButton` sin `tooltip`). La skill solo **documenta cómo activarla**.
- **Con `on`:** se carga `references/accessibility.md` y se aplican sus reglas en toda la cadena.
- **BIT-012 es independiente del interruptor.** Las keys y los `Semantics(identifier:)` para
  Patrol no son accesibilidad y no dependen de `a11y`.

**Estado actual (la política que se invierte)**
- Hoy la semántica está **encendida siempre**: `page-patterns.md` § Accessibility (6 viñetas),
  `SKILL.md:63`, `checklist.md` §10 en cada auditoría y la recomendación de guidelines en
  `widget-tests.md:68`. `hu-template.md:53` la cita como NFR, sin interruptor.
- La skill tiene buena estructura (carga selectiva de referencias por gestor de estado), pero
  **no tiene scripts ni evals**; la `description` mide ~1 000 caracteres y mezcla alcance y triggers.
- **Comentarios:** `code-comments.md` + `check_comments.py` son coherentes entre sí, pero sin fuente
  oficial citada y con `///` exigido solo en `domain/`.
- **Distribución:** capas bien definidas (`conventions.md` §1 a §8, `check_layers.py`); la única
  métrica interna de pantalla es `quality.max_build_lines` (120).

## Hallazgos

*A. Semántica y accesibilidad* (reclasificados el 2026-11-19 bajo la política opt-in: aplican solo
cuando `a11y: on`, salvo el primero)
- [x] **Alta.** No existe el interruptor `a11y` ni nadie lo lee. Es el hallazgo nuevo que ordena
      a los demás.
- [ ] **Alta (solo `on`).** (diferido a propósito, ver Cierre) "Checked by forge-audit" no se cumple: no hay script de accesibilidad;
      solo la pregunta manual §10.
- [x] **Alta (solo `on`).** `forge-tests/references/widget-tests.md:68` recomienda
      `meetsGuideline(...)` sin `tester.ensureSemantics()`: sin semántica activa las guías no miden
      nada. El ejemplo `forge_demo` sí la usa (`transactions_page_test.dart:85`).
- [x] **Alta (solo `on`).** La accesibilidad no se pide aguas arriba: `hu-template.md` solo la cita
      como ejemplo de NFR; `forge-figma` no extrae etiquetas, orden de foco ni textos alternativos;
      el blueprint no tiene columna de semántica.
- [x] **Media (solo `on`).** Cobertura incompleta: encabezados (`header`), orden de lectura
      (`sortKey`), etiquetas de campos y de estados de carga (`semanticsLabel`), anuncios asíncronos
      (`liveRegion`, `SemanticsService.announce` y `MediaQueryData.supportsAnnounce`; la API cambió
      y Android desaconseja los anuncios), lectura localizada de importes y fechas.
- [x] **Media (solo `on`).** Falta `iOSTapTargetGuideline` (44 pt) junto a
      `androidTapTargetGuideline` (48 dp); WCAG 2.2 pide 24×24 como mínimo AA y 200 % de texto. La
      skill no cita ninguna fuente.
- [x] **Media (solo `on`).** Choque no documentado: las restricciones de tamaño de
      `leading`/`trailing` en `ListTile` frente a los 48×48.
- [x] **Media (solo `on`).** El smoke test de texto grande solo detecta excepciones de overflow,
      no contenido truncado.
- [x] **Media.** Cuatro skills hablan de accesibilidad (`presentation`, `audit`, `tests`, `figma`)
      sin una fuente de verdad: umbrales repetidos con riesgo de divergir.
- [x] **Baja (solo `on`).** `ValidationFailure.serverMessage` se muestra tal cual: puede ser texto
      sin localizar ni pensado para lector de pantalla.
- [x] ~~**Media.** El ejemplo `transaction_tile.dart` no cumple la política (`semanticLabel: null`,
      sin `MergeSemantics`).~~ Con `off` deja de ser un incumplimiento (2026-11-19). Se corrige solo
      si se activa `a11y` en el ejemplo, en un commit aparte.

*B. Comentarios y documentación*
- [x] **Alta.** La política no cita *Effective Dart* (Documentation) ni el *Flutter style guide*;
      coincide en espíritu pero no es auditable ni defendible.
- [x] **Media.** `check_comments.py` exige `///` solo en `domain/`; los widgets compartidos lo piden
      en `forge-presentation` pero nadie lo verifica.
- [x] **Media.** Sin criterio de redacción del `///` (resumen de una frase, línea en blanco, detalle;
      `[Referencia]`, `{@template}`, ejemplos) ni ejemplos buenos y malos por capa.
- [x] **Baja.** El idioma fijo (inglés) no tiene su razón registrada.

*C. Nomenclatura y distribución dentro de presentación*
- [x] **Media.** `conventions.md` §8 no cubre nombres de páginas (`XPage`), widgets (`XTile`, `XCard`,
      `XSection`) ni archivos (`snake_case`, lint `file_names`).
- [x] **Media.** Solo se limita `build` (añadido 2026-11-19: complejidad ciclomática máx. 10 por `build()`, `quality.max_build_complexity`; medido en UnitedApp, 3 de 209 la superan y los 3 miden ≤120 líneas, así que complementa al límite de líneas; hoy sin script, lo cubre DCM o la revisión): no hay umbral por archivo, por anidamiento de widgets ni por
      clases por archivo. Una página de 600 líneas con widgets privados puede cumplir y seguir
      siendo ilegible.
- [x] **Media.** Sin criterio de extracción ni de promoción de widget local a compartido (p. ej.
      "al usarlo una segunda feature"); hoy depende de lo que diga `design.md`.
- [x] **Media.** Sin esqueleto recomendado de `pages/`, `widgets/`, `state/` ni regla para
      subcarpetas y secciones de pantallas largas.
- [x] **Baja.** `TransactionsFailure` (estado) frente a `Failure<T>` (resultado) se confunde al leer.
- [x] **Media.** `check_layers.py` solo valida importaciones; nada comprueba nombres, tamaño de
      archivo ni anidamiento.

*D. Evals*
- [x] **Alta.** No hay ningún eval de `forge-presentation` (tampoco de `forge-tests`,
      `forge-data-layer` ni `forge-e2e`). Sin eval no cuenta como capacidad (criterio de BIT-004).

## Plan de implementación (aprobado 2026-11-19)

*Fase 0 · Decisiones y fuentes (bajo)*
- [x] Definir el interruptor: nombre (`a11y`), valores, clave `accessibility.default` en
      `profile-schema.md` y quién lo lee (`requirements` → `deliver` → `blueprint`, `presentation`,
      `tests`, `audit`).
- [x] Verificar y fijar las fuentes (2026-11-19). Verificadas: guía de accesibilidad y página *Accessibility testing* de Flutter (48/44, guidelines, `ensureSemantics`), WCAG 2.5.8 y 1.4.4, *Effective Dart*, style guide de Flutter (sin límite de tamaño de archivo), principios de accesibilidad de Android. **Confirmado por el usuario (2026-11-19):** Apple HIG (44 pt), Android 48 dp en su fuente primaria, el tramo final del style guide y la API de anuncios contra la versión instalada de Flutter. Los datos concretos que vio no quedaron anotados aquí.
- [x] ADR corto único: interruptor opt-in, fuentes adoptadas, comentarios en **inglés** (con su
      razón) y alcance de `///`.

*Fase 1 · Contenido de `forge-presentation` (bajo a medio)*
- [x] Crear `references/accessibility.md`, cargada **solo con `a11y: on`**: encabezados, orden de
      lectura, campos y formularios, estados de carga, anuncios con la API vigente (consultando
      `supportsAnnounce`), importes y fechas, y la nota de `ListTile`. Reducir `page-patterns.md`
      § Accessibility y `SKILL.md:63` a "si `a11y: on`, ver la referencia". Única fuente de verdad.
- [x] Añadir una referencia de estructura: nombres de página, widget y archivo; esqueleto de
      carpetas; criterios de extracción y de promoción a compartido; umbrales de tamaño por archivo
      y anidamiento (**valores medidos, no supuestos**; ver la medición de la fase 4).
      Incluir un apartado breve: los widgets interactivos y los contenedores de estado se nombran y
      ubican de modo que luego puedan llevar key de prueba; la convención la decide **BIT-012**.
- [x] Reescribir la `description` más corta, separando alcance y triggers.
- [x] Plantilla de Riverpod 2.x en lugar de la nota en prosa.

*Fase 2 · Documentación y comentarios (medio)*
- [x] Citar las fuentes oficiales en `code-comments.md` y añadir la guía de redacción de `///` con
      ejemplos buenos y malos por capa.
- [x] Extender `check_comments.py`: `///` en `domain/` **y** en `paths.shared_widgets`;
      `public_member_api_docs` como opción del profile para quien la quiera; mantener el modo
      `--changed-from` de adopt.

*Fase 3 · Pruebas y auditoría (medio; toca otras skills, coordinar con BIT-002)*
- [x] Hacer condicional a `a11y: on`: `checklist.md` §10, los guidelines de `widget-tests.md`
      (con `ensureSemantics()` obligatorio, `iOSTapTargetGuideline` y una prueba de texto grande que
      compruebe contenido visible, no solo "sin excepción"), una sección de semántica en
      `design-template.md` y una columna en `blueprint-template.md`.
- [x] Añadir a `hu-template.md` el campo `a11y` (con su pregunta en la lista de brechas), para que
      la HU o los requisitos puedan activarlo.
- [x] Evaluar `check_a11y.py` en `forge-audit`, **solo para `on`** (`IconButton` sin `tooltip`,
      `Icon` sin etiqueta, `Image` sin `semanticLabel`/`excludeFromSemantics`) y un chequeo de
      nombres y tamaños; decidirlo con datos de falsos positivos.

*Fase 4 · Evals, medición y ejemplo (medio)*
- [x] Medición previa, **solo lectura** (hecha 2026-11-19 sobre `UnitedApp/lib` y `forge_demo`; cifras en `structure.md`), en UNITED y `forge_demo`: tamaño de archivo, anidamiento
      y `max_build_lines`. Con esos datos se proponen los umbrales de la fase 1.
- [x] Evals con el formato de los existentes: `presentation-sealed-state-and-disposal`,
      `presentation-a11y-semantics` (con `off` **no** exige nada; con `on` sí) y
      `presentation-naming-and-structure`. Sin comprobación de keys: eso es BIT-012.
- [ ] `forge_demo`: sin cambios mientras `a11y` esté apagado. Si se activa, corregir
      `transaction_tile.dart` y ampliar su test a la lista cargada, en un commit aparte.

**Criterio de cierre** (el de BIT-004): una referencia única de accesibilidad con el interruptor
funcionando de extremo a extremo, tests que miden semántica de verdad cuando está activa, evals
pasando, una ADR y entrada en `CHANGELOG`.

## Dependencias y límites
- BIT-001 (las etiquetas semánticas son texto localizable, solo con `a11y: on`), BIT-002
  (estrategia de pruebas; coordinar la fase 3 sobre `forge-tests`), BIT-009 (modelo y esfuerzo).
  No interfiere con BIT-010.
- **BIT-012 (keys para Patrol) depende de que termine la fase 1 de esta entrada**: ambas editan
  `forge-presentation/SKILL.md` y `blueprint-template.md`. Las columnas "a11y" (aquí) y "keys de
  prueba" (BIT-012) del blueprint se diseñan juntas para no duplicarse. La convención y la
  implementación de las keys **quedan en BIT-012**, no aquí.
- **Fuera de alcance:** las diferencias de maquetación frente a Figma se trazan en BIT-013
  (`forge-figma`, `forge-deliver`, `forge-audit`, `forge-tests`). Aquí solo se toca la parte de
  `forge-presentation` que no dependa de ella.

## Notas
- Medir antes de fijar umbrales: tamaño de archivo, anidamiento y `max_build_lines` se calibran con
  los proyectos reales (UNITED, `forge_demo`) para no inventar números.
- Riesgo asumido con `off`: la auditoría no avisa de fallos básicos de accesibilidad. Si más
  adelante se quiere un mínimo sin coste, se reabre como decisión (confirmado el 2026-11-19).

- Fase 1 (2026-11-19): `accessibility.md` y `structure.md` creadas, `SKILL.md` y `page-patterns.md`
  apuntan a ellas. Umbrales propuestos desde la medición de UnitedApp (275 archivos): archivo 300
  líneas, más de 3 clases, anidamiento 20. Son orientación hasta que un script los compruebe.
  La plantilla Riverpod 2.x dejó sin verificar la guarda tras `await` (anotado en el archivo).
  Los umbrales de `structure.md` y el apartado de keys quedan para revisión.
- Fase 2 (2026-11-19): `code-comments.md` cita *Effective Dart* (style guide sin verificar), razona
  el inglés y trae guía de `///` con ejemplos por capa. `check_comments.py` acepta `--shared-widgets`
  (con test); `public_member_api_docs` y `max_build_complexity` quedan como claves del profile.
  El script de complejidad ciclomática no existe todavía: evaluarlo en la fase 3 junto a `check_a11y.py`.
- Fase 3 (2026-11-19): `a11y` condiciona checklist §10, `flutter-reviewer`, `forge-audit` (SKILL y
  severity), `widget-tests.md`, `forge-tests/SKILL.md`, `hu-template.md` (campo y NFR), `hu-to-brief.md`
  (brecha), `brief-template.md`, `design-template.md` (sección Semantics), `blueprint-template.md`
  (columna) y `forge-deliver` (paso 3, lo registra en `state.json`). Se incluyeron `flutter-reviewer`,
  `forge-audit/SKILL.md` y `severity.md`, que la entrada no listaba.
  Evaluación de scripts (solo lectura sobre UnitedApp, proyecto sin a11y): `check_a11y.py` marcaría
  el 100 % de 32 `IconButton`, 141 `Icon` y 25 `Image`, así que no hay datos de falsos positivos
  (todo es real o decorativo). **Decisión:** si se escribe, que solo marque `IconButton` sin `tooltip`
  (preciso); `Icon` e `Image` se dejan a la revisión (muchos son decorativos dentro de botones
  etiquetados). **No implementado**: se pospone hasta que un proyecto active `a11y` y haya datos.
  Complejidad ciclomática: sin script, la cubre DCM o la revisión (ver fase 2).
- Fase 4 (2026-11-19): creados los 3 evals (`presentation-sealed-state-and-disposal`,
  `presentation-a11y-semantics`, `presentation-naming-and-structure`) con el formato de los
  existentes. Ejecutados el 2026-11-19 con `claude plugin eval` (1 corrida por brazo, con y sin plugin, coste ~0,94 USD): `sealed-state` pasa con y sin plugin (1/1), `naming-and-structure` pasa con plugin (1) y falla sin él (0), `a11y-semantics` falló en la primera corrida por un criterio mío incorrecto (exigía marcar el tap target de `IconButton`, que ya cumple 48×48, y citar `accessibility.md` sin invocar la skill); lo corregí tras ver el fallo y la repetición pasó con plugin (1) y falló sin él (0). Una sola corrida por caso: indicio, no medida estable. `forge_demo` sin cambios (`a11y` apagado).

## Cierre (2026-11-19)
Criterio de cierre cumplido: referencia única de accesibilidad con el interruptor de extremo a
extremo, tests que miden semántica cuando está activa (`ensureSemantics`), evals pasando con
plugin, ADR 0008 y entrada en `CHANGELOG`. Los hallazgos de la lista A a D quedan atendidos por las
fases 0 a 4, salvo lo diferido a propósito: `check_a11y.py` (hasta tener un proyecto con `a11y: on`),
`forge_demo` sin cambios con `a11y` apagado, y `public_member_api_docs` como opción. Los umbrales de
tamaño son empíricos (el style guide de Flutter no fija ninguno); recalibrar con más proyectos.

## Recalibración de umbrales (2026-11-19, tras el cierre)
Por decisión del usuario los umbrales pasan a ser objetivos estrictos y se nutrirán con más
proyectos: `build()` 50 líneas, complejidad 5, archivo 250, anidamiento 12 (se propuso 10; con 10
marcaba el 38 % de UnitedApp y `forge_demo` quedaba en su límite, porque la métrica cuenta la
sangría de todo el archivo; una métrica solo dentro de `build()` permitiría endurecerlo).
Con ellos, UnitedApp tiene avisos en 121 de 276 archivos (44 %) con anidamiento 10 y menos con 12:
una auditoría completa no es viable en un proyecto desordenado, por eso en `adopt`/`improve` se usa
`--changed-from`. **Decisión abierta:** si `build-lines` y `build-complexity` deben pasar a `warn` en
esos modos, o si los valores estrictos son solo el default del modo `new`. `forge_demo` se
refactorizó (`_LoadMoreOnScroll`, `_ListFooter`, `listLength`) para cumplirlos; 29 tests de Flutter
y `flutter analyze` pasan.
