---
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

El feature "transfers" tiene dos pantallas (formulario y confirmación) y una lista de cuentas. El blueprint declara `TransferKeys` con `amount`, `submit`, `confirm` y `item(id)`. Al escribir la prueba Patrol descubro que el botón "Cancelar" de la confirmación no tiene key. ¿Qué finders uso en el test, y qué hago con "Cancelar"? ¿Puedo agregarle la key en la página para terminar rápido?
