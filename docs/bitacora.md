# Bitácora de mejoras, revisiones, actualizaciones y auditorías

Registro vivo de puntos que quiero investigar, revisar o aprender a fondo. Se va ampliando
conforme aparezcan nuevos temas. No sustituye a los ADR (`docs/adr/`): una entrada madura
aquí y, cuando se decide algo, pasa a ADR + `CHANGELOG`.

**Estados:** `pendiente` · `en curso` · `hecho` · `descartado`
**Tipos:** `mejora` · `revisión` · `actualización` · `auditoría` · `aprendizaje`

## Índice

| ID | Tema | Tipo | Estado | Alta |
|---|---|---|---|---|
| BIT-001 | Localización (l10n): configuración, optimización y comparación con UNITED | auditoría, mejora | pendiente | 2026-11-14 |
| BIT-002 | Estrategia de pruebas: unit, widget, integration_test y Patrol (+ Patrol en CI) | auditoría, mejora | pendiente | 2026-11-14 |
| BIT-003 | Secrets de GitHub | revisión | pendiente | 2026-11-14 |
| BIT-004 | Nuevas skills de refuerzo: `forge-health` y `forge-upgrade` | mejora | en progreso (`forge-health` hecha; solo `forge-upgrade` pendiente) | 2026-11-14 |
| BIT-005 | Flavors: configuración, auditoría, alcances, límites y riesgos | auditoría, aprendizaje | pendiente | 2026-11-14 |
| BIT-006 | Inyección de dependencias: implementación, origen, distribución y comparación con UNITED | auditoría, mejora | pendiente | 2026-11-14 |
| BIT-007 | API client: consumo de endpoints, repositorios, errores e interceptores | auditoría, mejora | pendiente | 2026-11-14 |
| BIT-008 | Telemetría y métricas del agente (B4): beneficio, ahorro, costo y tiempo por tipo de corrida | revisión, mejora | cerrada (2026-11-17; la línea base sigue en BIT-010) | 2026-11-17 |
| BIT-009 | Revisión de modelo y esfuerzo por agente y skill (costo vs. calidad) | revisión, mejora | pendiente | 2026-11-17 |
| BIT-010 | Línea base de `forge-metrics`: mediana, rango y ahorro con corridas reales | medición | pendiente (se acumula con el uso) | 2026-11-17 |

---

## BIT-001 · Localización (l10n)

- **Tipo:** auditoría, mejora, aprendizaje · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** `plugins/flutter-forge/skills/forge-l10n/` (`SKILL.md`,
  `references/pipelines.md`, `references/arb-patterns.md`)

**Qué quiero saber / hacer**
- [ ] Cómo se está configurando hoy (`l10n.yaml`, ARB, generación, pipelines soportados).
- [ ] Cómo funciona de punta a punta: de la cadena fija en UI a la clave ARB, y cómo la
      detectan `forge-presentation` y `forge-audit`.
- [ ] Posibles optimizaciones (plurales/select, placeholders tipados, claves por feature,
      cadenas huérfanas o duplicadas, tiempo de generación).
- [ ] Auditoría: cobertura de cadenas fijas, claves sin traducir, consistencia entre locales.
- [ ] **Comparar con la implementación actual de UNITED** (qué hace mejor cada una y qué
      conviene adoptar).

**Notas**
- Nota: el tema está escrito como "i10n" en la solicitud; el nombre correcto es
  l10n (localization). Buscar con ese nombre.
- Pendiente de ubicar el código de UNITED para la comparación.

---

## BIT-002 · Estrategia de pruebas: unit, widget, integration_test y Patrol

- **Tipo:** auditoría, mejora · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** skills `forge-tests` y `forge-e2e`, `.github/workflows/ci.yml` y
  `.github/workflows/evals.yml`, `plugins/flutter-forge/tests/`

**Qué quiero saber / hacer**
- [ ] Revisar y auditar la **escritura automática de pruebas** que genera el agente: cómo se
      configura, qué produce y con qué calidad.
- [ ] Validar **criterios de seguridad** de las pruebas (datos de prueba, credenciales,
      secretos en fixtures, qué se ejecuta contra qué entorno).
- [ ] Definir **cuándo usar cada tipo**: unit test, widget test, `integration_test` y Patrol
      (criterio de elección, costo, estabilidad, cobertura que aporta cada uno) y dejarlo
      documentado como guía en la estructura de pruebas.
- [ ] Definir la estructura de carpetas y convenciones de nombres por tipo de prueba.
- [ ] **Configurar Patrol para que corra en CI** (emulador/simulador, tiempos, artefactos,
      reintentos; hoy el E2E no corre en CI).

**Notas**
- Se escribió "test_integration" y "test_unit"; se asumen `integration_test` y `test/` (unit).
- Relacionado con B3 de `Curriculum/07_estudio-agente/04-brechas-y-diferenciador.md`
  (Patrol en CI y evals para `forge-tests` / `forge-e2e`).

---

## BIT-003 · Secrets de GitHub

- **Tipo:** revisión · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** Settings → Secrets and variables del repositorio, workflows en
  `.github/workflows/`, `SECURITY.md`

**Qué quiero saber / hacer**
- [ ] Inventario de los secrets y variables existentes (repositorio, entorno, organización).
- [ ] Verificar cuáles usa realmente cada workflow y eliminar los que no se usen.
- [ ] Revisar alcance y permisos (`permissions:` por job, tokens mínimos, entornos con
      aprobación, exposición en ramas de forks y PR).
