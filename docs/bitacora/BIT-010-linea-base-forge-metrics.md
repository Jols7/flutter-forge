# BIT-010 · Línea base de `forge-metrics`: mediana, rango y ahorro

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-008](BIT-008-telemetria-y-metricas.md), [BIT-009](BIT-009-modelo-y-esfuerzo.md), [BIT-011](BIT-011-forge-presentation-semantica.md)

- **Tipo:** medición · **Estado:** pendiente (se acumula con el uso) · **Alta:** 2026-11-17
- **Origen:** pendiente de BIT-008. La skill ya mide; falta tener corridas comparables para que
  sus cifras signifiquen algo. Alimenta BIT-009 (modelo y esfuerzo por componente).

**Requerimientos previos**
- [ ] Plugin `flutter-forge` en la versión 0.7.0 o superior (registra `phase_log`, `gates.*.changed`,
      `retries` y `baseline_estimate_hours`). Anotar la versión usada.
- [ ] Proyecto Flutter con `.flutter-forge/profile.yaml` (UNITED u otro) y la misma rama base en
      todas las corridas.
- [ ] Una **HU fija** con huecos conocidos; escribir la lista de huecos plantados **antes** de
      correr, para medir cuántos detecta el agente.
- [ ] Un mismo modelo y esfuerzo en las 5 corridas de implementación. Cambiarlos es objeto de BIT-009.
- [ ] `baseline_estimate_hours` definido **antes** de la primera corrida, igual en todas, con quién
      lo estimó y cómo. Para auditorías, la estimación manual equivalente.
- [ ] Un cronómetro para el tiempo humano de revisión y retrabajo por corrida (`--review-hours`).
- [ ] Tarifa horaria que usará quien lea el informe (no se asume ninguna).

**Pasos por corrida de implementación (5, tipo `deliver`)**
1. Slug nuevo y distinto (`base-01` … `base-05`), sesiones nuevas, sin trabajo ajeno en medio.
2. `/flutter-forge:forge-deliver` con la HU fija; responder los gates normalmente.
3. Cronometrar la revisión y corrección humana de lo entregado.
4. Cerrar **todas** las sesiones de la corrida (el costo oficial solo existe al cerrarlas).
5. En sesión nueva: `/flutter-forge:forge-metrics base-0N --review-hours <h>`; confirmar las
   sesiones `linked` y `adjacent` con `--include` o `--exclude`.
6. Revisar que el resultado sea `complete`, no `INCOMPLETE`, y sin advertencias de `phase_log`.

**Pasos por auditoría (2, tipo `review` o `health`)**
1. Misma entrada para ambas (mismo repo y mismo commit) con `flutter-reviewer` o `forge-health`.
2. Cerrar la sesión; medir con `--session <id> --id audit-0N --review-hours <h> --write`.
3. Registrar los hallazgos aceptados y rechazados. `--review-hours` es el tiempo humano de leer la
   salida y decidir qué se acepta. Con `--session` el script no lee `baseline_estimate_hours`
   (sale de `state.json`, que una auditoría no tiene), así que el ahorro de una auditoría no sale
   calculado: se compara a mano con la estimación manual previa, o se omite.
4. Las 2 auditorías son independientes de las 5 corridas (la corrida ya incluye su propia fase de
   revisión). Se recomienda una de cada tipo; ninguna llega a 5, así que se reportan como anécdota.

**Estrategia acordada (2026-11-18): repetir `simulador-inversion` desde un punto anterior**

Donde difiera de los pasos genéricos de arriba, manda esta sección. Los hashes son los de
`git log` de UnitedApp al 2026-11-18; confirmarlos antes de usarlos: la implementación original es
`f9d5ba0` (feat) con `5d5229c` (chore E2E), y su padre `0ef68b5` es el último commit anterior.

*Decisiones*
- **Perfil sí, brief no.** El perfil (`forge-profile`) es preparación única y no es costo de la
  feature: se genera una vez y se confirma en el commit base. El **brief se genera en cada
  corrida** a partir de la HU, porque la fase de requisitos y el Gate 1 son parte de lo que se
  mide, y la estimación `baseline_estimate_hours` (HU → listo para merge) también los incluye.
  Si se commitea un brief ya hecho y las corridas parten del diseño, se mide menos que lo que
  cubre la estimación y el ahorro sale inflado. Esa variante solo vale como estudio aparte, con
  `phases` acotadas y una estimación que también excluya requisitos.
- **Un solo directorio de trabajo** para todas las mediciones (`UnitedApp-baseline`, un worktree
  o clon de UnitedApp), no tu copia de trabajo (tiene cambios sin commitear) ni un worktree por
  corrida. El script busca los transcripts por la ruta del proyecto y guarda `history.jsonl` dentro
  de él: con rutas distintas, `--summary` no agruparía las corridas. `.flutter-forge/metrics/` se
  ignora por git y por eso sobrevive al cambiar de rama.
- **Las auditorías no dependen de las corridas.** Se hacen en el mismo directorio y antes de las
  corridas: son cortas, no dejan nada en el commit base y sirven de ensayo del procedimiento de
  medición (cerrar sesiones, `--session`, `--include/--exclude`) antes de gastar en las cinco.

*Pasos*
0. **Preparar el directorio.** Crear `UnitedApp-baseline` desde un checkout limpio de `0ef68b5`;
   `flutter pub get`, generación de código y lo que pida el proyecto. Dejar fuera la rama de la
   implementación original (sin remoto ni ramas locales que la contengan) para que el agente no
   la lea en el historial; el diff de la auditoría `review` se obtiene antes y se guarda aparte.
