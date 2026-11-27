# Bitácora de mejoras, revisiones, actualizaciones y auditorías

Registro vivo de puntos que quiero investigar, revisar o aprender a fondo. Se va ampliando
conforme aparezcan nuevos temas. No sustituye a los ADR (`docs/adr/`): una entrada madura
aquí y, cuando se decide algo, pasa a ADR + `CHANGELOG`.

Cada entrada vive en su propio archivo en [`docs/bitacora/`](bitacora/). Este documento es el
**índice** y las **convenciones generales**; para leer un tema basta abrir su archivo.

## Índice

| ID | Tema | Tipo | Estado | Alta |
|---|---|---|---|---|
| [BIT-001](bitacora/BIT-001-l10n-localizacion.md) | Localización (l10n): configuración, optimización y comparación con UNITED | auditoría, mejora | pendiente | 2026-11-14 |
| [BIT-002](bitacora/BIT-002-estrategia-de-pruebas.md) | Estrategia de pruebas: unit, widget, integration_test y Patrol (+ Patrol en CI) | auditoría, mejora | pendiente | 2026-11-14 |
| [BIT-003](bitacora/BIT-003-secrets-de-github.md) | Secrets de GitHub | revisión | pendiente | 2026-11-14 |
| [BIT-004](bitacora/BIT-004-skills-forge-health-y-upgrade.md) | Nuevas skills de refuerzo: `forge-health` y `forge-upgrade` | mejora | en progreso (`forge-health` hecha; solo `forge-upgrade` pendiente) | 2026-11-14 |
| [BIT-005](bitacora/BIT-005-flavors.md) | Flavors: configuración, auditoría, alcances, límites y riesgos | auditoría, aprendizaje | pendiente | 2026-11-14 |
| [BIT-006](bitacora/BIT-006-inyeccion-de-dependencias.md) | Inyección de dependencias: implementación, origen, distribución y comparación con UNITED | auditoría, mejora | pendiente | 2026-11-14 |
| [BIT-007](bitacora/BIT-007-api-client.md) | API client: consumo de endpoints, repositorios, errores e interceptores | auditoría, mejora | pendiente | 2026-11-14 |
| [BIT-008](bitacora/BIT-008-telemetria-y-metricas.md) | Telemetría y métricas del agente (B4): beneficio, ahorro, costo y tiempo por tipo de corrida | revisión, mejora | cerrada (2026-11-17; la línea base sigue en BIT-010) | 2026-11-17 |
| [BIT-009](bitacora/BIT-009-modelo-y-esfuerzo.md) | Revisión de modelo y esfuerzo por agente y skill (costo vs. calidad) | revisión, mejora | pendiente | 2026-11-17 |
| [BIT-010](bitacora/BIT-010-linea-base-forge-metrics.md) | Línea base de `forge-metrics`: mediana, rango y ahorro con corridas reales | medición | pendiente (se acumula con el uso) | 2026-11-17 |
| [BIT-011](bitacora/BIT-011-forge-presentation-semantica.md) | `forge-presentation`: semántica y accesibilidad (opt-in con `a11y`), política de comentarios y estructura de código | auditoría, mejora | hecho (2026-11-19) | 2026-11-19 |
| [BIT-012](bitacora/BIT-012-e2e-patrol-dispositivo-y-keys.md) | E2E con Patrol: ejecución fiable (selección de dispositivo) y keys en los widgets para pruebas | auditoría, mejora | hecho (2026-11-26; verificado en simulador, 0.9.0) | 2026-11-19 |
| [BIT-013](bitacora/BIT-013-fidelidad-visual-frente-a-figma.md) | Fidelidad visual frente a Figma: diferencias de maquetación, tolerancia y verificación (`forge-figma` → `forge-presentation`) | auditoría, mejora | hecho (2026-11-26; calibración de umbrales abierta) | 2026-11-19 |
| [BIT-014](bitacora/BIT-014-desviacion-justificada-presentacion-frente-a-figma.md) | Desviación justificada del código de presentación frente al diseño (catálogo cerrado, verificación por geometría) | mejora | pendiente (prioridad baja) | 2026-11-19 |

## Convenciones

**Estados:** `pendiente` · `en curso` · `hecho` · `descartado`
**Tipos:** `mejora` · `revisión` · `actualización` · `auditoría` · `aprendizaje` · `medición`
**Prioridad (opcional):** `alta` · `media` · `baja`. Va en la línea de cabecera de la entrada y, si no es media,
entre paréntesis en el estado del índice. Omitida equivale a media.

**Archivos y numeración**
- Un archivo por entrada: `docs/bitacora/BIT-NNN-slug.md` (`slug` en minúsculas, sin acentos,
  guiones). El número es correlativo y **no se reutiliza**, aunque la entrada se descarte.
- El título del archivo es `# BIT-NNN · Tema`. El archivo de referencia es
  [`_plantilla.md`](bitacora/_plantilla.md).
- El nombre del archivo no cambia al cambiar el estado; el estado vive en la entrada y en el índice.

**Relaciones entre entradas**
- Cada entrada abre con una línea `Relacionadas:` con enlaces a las demás BIT con las que
  comparte skills, hallazgos o dependencias. La relación es **bidireccional**: si BIT-A cita a
  BIT-B, BIT-B también enlaza a BIT-A.
- Al **dividir** una entrada, la original deja un puntero a la nueva y la nueva indica su
  `Origen` ("separada de BIT-NNN"). Ejemplo: BIT-002 → BIT-012.
- Las dependencias de orden (p. ej. "hacer primero BIT-008") se escriben también en el cuerpo.

**Cómo añadir una entrada**
1. Copiar `bitacora/_plantilla.md` a `bitacora/BIT-NNN-slug.md` con el siguiente número libre.
2. Rellenar tipo, estado `pendiente`, fecha de alta, origen y "Dónde mirar".
3. Añadir la fila al índice de arriba.
4. Completar `Relacionadas:` y añadir el enlace de vuelta en cada entrada relacionada.

**Mientras la entrada vive**
- Marcar los puntos con `- [ ]` y cerrarlos con `- [x]`; anotar fecha y motivo cuando se cambie
  de alcance, no borrar lo anterior.
- Lo verificado de memoria (citas, versiones, APIs) se marca para comprobarlo en la fase 0.
- Si una entrada pasa de unas 150 líneas, valorar dividirla por tema (como BIT-002 y BIT-012).

**Cierre**
- Cambiar el estado en la entrada **y** en el índice, y enlazar el ADR o el commit que la cerró.
- Si el resultado es una decisión de diseño, crear el ADR en `docs/adr/` y enlazarlo desde la entrada.
- Una entrada cerrada no se borra: sirve de historial y de contexto para las relacionadas.

**Recomendaciones de lectura (para personas y agentes)**
- Para un tema, abrir solo su archivo y seguir los enlaces de `Relacionadas:` si hacen falta.
- No cargar toda la carpeta: el índice basta para elegir.