- [ ] Definir rotación y responsables; confirmar que ninguno aparece en logs ni en el repo
      (apoyarse en `forge-security/scripts/scan_secrets.py`).
- [ ] Decidir qué secrets harán falta para Patrol en CI (BIT-002).

---

## BIT-004 · Nuevas skills de refuerzo: `forge-health` y `forge-upgrade`

- **Tipo:** mejora · **Estado:** en progreso (`forge-health` hecha 2026-11-17; solo `forge-upgrade` pendiente) · **Alta:** 2026-11-14
- **Fuente:** `Curriculum/07_estudio-agente/04-brechas-y-diferenciador.md`
  (`/Users/joel/Documents/Curriculum/07_estudio-agente/04-brechas-y-diferenciador.md`)
- Nota: en la solicitud aparece como "flutter-healt" y "flutter-upgrade"; se nombran como
  el resto de skills del plugin (`forge-*`), acorde con el documento de brechas.

**`forge-health` (brecha B1, ⭐ objetivo principal) — HECHA**
- Auditoría de proyecto completo y línea base de un repo ajeno → `health-report.md`.
- Arquitectura real vs. declarada y deuda por capa; hallazgos de seguridad, rendimiento,
  pruebas (zonas calientes sin cobertura con `git log`) y dependencias obsoletas.
- Backlog priorizado (riesgo × frecuencia de cambio × esfuerzo), quick wins vs. apuestas
  grandes, ruta de migración incremental (`adopt/improve/migrate`) y sección de decisiones
  que necesitan un humano.
- Prueba pública: correrlo sobre 1–2 repos Flutter open source y publicar informe y falsos
  positivos.
- Esfuerzo estimado: medio-alto.

**`forge-upgrade` (brecha B2)**
- Inventario de breaking changes, plan por etapas, `pub outdated` con riesgo, migración de
  APIs depreciadas, verificación (analyze + tests + build por flavor) y rollback.
- Alimenta al agente con la experiencia real de migración 3.13.8 → 3.35.
- Esfuerzo estimado: medio.

**Criterio de cierre** (del documento): cada brecha cerrada = una skill + un eval + un ADR
corto + una entrada en `CHANGELOG`. Sin eval no cuenta como capacidad.

**Avance (2026-11-16, actualizado 2026-11-17)**
- [x] `forge-health` implementada en `plugins/flutter-forge/skills/forge-health/` (scripts,
      referencias, tests, eval `health-baseline-hotspots`, ADR 0005, CHANGELOG 0.5.0).
- [x] Profundidad `standard` (ADR 0006): `infer_layers.py`, `draft_profile.py` y cola de revisión de 30 archivos.
- [x] Re-correr sobre UNITED para medir cobertura de capas, archivos leídos y costo (`standard` vs `quick`). _(cerrado por el autor el 2026-11-17)_
- [x] Prueba pública: correrla sobre 1–2 repos Flutter open source y publicar informe + falsos positivos. _(cerrado por el autor el 2026-11-17)_
- [x] Corrida real de `/flutter-forge:forge-health` (confirmar `${CLAUDE_SKILL_DIR}` y el fork). _(cerrado por el autor el 2026-11-17)_
- [ ] `forge-upgrade` (B2): **único pendiente de BIT-004**.

**Pendiente**
- [ ] Decidir el orden (el documento sugiere B1 después de una corrida grabada de
      `forge-deliver` y un eval E2E).
- [ ] Revisar el resto de brechas (B3–B9) y decidir cuáles se anotan aquí.

---

## BIT-005 · Flavors (entornos y variantes de build)

- **Tipo:** auditoría, revisión, aprendizaje · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** skill `flutter-build-release` (flavors dev/qa/prod y entrypoints),
  `forge-profile` (`detect_project.py`, `profile-schema.md`), `forge-architecture/references/core-bootstrap.md`,
  `forge-security/SKILL.md`, `SECURITY.md`

**Qué quiero saber / hacer**
- [ ] Cómo están configurados hoy: Android (`productFlavors`), iOS (schemes, xcconfig,
      build configurations), entrypoints (`main_dev.dart`, etc.), `--dart-define` o
      `--dart-define-from-file`, y cómo los detecta y modela el profile.
- [ ] Auditar la estructura: nombres consistentes entre plataformas, applicationId/bundle id
      por entorno, iconos y nombre de app por flavor, Firebase/google-services por flavor,
      firmas, y que el código no ramifique por flavor fuera del bootstrap.
- [ ] Contrastar con la documentación oficial de Flutter (flavors Android/iOS, `--flavor`,
      `--dart-define`) y con proyectos grandes existentes (open source y guías de referencia).
- [ ] Alcances y limitaciones: qué resuelven (identidad, config, endpoints, servicios) y qué
      no (no aíslan datos en runtime por sí solos, soporte desigual en web/desktop,
      sincronizar Android e iOS a mano, tiempos de build).
- [ ] Usos prácticos y configuraciones necesarias por caso (dev/qa/prod, white-label,
      instalación en paralelo, canales de distribución).
- [ ] **Cuándo usarlos y cuándo no:** criterios de decisión (p. ej. solo `--dart-define`
      si basta cambiar endpoints; flavors completos si cambian id, firma, servicios o
      branding) y costo de mantenerlos.
- [ ] **Riesgos:** compilar o publicar el entorno equivocado, secretos o claves de prod en
      artefactos dev, divergencia entre plataformas, configuraciones sin probar en CI,
      deriva de configuración; definir mitigaciones y checks automáticos.

