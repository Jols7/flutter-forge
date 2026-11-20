---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

El diseño de Figma de un listado de cuentas dice: cada fila mide 64 de alto, con un avatar de 40×40 a la
izquierda (16 de margen), título y subtítulo en dos líneas, un importe alineado a la derecha y 12 de
espacio entre el avatar y el texto. El botón principal mide 40 de alto con radio 48. El selector de
divisa son tres chips de 34 de alto.

El proyecto usa Material 3 con `ListTile`, `FilledButton` y `ChoiceChip`. No cambies archivos. Dime, por
cada componente, si basta el widget Material por defecto, si se ajusta con parámetros o si conviene un
widget propio, y registra la decisión como lo hace forge-figma.

Usa flutter-forge (forge-figma).
