# BIT-001 · Localización (l10n)

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-011](BIT-011-forge-presentation-semantica.md)

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
- Relación con BIT-011 (2026-11-19): las etiquetas semánticas (`Semantics(label:)`, `tooltip`,
  textos para lector de pantalla) son texto localizable y deben pasar por l10n, pero **solo cuando
  el interruptor `a11y` está en `on`**. Por defecto está apagado; no hay claves de ARB de
  accesibilidad que añadir hasta entonces.