**Notas**
- Relacionado con BIT-002 (tests por entorno) y BIT-003 (secrets por entorno en CI).

---

## BIT-006 · Inyección de dependencias

- **Tipo:** auditoría, mejora · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** `forge-architecture/references/core-bootstrap.md` y `conventions.md`,
  referencias de DI en `forge-presentation` y `forge-data-layer`, ADR 0004 (comparativa
  de arquitecturas de referencia)

**Qué quiero saber / hacer**
- [ ] Cómo se implementa hoy (paquete usado, registro manual o generado, ciclo de vida de
      singletons, factories y lazy, módulos por feature).
- [ ] De dónde se toma esta estructura (qué referencias oficiales o proyectos la inspiraron
      y qué se adoptó o descartó, ver ADR 0004).
- [ ] Cómo funciona de punta a punta: bootstrap, orden de registro, resolución en
      presentación, reemplazo en tests y por flavor (BIT-005).
- [ ] Cómo se distribuye en el proyecto: qué vive en `core` y qué en cada feature, quién
      registra qué, y si respeta las reglas de capas.
- [ ] Revisar anti-patrones (blocs singleton con estado viejo, service locator usado dentro
      de la lógica de dominio) y proponer mejoras si hacen falta.
- [ ] **Comparar con la implementación actual de UNITED.**

---

## BIT-007 · API client

- **Tipo:** auditoría, mejora · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** skills `forge-data-layer`, `forge-api-contract` (incluye
  `references/mock-interceptor.md` y `sources.md`), ADR 0002 (errores con tipo Result)

**Qué quiero saber / hacer**
- [ ] Cómo se implementa hoy: cliente HTTP, consumo de endpoints, base URL por entorno,
      serialización y mapeo a modelos.
- [ ] De dónde se toma esta estructura y qué se adoptó de referencias externas.
- [ ] Cómo funciona de punta a punta y cómo se conecta con los repositorios (datasource →
      repositorio → dominio).
- [ ] Manejo de errores: traducción de fallos de red y HTTP al tipo de error del dominio,
      reintentos, timeouts, cancelación.
- [ ] Interceptores: autenticación y refresco de token, logging sin datos sensibles,
      mock, cabeceras comunes; orden y responsabilidades.
- [ ] Cómo se distribuye en el proyecto y cómo se registra en la inyección (BIT-006).
- [ ] Revisar y mejorar lo necesario; **comparar con la implementación actual de UNITED.**

**Notas**
- Mismos puntos que BIT-006; se revisan juntos porque el cliente se registra vía DI.

---

## BIT-008 · Telemetría y métricas del propio agente (brecha B4)

- **Tipo:** revisión, mejora · **Estado:** cerrada el 2026-11-17 (skill entregada; la línea base pasó a BIT-010) · **Alta:** 2026-11-17
- **Decisión:** ADR 0007. Se implementó la skill manual `forge-metrics` (v0.7.0). Donde el plan de
  abajo difiera, manda el ADR: se mide después de cerrar las sesiones, los totales salen de
  `cost-state` sin tabla de precios, y la salida va a `.flutter-forge/metrics/`, no a `result.json`.
- **Cerrado (2026-11-17):**
  - [x] Corrida de punta a punta sobre datos reales: `run_metrics.py --slug simulador-inversion`
        sobre UnitedApp (deliver, 4 sesiones, \$15.43 a precios de API, 232 llamadas, 93 min de
        pared / 65 activos, 11/11 ACs, 3 hallazgos corregidos). Funciona sin `--write` y no copia texto.
        `--list` también reconoce las sesiones de `forge-*` de ese proyecto.
  - [x] Pruebas: 15 de `test_metrics.py` y 87 en total, en verde.
  - [x] Evals `metrics-interpret-run` y `metrics-incomplete-no-invention` (3/3 jueces; delta 0
        frente a sin plugin, porque las reglas van en el prompt, como en `forge-health`; la skill es
        manual y no se puede invocar en un eval).
- **Cierre:** se cumple el criterio de brecha cerrada (skill + eval + ADR + `CHANGELOG`). La línea
  base valida lo que la skill medirá, no la skill; se mueve a **BIT-010** y no bloquea BIT-009.
  Límites vigentes: sin `baseline_estimate_hours` previo el ahorro no se calcula, y con menos de
  5 corridas completas de un tipo se reporta como anécdota.
- **Hallazgos al verificar:** esa corrida es anterior a `phase_log`, así que fix y report quedan
  dentro de `review`; hay 5 sesiones adyacentes sin contar y una `linked` (`1ac9e0ce`) por confirmar.
- **Fuente:** `Curriculum/07_estudio-agente/04-brechas-y-diferenciador.md`, sección B4
  (`/Users/joel/Documents/Curriculum/07_estudio-agente/04-brechas-y-diferenciador.md`).
  El documento la ordena tercera por impacto/esfuerzo (esfuerzo bajo).
- **Dónde mirar:** `forge-deliver/references/result.schema.json`, `result.example.json`,
  `run-state.md` (`state.json`), `report-template.md`, `docs/subagent-contract.md`,
  `forge-health/scripts/health_snapshot.py` (ya produce `metrics.json`), `.github/workflows/evals.yml`.

**Objetivo de la revisión**
Decidir la mejor forma de medir, por cada tipo de uso de flutter-forge, **cuánto cuesta, cuánto
tarda, cuánto ahorra y qué beneficio deja**, con datos propios y no con estimaciones. Hoy la
cifra "5 → 2 días" viene del plugin interno y no se puede reproducir con este repo.

