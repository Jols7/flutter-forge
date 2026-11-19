---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Voy a implementar con forge-presentation una tarjeta de resultado a partir de este `design.md`
(extracto). No cambies archivos: dame el árbol de widgets y qué reglas de layout aplicas.

```
Layout (node 78627:22593): Column(gap 16) card, padding 16, radius 16, border 1
  ├─ Column(gap 16)                       ← nivel interno, su propio gap
  │    ├─ Row: título (titleMedium, onSurface) · "Ganarías" + importe (bodySmall / headlineSmall 20, onPrimaryContainer)
  │    ├─ Divider
  │    └─ Column(gap 8)                   ← filas del resumen
  │         ├─ Row(spaceBetween): etiqueta bodySmall onSurfaceVariant · valor titleMedium onSurface
  │         └─ Row(spaceBetween): etiqueta bodySmall onSurfaceVariant · valor titleMedium onSurface
  └─ Nota: padding 16, radius 16, border 1, primaryContainer

Responsive behavior: tarjeta fill (el min-width 300 del diseño se ignora: no cabe en 320 dp);
filas: etiqueta Expanded, valor Flexible; el importe de la cabecera puede llegar a $9,999,999,999.99.
```

Usa flutter-forge (forge-presentation).
