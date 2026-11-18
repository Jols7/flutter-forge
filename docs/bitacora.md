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
| BIT-004 | Nuevas skills de refuerzo: `forge-health` y `forge-upgrade` | mejora | en progreso (`forge-health` implementada; `forge-upgrade` pendiente) | 2026-11-14 |
| BIT-005 | Flavors: configuración, auditoría, alcances, límites y riesgos | auditoría, aprendizaje | pendiente | 2026-11-14 |
| BIT-006 | Inyección de dependencias: implementación, origen, distribución y comparación con UNITED | auditoría, mejora | pendiente | 2026-11-14 |
| BIT-007 | API client: consumo de endpoints, repositorios, errores e interceptores | auditoría, mejora | pendiente | 2026-11-14 |
| BIT-008 | Telemetría y métricas del agente (B4): beneficio, ahorro, costo y tiempo por tipo de corrida | revisión, mejora | en curso (`forge-metrics` implementada; falta línea base) | 2026-11-17 |

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

- **Tipo:** mejora · **Estado:** pendiente · **Alta:** 2026-11-14
- **Fuente:** `Curriculum/07_estudio-agente/04-brechas-y-diferenciador.md`
  (`/Users/joel/Documents/Curriculum/07_estudio-agente/04-brechas-y-diferenciador.md`)
- Nota: en la solicitud aparece como "flutter-healt" y "flutter-upgrade"; se nombran como
  el resto de skills del plugin (`forge-*`), acorde con el documento de brechas.

**`forge-health` (brecha B1, ⭐ objetivo principal)**
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

**Avance (2026-11-16)**
- [x] `forge-health` implementada en `plugins/flutter-forge/skills/forge-health/` (scripts,
      referencias, tests, eval `health-baseline-hotspots`, ADR 0005, CHANGELOG 0.5.0).
- [x] Profundidad `standard` (ADR 0006): `infer_layers.py`, `draft_profile.py` y cola de revisión de 30 archivos.
- [ ] Re-correr sobre UNITED para medir cobertura de capas, archivos leídos y costo (`standard` vs `quick`).
- [ ] Prueba pública: correrla sobre 1–2 repos Flutter open source y publicar informe + falsos positivos.
- [ ] Corrida real de `/flutter-forge:forge-health` (confirmar `${CLAUDE_SKILL_DIR}` y el fork).
- [ ] `forge-upgrade` (B2).

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

- **Tipo:** revisión, mejora · **Estado:** en curso · **Alta:** 2026-11-17
- **Decisión:** ADR 0007. Se implementó la skill manual `forge-metrics` (v0.7.0). Donde el plan de
  abajo difiera, manda el ADR: se mide después de cerrar las sesiones, los totales salen de
  `cost-state` sin tabla de precios, y la salida va a `.flutter-forge/metrics/`, no a `result.json`.
- **Pendiente:** correr la skill de punta a punta, agregar su eval y juntar la línea base
  (5 corridas de la HU demo y 2 auditorías).
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

## Cómo añadir una entrada

Copiar el bloque de una entrada existente, asignar el siguiente `BIT-NNN`, añadir la fila al
índice y registrar la fecha de alta. Al terminar, cambiar el estado y enlazar el ADR o el
commit que lo cerró.
