---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Te paso el CSS que Figma generó para una tarjeta de resultado. No hay Figma MCP. Conviértelo a un árbol
de widgets de Flutter. Usa la paleta de un proyecto con `AppColors` (getters `surfaceContainerLow`,
`onSurface`, `onSurfaceVariant`, `primary`, `onPrimaryContainer`) y `Theme.of(context).textTheme`. No cambies archivos.

```css
.card { display:flex; flex-direction:column; gap:16px; width:343px; padding:16px;
        border-radius:16px; border:1px solid rgba(255,126,43,.16); background:#FFF1EB; }
.header { display:flex; justify-content:space-between; align-items:flex-start; width:311px; }
.title  { width:149px; font:500 16px/24px Montserrat; color:#221A15; }
.amount { width:139px; font:400 20px Unbounded; color:#703715; text-align:right; }
.row    { display:flex; justify-content:space-between; width:311px; gap:8px; }
.label  { font:400 12px/16px 'DM Sans'; color:#9E8B81; }
.value  { font:500 16px/24px Montserrat; color:#221A15; }
.line   { width:268px; height:1px; background:#FF7E2B; }
```

Usa flutter-forge (forge-figma, modo CSS).