1. **Commit base `B`.** Rama `baseline/base` desde `0ef68b5`. Ejecutar `forge-profile`, revisar el
   perfil, commitear `.flutter-forge/profile.yaml` y `layers.json` y la HU fuente (`hu.md` o
   la fuente que use el proyecto). Es lo único que se agrega. Anotar el hash de `B`, la versión del
   plugin, el modelo y el esfuerzo. Todas las corridas parten de `B`.
2. **Fijar la estimación.** Con la definición de `baseline_estimate_hours` de arriba, sin mirar la
   corrida original, escribirla junto con la persona que la estimó y la fecha en la hoja de
   entregables y en un archivo de texto para responder siempre igual cuando `forge-deliver` la pida.
3. **Preparar respuestas fijas a los gates.** Escribir una sola vez qué responderás en los gates
   de la HU (huecos plantados, decisiones) y reutilizarlas. Reduce la variación y el efecto de
   aprendizaje; anotar que el tiempo de revisión es el de alguien que ya conoce el caso.
4. **Auditoría `health`.** En `B` (checkout de `baseline/base`), en sesión propia con
   `forge-health`; cerrar la sesión; `/flutter-forge:forge-metrics --session <id> --id audit-health
   --review-hours <h>`. Descartar lo que escriba en el árbol (`git clean`/`reset`): `B` no cambia.
5. **Auditoría `review`.** Checkout de `f9d5ba0` (con `5d5229c` si se quiere el E2E) y revisar el
   diff `0ef68b5..f9d5ba0` con `flutter-reviewer`; cerrar; medir con `--id audit-review`. Volver a
   `B` y limpiar.
6. **Corridas `base-01` … `base-05`**, una por una:
   1. `git switch -C run/base-0N baseline/base` (árbol limpio, desde `B`).
   2. Sesión nueva; `/flutter-forge:forge-deliver` con la HU y el slug `base-0N`. Responder los
      gates con las respuestas fijas y la misma estimación.
   3. Decidir una vez y mantener en las cinco si se corre el E2E (necesita dispositivo y
      credenciales; si no, queda `pending-run` en todas).
   4. Cronometrar la revisión y las correcciones humanas, y los gates.
   5. Cerrar **todas** las sesiones de la corrida.
   6. **Antes de cambiar de rama**, en sesión nueva: `/flutter-forge:forge-metrics base-0N
      --review-hours <h>` (necesita `.flutter-forge/runs/base-0N` presente). Confirmar sesiones
      `linked` y `adjacent`. Debe quedar `complete` y sin advertencias de `phase_log`.
   7. Commitear en `run/base-0N` la carpeta de la corrida y el código, para conservar la evidencia.
7. **Resumen.** `/flutter-forge:forge-metrics --summary` en `UnitedApp-baseline`: debe mostrar
   `deliver` con 5 corridas completas, y `review` y `health` con 1 cada una. Pasar a la hoja de
   entregables y escribir el informe de `docs/`.

*Riesgos de esta estrategia*
- **Contaminación:** historial de git, memoria de Claude Code del proyecto o `forge-learn`
  arrastrando datos de una corrida a la siguiente. Revisar antes de la corrida 2 que `B` y
  `.flutter-forge/` estén idénticos al inicio.
- **Medición tardía:** cambiar de rama sin medir pierde `state.json`/`result.json` (si no se
  commitearon) y deja la corrida sin outcome.
- **Una sola tarea:** la mediana describe esta feature, no todas. Complementar con features reales.

**Resultados esperados**
- 5 corridas `complete` de tipo deliver y 2 de auditoría, cada una con `baseline_estimate_hours` y
  `review_hours`, sin sesiones por confirmar.
- Por tipo: mediana y rango de costo (a precios de API), minutos activos y de modelo, costo por AC,
  tasa de aceptación de hallazgos, reintentos y gates cambiados; fase más cara y su variación.
- Ahorro por corrida = `baseline − (activo + revisión + retrabajo)` y su mediana y rango; costo por
  feature = costo a precios de API + horas humanas × tarifa.
- Huecos de la HU detectados frente a plantados.
- Lectura honesta: qué varía entre corridas (si el rango es muy amplio, la mediana dice poco).

**Entregables**
- `.flutter-forge/metrics/` con los `<id>.json`, `<id>.md` y `history.jsonl` de las 7 mediciones
  (solo contadores; se pueden compartir sin texto de la conversación).
- Salida de `run_metrics.py --summary` y la tabla de mediana y rango por tipo.
- Hoja con: HU usada, huecos plantados, `baseline_estimate_hours` y quién lo estimó, `--review-hours`
  de cada corrida, tarifa y versiones (plugin, modelo).
- Informe corto en `docs/` con la tabla, el ahorro calculado y los límites; entrada en `CHANGELOG`
  si cambia algo de la skill.
- Cierre de BIT-010 y datos de entrada para BIT-009.

**Criterio de cierre**
Los 7 resultados completos y el informe publicado. Si no se alcanzan 5 corridas del tipo, se
reporta como anécdota y la entrada sigue abierta. Cada feature real entregada con 0.7.0 y medida
cuenta como una corrida más.

**Notas**
- Una corrida no prueba nada; separar casos fáciles de difíciles.
- No hay que repetir las corridas por la línea base: si el trabajo es real, mide cada feature normal.
- La corrida de UnitedApp (`simulador-inversion`) no cuenta: es anterior a `phase_log` y sin estimación previa.
