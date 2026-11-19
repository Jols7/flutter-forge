# BIT-004 · Nuevas skills de refuerzo: `forge-health` y `forge-upgrade`

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-008](BIT-008-telemetria-y-metricas.md), [BIT-011](BIT-011-forge-presentation-semantica.md)

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