**Tipos de corrida que hay que poder medir**

| Tipo | Entrada | Salida que ya existe | Qué se mide hoy |
|---|---|---|---|
| Implementación completa | `forge-deliver` (HU → feature) | `result.json`, `report.md`, `state.json` | Nada de eficiencia; `state.json` solo guarda `started_at` / `updated_at` |
| Revisión / auditoría de un diff | `flutter-reviewer`, `forge-audit`, `forge-security` | `findings.md`, `review.findings[]` | Conteos por severidad y estado, sin tiempo ni costo |
| Auditoría de proyecto completo | `forge-health` | `health-report.md`, `metrics.json` | Métricas **del repo**, no del agente |
| Skills sueltas (contrato, tests, l10n…) | cada `forge-*` | su archivo de run | Nada |

**Hallazgos de la revisión (verificados el 2026-11-17)**
- `result.schema.json` es `schema: 1` y solo admite agregar campos opcionales (política de
  `subagent-contract.md`). Añadir `metrics` **no rompe a ningún orquestador**.
- `state.json` ya se reescribe de forma atómica en cada fase y guarda `started_at`/`updated_at`:
  es el punto natural para marcar inicio y fin por fase.
- Los gates ya quedan registrados (`gates.*.status`, `at`, `notes`), pero no si la persona
  **cambió** algo. Eso es lo que falta para medir "tasa de aceptación".
- `review.findings[].status` ya distingue `open/fixed/wontfix/deferred`, así que la tasa de
  hallazgos aceptados se puede calcular sin campos nuevos.
- **El agente no ve sus propios tokens.** Un skill no tiene API para consultar su consumo. Si se
  le pide "estima tus tokens" el número es inventado. Hay que obtenerlo de fuera del modelo.
- Los transcripts de Claude Code (`~/.claude/projects/<proyecto>/*.jsonl`) **sí** guardan por
  mensaje `usage` (`input_tokens`, `output_tokens`, `cache_read_input_tokens`,
  `cache_creation_input_tokens`), el modelo y la marca de tiempo, y los subagentes tienen su
  propia carpeta de logs. Verificado sobre una sesión real de este repo: se pueden sumar
  tokens por modelo y duración total sin instrumentar nada. También hay registros `cost-state`.
- Ese formato **no es contrato público** y puede cambiar; además contiene el contenido de la
  conversación. Cualquier lector debe extraer solo contadores y nunca copiar texto al reporte.

**Opciones de implementación**

| Opción | Cómo | Pros | Contras |
|---|---|---|---|
| A. Auto-reporte del agente | El modelo rellena `metrics` en `result.json` | Cero infraestructura | Tokens y costo serían inventados; tiempo poco fiable. **Descartada** para tokens/costo |
| B. Script que lee el transcript | `scripts/run_metrics.py` suma `usage` y tiempos de la sesión y subagentes de un run y escribe `metrics.json` | Datos reales, determinista, mismo patrón que `forge-health` (scripts cuentan, el modelo juzga), testeable | Depende del formato del transcript y de su ruta; hay que acotar la sesión al run |
| C. Hooks + OpenTelemetry de Claude Code | Hooks (`SubagentStop`, `Stop`) y exportación OTel a un colector | Mejor para equipos y series largas | Requiere infraestructura y configuración por usuario; excesivo para un plugin genérico |
| D. Híbrida **(recomendada)** | Fase y gates los marca el agente en `state.json` (tiempo y conteos, hechos que sí conoce) + script B para tokens/costo, ejecutado al cerrar la fase 8 | Cubre todo con esfuerzo bajo; C queda como extensión | Hay que definir cómo asociar sesión ↔ run |

**Propuesta de datos (campos opcionales, `schema` sigue en 1)**
- `metrics.timing`: `started_at`, `finished_at`, `wall_seconds`, `phases[]` con `name`,
  `seconds`, `retries`. `wall_seconds` incluye las esperas en gates, así que añadir también
  `active_seconds` (sin gates) para no inflar el tiempo del agente con el tiempo humano.
- `metrics.usage`: por modelo `input`, `output`, `cache_read`, `cache_write`; `subagents` por
  separado; `estimated_cost` con `currency`, `pricing_as_of` y `pricing_source`. **Precios no
  hardcodeados en el código**: tabla en un archivo de referencia con fecha, porque cambian.
- `metrics.human`: `gates_total`, `gates_changed` (la persona modificó el brief o el blueprint),
  `questions_answered`, `findings_by_status` (`fixed/wontfix/deferred/open`),
  `acceptance_rate` = `fixed / (fixed + wontfix)` sobre hallazgos propuestos.
- `metrics.quality`: ACs `implemented-tested / total`, `analyze` limpio sí/no, violaciones de
  capas antes y después, reintentos de tests hasta verde.
- `metrics.run_type`: `deliver | review | audit | health | skill` para poder agregar por tipo.
- Fuera de `result.json`: un `metrics.json` por run y un agregado `.flutter-forge/metrics/history.jsonl`
  (una línea por corrida) para comparar corridas y calcular medianas.

**Cómo responder "¿cuánto ahorra?" sin engañarse**
El ahorro no se mide con el agente solo; hace falta un **contrafactual**:
- **Línea base humana:** estimación previa del equipo (horas) registrada **antes** de correr, en
  el brief (`baseline_estimate_hours`), no después. Si se estima después, el sesgo anula el dato.
- **Tiempo de revisión humana:** cronometrar lo que tarda la persona en revisar y corregir lo
  entregado; el ahorro neto es `baseline − (tiempo_agente_activo + revisión + retrabajo)`.
