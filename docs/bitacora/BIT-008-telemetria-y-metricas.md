# BIT-008 · Telemetría y métricas del propio agente (brecha B4)

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-004](BIT-004-skills-forge-health-y-upgrade.md), [BIT-009](BIT-009-modelo-y-esfuerzo.md), [BIT-010](BIT-010-linea-base-forge-metrics.md)

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
