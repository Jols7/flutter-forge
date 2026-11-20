---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Figma muestra una fila de resumen con la etiqueta "Cada mes recibirías" a la izquierda y el valor
"$1,333.33" a la derecha, dentro de una tarjeta de 358 de ancho (el marco mide 390). La etiqueta mide 118
de ancho, el valor 71 y la fila 24 de alto; el valor usa `titleMedium` (Montserrat 16) en `onSurface`. En
otra fila el valor puede ser "$9,999,999,999.99" o "Cuando quieras". La app debe verse bien en un teléfono
de 320 dp, en tableta, en horizontal y con texto al 200 %.

Dame el fragmento de widgets para esa fila y el comportamiento responsivo que debe quedar en el design.md.
No cambies archivos.

Usa flutter-forge (forge-figma).