- **Costo por feature** = tokens × precio + tiempo humano de revisión × tarifa (la tarifa la pone
  quien lee; no se asume ninguna).
- **Muestra:** una corrida no prueba nada. Reportar mediana y rango sobre N ≥ 5 por tipo, y
  separar casos fáciles de difíciles (la HU demo tiene huecos plantados: sirve de caso fijo).
- **Beneficio de calidad, además del ahorro:** hallazgos detectados antes de merge, gaps de la HU
  encontrados vs. plantados, cobertura y violaciones de capas evitadas.

**Métricas por tipo de corrida (qué reportar en cada una)**

| Tipo | Costo / tiempo | Beneficio | Ahorro |
|---|---|---|---|
| Implementación completa | Tokens y minutos activos por fase; reintentos | ACs cubiertos, gaps detectados, hallazgos corregidos | Horas estimadas − (activo + revisión + retrabajo) |
| Revisión de diff | Tokens por 100 líneas del diff; minutos | Hallazgos por severidad, tasa de aceptación | Tiempo de revisión humana evitado (estimado por la persona) |
| Auditoría de repo (`forge-health`) | Tokens y minutos por 1 000 archivos `.dart` | Backlog priorizado, quick wins, decisiones humanas listadas | Auditoría manual comparable (horas) |
| Skill suelta | Tokens y minutos | Salida válida a la primera sí/no | Estimación por skill |

**Plan de implementación sugerido (esfuerzo bajo, ~1–2 días)**
- [ ] Definir el bloque `metrics` en `result.schema.json` (solo campos opcionales) y actualizar
      `result.example.json`; añadir una prueba que valide el ejemplo.
- [ ] `state.json`: marcar `started_at`/`finished_at` por fase y contar gates cambiados y
      reintentos (cambio en `run-state.md` y en `forge-deliver/SKILL.md`).
- [ ] `forge-deliver/scripts/run_metrics.py`: leer el transcript de la sesión (y subagentes)
      acotado entre `started_at` y `finished_at` del run, sumar `usage` por modelo, escribir
      `metrics.json`, **sin copiar texto de la conversación**. Con `--transcript` explícito y
      degradación limpia (`usage: null`, razón) si no encuentra o no entiende el formato.
- [ ] Referencia `pricing.md` con tabla de precios, fecha y fuente; cálculo en el script.
- [ ] Sección **Métricas** en `report-template.md` (tiempo, costo, aceptación) y `history.jsonl`.
- [ ] Campo opcional `baseline_estimate_hours` en el brief para el ahorro.
- [ ] Mismo bloque para `flutter-reviewer` y `forge-health` (reutilizar el script).
- [ ] Eval: una corrida de la HU demo debe producir `metrics.json` válido con `usage` no nulo y
      sin texto de la conversación; prueba de que el script degrada bien sin transcript.
- [ ] ADR 0007 (telemetría local, opcional y sin envío externo) + entrada en `CHANGELOG`.
- [ ] Baseline real: correr 5 veces la HU demo y 2 auditorías; publicar la tabla con mediana y rango.

**Riesgos y decisiones abiertas**
- **Privacidad:** el transcript contiene código y conversación. Las métricas deben quedar
  **locales** (en `.flutter-forge/`), solo contadores, nunca enviarse a ningún servicio, y
  `.flutter-forge/metrics/` debe quedar documentado respecto a `.gitignore`. Decidir si
  `history.jsonl` se versiona (equipo) o no (individual).
- **Costo estimado vs. facturado:** con plan de suscripción no hay cobro por token; reportar
  "equivalente a precios de API" y decir que es una estimación, no una factura.
- **Caché:** el grueso de los tokens de entrada son lecturas de caché (en la sesión revisada, de
  cientos de millones de tokens de entrada la inmensa mayoría eran `cache_read`). Separarlo, o
  el costo saldrá muy distinto según el precio que se aplique.
- **Asociar sesión ↔ run:** una sesión puede contener varios runs o un run abarcar varias sesiones
  (`resume`). Acotar por `started_at`/`finished_at` del run y por `cwd`; documentar el límite.
- **Subagentes en modo orquestado:** si el engineer corre como subagente de otro orquestador, el
  orquestador es quien tiene los tokens; el contrato debería permitir que los inyecte
  (`metrics.usage.source: "orchestrator"`).
- **No confundir con la métrica de `forge-health`:** `metrics.json` de `forge-health` mide el
  repo. Renombrar o prefijar (`run-metrics.json`) para evitar choques.
- **Sesgo:** no publicar cifras de ahorro sin la línea base previa y sin N suficiente.
- Decidir si se agrega un comando/skill de lectura (`forge-stats`) que resuma `history.jsonl`,
  o si basta con el reporte por run.

**Criterio de cierre** (regla del documento de brechas): skill/script + eval + ADR corto +
entrada en `CHANGELOG`. Sin eval no cuenta como capacidad.

**Notas**
- Relacionado con BIT-004 (`forge-health` ya tiene un pendiente de "medir cobertura, archivos
  leídos y costo `standard` vs `quick`": este trabajo lo habilita) y con B3 (evals E2E y corrida
  grabada de `forge-deliver`, que son la fuente de las primeras muestras).
- La tabla "¿Ahorra tiempo/costo?" del documento pide: tiempo y tokens por feature, % de
  hallazgos aceptados y comparación con estimación. Este diseño cubre las tres.

---

