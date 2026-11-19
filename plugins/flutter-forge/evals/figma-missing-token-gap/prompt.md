---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Estoy mapeando un diseño de Figma a un proyecto Flutter. El tema define `AppColors.primary` (#FF7E2B),
`AppColors.onSurface` (#221A15), `AppColors.white` (#FFFFFF) y `AppColors.outlineVariant` (#D7C2B9); no
tiene `onPrimary`. Las fuentes del proyecto son `DMSans` y `Unbounded`. No cambies archivos.

Variables que Figma devolvió para la pantalla:

- `Schemes/Primary` = #ff7e2b
- `Schemes/On Primary` = #ffffff
- `Schemes/Outline Variant` = #d7c2b9
- `State Layers/Primary/Opacity-16` = #8d4e2a29 (se usa como borde de tarjetas y chips)
- `PGI United/title/medium` = Montserrat Medium 16/24
- `PGI United/headline/super small` = Unbounded 20, sin rol en el tema

Dime cómo quedan los tokens, qué es un gap y qué hay que decidir. Entrega la tabla de tokens y la de gaps.

Usa flutter-forge (forge-figma).