## BIT-009 · Revisión de modelo y esfuerzo por agente y skill

- **Tipo:** revisión, mejora · **Estado:** pendiente · **Alta:** 2026-11-17
- **Dónde mirar:** frontmatter de `plugins/flutter-forge/agents/*.md` y de
  `plugins/flutter-forge/skills/*/SKILL.md`, `forge-deliver/SKILL.md` (orquestador),
  `docs/subagent-contract.md`, ADR 0003 (revisión en contexto separado)

**Estado actual (verificado el 2026-11-17)**

| Componente | `model` hoy | Notas |
|---|---|---|
| Agente `flutter-engineer` | `sonnet` | Orquesta todo el pipeline |
| Agente `flutter-reviewer` | `sonnet` | Solo lectura; audit + security |
| Skill `forge-health` | `sonnet` (+ `context: fork`, `disable-model-invocation`) | Auditoría de repo completo |
| Las otras 15 skills (`forge-api-contract`, `-architecture`, `-audit`, `-blueprint`, `-data-layer`, `-deliver`, `-e2e`, `-figma`, `-l10n`, `-learn`, `-presentation`, `-profile`, `-requirements`, `-security`, `-tests`) | sin definir | Heredan el modelo de la sesión: quien las invoque con un modelo caro paga eso |

Ningún componente define `effort`. Cuando una skill corre dentro de un agente, el modelo
efectivo lo manda el agente; cuando se invoca suelta, el de la sesión.

**Qué quiero saber / hacer**
- [ ] Clasificar cada skill por **tipo de trabajo**: mecánico/determinista (scripts + plantillas),
      generación de código con reglas claras, o juicio (planear, revisar, priorizar, decidir).
- [ ] Proponer modelo y esfuerzo por componente, priorizando resultado donde un error cuesta caro
      y ahorrando donde el trabajo es mecánico. Hipótesis inicial a validar, no decisión:

| Componente | Naturaleza | Hipótesis de modelo | Esfuerzo |
|---|---|---|---|
| `forge-profile`, `forge-learn`, `forge-l10n` | detección y plantillas | modelo ligero (haiku) o sonnet | bajo |
| `forge-api-contract`, `forge-figma` | extracción y mapeo | sonnet | bajo–medio |
| `forge-data-layer`, `forge-presentation`, `forge-tests`, `forge-e2e` | generación con reglas | sonnet | medio |
| `forge-requirements`, `forge-blueprint` | interpretar huecos de la HU y planear clases | **evaluar un modelo superior** (un error aquí se propaga a todo el código) | alto |
| `forge-audit`, `forge-security`, agente `flutter-reviewer` | revisión y juicio | **evaluar un modelo superior** (buscan lo que los scanners no ven) | alto |
| `forge-health` | priorización y decisiones humanas | sonnet hoy; medir si un modelo superior mejora el backlog | medio–alto |
| `flutter-engineer` / `forge-deliver` | orquestación larga | sonnet; valorar subir si pierde el hilo entre fases | medio |

- [ ] **¿Subir el modelo de los agentes?** Medir antes de decidir. Un modelo mayor en planeación y
      revisión puede costar más por token pero ahorrar reintentos y retrabajo; hay que
      comprobarlo con datos, no suponerlo.
- [ ] Comparar por configuración, con la misma entrada y las mismas rúbricas: modelo ligero vs.
      sonnet vs. superior, y esfuerzo bajo/medio/alto. Métricas: ¿compila?, ¿pasa analyze y tests?,
      ¿respeta capas?, recall y precisión de hallazgos sobre un repo con defectos sembrados
      (B3), gaps de la HU detectados vs. plantados, reintentos, tokens y minutos.
- [ ] Verificar en la documentación vigente de Claude Code qué campos acepta el frontmatter de
      skills y agentes (`model`, `effort`, alias vs. id completo) y cómo se hereda el modelo
      cuando una skill corre dentro de un agente o en `context: fork`. No asumir.
- [ ] Decidir la política: alias (`sonnet`, `opus`, `haiku`) que siguen la versión vigente vs. id
      fijo que da reproducibilidad. Registrar el costo de que un alias cambie de modelo sin aviso
      (los evals semanales detectarían una regresión).
- [ ] Permitir que el proyecto sobrescriba el modelo (por ejemplo en `profile.yaml` o en el brief
      del orquestador) para quien prefiera ahorrar o priorizar calidad.
- [ ] Reglas de uso: qué fases pueden delegarse a un modelo ligero sin pasar por el gate, y cuáles
      no. El gate humano no debe depender de un modelo débil.
- [ ] Documentar la decisión en un ADR y reflejarla en `CHANGELOG` y `docs/architecture.md`.

**Riesgos**
- Un modelo barato en una fase temprana (requisitos, blueprint) abarata esa fase y encarece las
  siguientes: medir el costo del run completo, no el de cada skill.
- Fijar el modelo en una skill sobrescribe la elección de quien la invoca; dejar sin definir es
  a veces lo correcto para skills que se usan sueltas.
- Un modelo superior en el revisor no sirve si el contexto que recibe es ruido: revisar primero
  que los scanners filtren antes del LLM (principio 5 de `architecture.md`).

**Notas**
- Depende de BIT-008: sin telemetría de tokens, tiempo y tasa de aceptación por run no hay forma
  de justificar el cambio con datos. Hacer primero BIT-008, o al menos su script de métricas.
- Relacionado con B3 (evals con repos sembrados, que dan recall y precisión por configuración).
- Los modelos y precios cambian: la tabla de hipótesis se valida con los vigentes al medir.

---

## BIT-010 · Línea base de `forge-metrics`: mediana, rango y ahorro

- **Tipo:** medición · **Estado:** pendiente (se acumula con el uso) · **Alta:** 2026-11-17
- **Origen:** pendiente de BIT-008. La skill ya mide; falta tener corridas comparables para que
  sus cifras signifiquen algo. Alimenta BIT-009 (modelo y esfuerzo por componente).

**Requerimientos previos**
- [ ] Plugin `flutter-forge` en la versión 0.7.0 o superior (registra `phase_log`, `gates.*.changed`,
      `retries` y `baseline_estimate_hours`). Anotar la versión usada.
- [ ] Proyecto Flutter con `.flutter-forge/profile.yaml` (UNITED u otro) y la misma rama base en
      todas las corridas.
- [ ] Una **HU fija** con huecos conocidos; escribir la lista de huecos plantados **antes** de
      correr, para medir cuántos detecta el agente.
- [ ] Un mismo modelo y esfuerzo en las 5 corridas de implementación. Cambiarlos es objeto de BIT-009.
- [ ] `baseline_estimate_hours` definido **antes** de la primera corrida, igual en todas, con quién
      lo estimó y cómo. Para auditorías, la estimación manual equivalente.
- [ ] Un cronómetro para el tiempo humano de revisión y retrabajo por corrida (`--review-hours`).
- [ ] Tarifa horaria que usará quien lea el informe (no se asume ninguna).

**Pasos por corrida de implementación (5, tipo `deliver`)**
1. Slug nuevo y distinto (`base-01` … `base-05`), sesiones nuevas, sin trabajo ajeno en medio.
2. `/flutter-forge:forge-deliver` con la HU fija; responder los gates normalmente.
3. Cronometrar la revisión y corrección humana de lo entregado.
4. Cerrar **todas** las sesiones de la corrida (el costo oficial solo existe al cerrarlas).
5. En sesión nueva: `/flutter-forge:forge-metrics base-0N --review-hours <h>`; confirmar las
   sesiones `linked` y `adjacent` con `--include` o `--exclude`.
6. Revisar que el resultado sea `complete`, no `INCOMPLETE`, y sin advertencias de `phase_log`.

**Pasos por auditoría (2, tipo `review` o `health`)**
1. Misma entrada para ambas (mismo repo y mismo commit) con `flutter-reviewer` o `forge-health`.
2. Cerrar la sesión; medir con `--session <id> --id audit-0N --review-hours <h> --write`.
3. Registrar los hallazgos aceptados y rechazados. `--review-hours` es el tiempo humano de leer la
   salida y decidir qué se acepta. Con `--session` el script no lee `baseline_estimate_hours`
   (sale de `state.json`, que una auditoría no tiene), así que el ahorro de una auditoría no sale
   calculado: se compara a mano con la estimación manual previa, o se omite.
4. Las 2 auditorías son independientes de las 5 corridas (la corrida ya incluye su propia fase de
   revisión). Se recomienda una de cada tipo; ninguna llega a 5, así que se reportan como anécdota.

**Estrategia acordada (2026-11-18): repetir `simulador-inversion` desde un punto anterior**

Donde difiera de los pasos genéricos de arriba, manda esta sección. Los hashes son los de
`git log` de UnitedApp al 2026-11-18; confirmarlos antes de usarlos: la implementación original es
`f9d5ba0` (feat) con `5d5229c` (chore E2E), y su padre `0ef68b5` es el último commit anterior.

*Decisiones*
- **Perfil sí, brief no.** El perfil (`forge-profile`) es preparación única y no es costo de la
  feature: se genera una vez y se confirma en el commit base. El **brief se genera en cada
  corrida** a partir de la HU, porque la fase de requisitos y el Gate 1 son parte de lo que se
  mide, y la estimación `baseline_estimate_hours` (HU → listo para merge) también los incluye.
  Si se commitea un brief ya hecho y las corridas parten del diseño, se mide menos que lo que
  cubre la estimación y el ahorro sale inflado. Esa variante solo vale como estudio aparte, con
  `phases` acotadas y una estimación que también excluya requisitos.
- **Un solo directorio de trabajo** para todas las mediciones (`UnitedApp-baseline`, un worktree
  o clon de UnitedApp), no tu copia de trabajo (tiene cambios sin commitear) ni un worktree por
  corrida. El script busca los transcripts por la ruta del proyecto y guarda `history.jsonl` dentro
  de él: con rutas distintas, `--summary` no agruparía las corridas. `.flutter-forge/metrics/` se
  ignora por git y por eso sobrevive al cambiar de rama.
- **Las auditorías no dependen de las corridas.** Se hacen en el mismo directorio y antes de las
  corridas: son cortas, no dejan nada en el commit base y sirven de ensayo del procedimiento de
  medición (cerrar sesiones, `--session`, `--include/--exclude`) antes de gastar en las cinco.

*Pasos*
0. **Preparar el directorio.** Crear `UnitedApp-baseline` desde un checkout limpio de `0ef68b5`;
   `flutter pub get`, generación de código y lo que pida el proyecto. Dejar fuera la rama de la
   implementación original (sin remoto ni ramas locales que la contengan) para que el agente no
   la lea en el historial; el diff de la auditoría `review` se obtiene antes y se guarda aparte.
1. **Commit base `B`.** Rama `baseline/base` desde `0ef68b5`. Ejecutar `forge-profile`, revisar el
   perfil, commitear `.flutter-forge/profile.yaml` y `layers.json` y la HU fuente (`hu.md` o
   la fuente que use el proyecto). Es lo único que se agrega. Anotar el hash de `B`, la versión del
   plugin, el modelo y el esfuerzo. Todas las corridas parten de `B`.
2. **Fijar la estimación.** Con la definición de `baseline_estimate_hours` de arriba, sin mirar la
   corrida original, escribirla junto con la persona que la estimó y la fecha en la hoja de
   entregables y en un archivo de texto para responder siempre igual cuando `forge-deliver` la pida.
3. **Preparar respuestas fijas a los gates.** Escribir una sola vez qué responderás en los gates
   de la HU (huecos plantados, decisiones) y reutilizarlas. Reduce la variación y el efecto de
   aprendizaje; anotar que el tiempo de revisión es el de alguien que ya conoce el caso.
4. **Auditoría `health`.** En `B` (checkout de `baseline/base`), en sesión propia con
   `forge-health`; cerrar la sesión; `/flutter-forge:forge-metrics --session <id> --id audit-health
   --review-hours <h>`. Descartar lo que escriba en el árbol (`git clean`/`reset`): `B` no cambia.
5. **Auditoría `review`.** Checkout de `f9d5ba0` (con `5d5229c` si se quiere el E2E) y revisar el
   diff `0ef68b5..f9d5ba0` con `flutter-reviewer`; cerrar; medir con `--id audit-review`. Volver a
   `B` y limpiar.
6. **Corridas `base-01` … `base-05`**, una por una:
   1. `git switch -C run/base-0N baseline/base` (árbol limpio, desde `B`).
   2. Sesión nueva; `/flutter-forge:forge-deliver` con la HU y el slug `base-0N`. Responder los
      gates con las respuestas fijas y la misma estimación.
   3. Decidir una vez y mantener en las cinco si se corre el E2E (necesita dispositivo y
      credenciales; si no, queda `pending-run` en todas).
   4. Cronometrar la revisión y las correcciones humanas, y los gates.
   5. Cerrar **todas** las sesiones de la corrida.
   6. **Antes de cambiar de rama**, en sesión nueva: `/flutter-forge:forge-metrics base-0N
      --review-hours <h>` (necesita `.flutter-forge/runs/base-0N` presente). Confirmar sesiones
      `linked` y `adjacent`. Debe quedar `complete` y sin advertencias de `phase_log`.
   7. Commitear en `run/base-0N` la carpeta de la corrida y el código, para conservar la evidencia.
7. **Resumen.** `/flutter-forge:forge-metrics --summary` en `UnitedApp-baseline`: debe mostrar
   `deliver` con 5 corridas completas, y `review` y `health` con 1 cada una. Pasar a la hoja de
   entregables y escribir el informe de `docs/`.

*Riesgos de esta estrategia*
- **Contaminación:** historial de git, memoria de Claude Code del proyecto o `forge-learn`
  arrastrando datos de una corrida a la siguiente. Revisar antes de la corrida 2 que `B` y
  `.flutter-forge/` estén idénticos al inicio.
- **Medición tardía:** cambiar de rama sin medir pierde `state.json`/`result.json` (si no se
  commitearon) y deja la corrida sin outcome.
- **Una sola tarea:** la mediana describe esta feature, no todas. Complementar con features reales.

**Resultados esperados**
- 5 corridas `complete` de tipo deliver y 2 de auditoría, cada una con `baseline_estimate_hours` y
  `review_hours`, sin sesiones por confirmar.
- Por tipo: mediana y rango de costo (a precios de API), minutos activos y de modelo, costo por AC,
  tasa de aceptación de hallazgos, reintentos y gates cambiados; fase más cara y su variación.
- Ahorro por corrida = `baseline − (activo + revisión + retrabajo)` y su mediana y rango; costo por
  feature = costo a precios de API + horas humanas × tarifa.
- Huecos de la HU detectados frente a plantados.
- Lectura honesta: qué varía entre corridas (si el rango es muy amplio, la mediana dice poco).

**Entregables**
- `.flutter-forge/metrics/` con los `<id>.json`, `<id>.md` y `history.jsonl` de las 7 mediciones
  (solo contadores; se pueden compartir sin texto de la conversación).
- Salida de `run_metrics.py --summary` y la tabla de mediana y rango por tipo.
- Hoja con: HU usada, huecos plantados, `baseline_estimate_hours` y quién lo estimó, `--review-hours`
  de cada corrida, tarifa y versiones (plugin, modelo).
- Informe corto en `docs/` con la tabla, el ahorro calculado y los límites; entrada en `CHANGELOG`
  si cambia algo de la skill.
- Cierre de BIT-010 y datos de entrada para BIT-009.

**Criterio de cierre**
Los 7 resultados completos y el informe publicado. Si no se alcanzan 5 corridas del tipo, se
reporta como anécdota y la entrada sigue abierta. Cada feature real entregada con 0.7.0 y medida
cuenta como una corrida más.

**Notas**
- Una corrida no prueba nada; separar casos fáciles de difíciles.
- No hay que repetir las corridas por la línea base: si el trabajo es real, mide cada feature normal.
- La corrida de UnitedApp (`simulador-inversion`) no cuenta: es anterior a `phase_log` y sin estimación previa.

---

## Cómo añadir una entrada

Copiar el bloque de una entrada existente, asignar el siguiente `BIT-NNN`, añadir la fila al
índice y registrar la fecha de alta. Al terminar, cambiar el estado y enlazar el ADR o el
commit que lo cerró.
