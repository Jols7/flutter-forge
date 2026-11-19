# BIT-012 · E2E con Patrol: ejecución fiable y testabilidad de los widgets

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-002](BIT-002-estrategia-de-pruebas.md), [BIT-011](BIT-011-forge-presentation-semantica.md), [BIT-013](BIT-013-fidelidad-visual-frente-a-figma.md)

- **Tipo:** auditoría, mejora · **Estado:** pendiente · **Alta:** 2026-11-19
- **Origen:** separada de BIT-002 (2026-11-19), que mezclaba la estrategia general de pruebas con
  dos problemas concretos de Patrol: la ejecución y la testabilidad.
- **Dónde mirar:** `plugins/flutter-forge/skills/forge-e2e/` (`SKILL.md`, `references/`,
  `scripts/`), `forge-presentation/references/page-patterns.md`, `forge-blueprint/`,
  `forge-tests/references/widget-tests.md`, `forge-audit/`

**Parte A · Bucle de selección de dispositivo en la etapa E2E**

- **Origen:** pruebas con `forge-deliver`. En **dos corridas seguidas**, al llegar a la etapa E2E
  con Patrol, la ejecución entra en un bucle: la herramienta pide elegir un dispositivo mostrando
  **3 opciones**, no recibe respuesta y repite el prompt generando logs sin parar hasta que se
  detiene. Es reproducible, no un hecho aislado.
- **Causa probable (por confirmar):** `patrol test` / `flutter test` sin `--device` (`-d`) y con
  varios dispositivos disponibles (p. ej. simulador iOS, emulador Android, macOS/Chrome) pregunta
  por consola. En una ejecución sin TTY o con el agente no hay quién conteste, y el runner lo
  reintenta o queda leyendo stdin.
- **Objetivo:**
  1. Revisar si la skill de Patrol E2E (`forge-e2e`, y `flutter-patrol-flows` en el plugin PGI)
     tiene alguna política para este caso (selección de dispositivo, `--device`, `flutter devices`,
     timeout o corte ante prompts interactivos).
  2. Si no la hay, investigar cómo lo resuelve Patrol y la CLI de Flutter, e implementar la solución.
  3. **Por defecto usar un simulador disponible y ya booteado**, salvo que el usuario indique otro.
- **Posibles soluciones (a evaluar, no excluyentes):**
  - **A. Default determinista (recomendada como base, costo casi cero):** antes de correr, listar
    con `flutter devices --machine` (o `xcrun simctl list devices booted` / `adb devices`), filtrar
    simuladores/emuladores **ya booteados** y pasar siempre `--device <id>` explícito. Orden de
    preferencia sugerido: el indicado por el usuario o el perfil → simulador iOS booteado →
    emulador Android booteado. Nunca invocar Patrol sin `--device`.
  - **B. Un solo dispositivo candidato:** si hay exactamente uno booteado, usarlo sin preguntar.
    Si hay varios, aplicar el orden de A y registrar en el informe cuál se eligió y por qué.
  - **C. Ninguno booteado:** bootear uno (`xcrun simctl boot` del último usado o del definido en el
    perfil) y esperar a `bootstatus`; si no se puede, **detenerse con error claro**, sin bucle.
  - **D. Preguntar al usuario revisor (más seguro cuando hay ambigüedad real):** una sola pregunta
    en la etapa E2E con las opciones detectadas y la elegida por defecto marcada; en modo
    desatendido (orquestador) no preguntar y aplicar A/B/C. Guardar la respuesta en
    `.flutter-forge/profile.yaml` (p. ej. `e2e.device`) para no repetirla en la siguiente corrida.
  - **E. Salvaguardas contra el bucle (obligatorias sea cual sea la elegida):** ejecutar con
    entrada no interactiva (stdin cerrado / sin TTY), con timeout y detección de prompts repetidos
    en el runner (el script que filtra el reporte y corta corridas colgadas debe abortar si ve el
    mismo prompt de selección más de una vez) y con límite de líneas de log.
- **Recomendación inicial:** A + B + C como flujo por defecto, E siempre, y D solo en modo
  interactivo cuando haya más de un candidato o ninguno. Es más barato que preguntar siempre y
  evita el bucle que hoy consume tiempo y tokens.
- **Criterio de hecho:** la skill documenta la política; el runner nunca invoca Patrol sin
  `--device`; un eval cubre los casos 0, 1 y 3 dispositivos y confirma que no hay bucle.

**Parte B · Keys en los widgets para escribir y ejecutar pruebas con Patrol**

- **Origen:** petición del 2026-11-19: revisar las keys de los widgets para facilitar la escritura
  y ejecución de pruebas con Patrol, y ver si el problema es de `forge-presentation` y si hace
  falta una convención específica.
- **Qué hay hoy (revisión de solo lectura):**
  - `forge-presentation` **no tiene convención de keys para pruebas**. Solo menciona
    `ValueKey(item.id)` para ítems de lista reordenables (`references/page-patterns.md:109`).
  - `forge-e2e/SKILL.md:61-68` y `forge-tests/references/widget-tests.md:63` dicen "añadir
    `Key('<pantalla>_<elemento>')` solo si el finder es ambiguo y mencionarlo en el informe". Es
    **reactivo**: la fase E2E acaba editando widgets de producción ya auditados, y cada corrida
    inventa sus nombres.
  - Los ejemplos de Patrol (`forge-e2e/references/flow-test-format.md:27-33`) usan
    `$(#transfer_amount)`, es decir, dan por hecho que la key existe; nadie en el pipeline se
    compromete a crearla. Los dos formatos de nombre citados (`<pantalla>_<elemento>` y
    `transfer_submit`) tampoco coinciden del todo.
- **¿Es un problema de `forge-presentation`?** En parte. Es la skill que **produce** los widgets,
  así que debe **aplicar** la convención, pero la causa está aguas arriba: nadie **declara** qué
  elementos son testeables. Mismo patrón que la semántica en BIT-011 (el blueprint no tiene
  columna de semántica; tampoco de keys).
- **Propuesta de convención (a validar):**
  - Una sola fuente de verdad (p. ej. `forge-architecture/references/conventions.md`) y las demás
    skills la enlazan, sin repetir umbrales.
  - **Qué lleva key:** elementos con los que el flujo interactúa o que prueba (botones de acción,
    campos, pestañas, ítems de lista) y el contenedor de cada estado sellado (carga, error,
    vacío, contenido). No todo widget.
  - **Nombre:** `snake_case`, `<pantalla>_<elemento>`; para listas, `<pantalla>_item_<id>`.
    Nunca datos personales ni sensibles en el nombre (relevante para BIT-002 y el MASVS).
  - **Constantes por feature** (`abstract final class TransferKeys { static const submit =
    Key('transfer_submit'); }`) que usan la página, el widget test y el test Patrol: evita
    erratas y hace que renombrar sea seguro. Evitar `GlobalKey` para esto.
  - Valorar `Semantics(identifier: ...)` como complemento para localizar desde el lado nativo
    (verificar versión mínima de Flutter y soporte de Patrol antes de recomendarlo).
- **Dónde tocaría (si se aprueba):** `forge-blueprint` (columna "keys de prueba" por widget
  interactivo), `forge-presentation` (aplicar la convención), `forge-figma` (nombrar según el
  diseño, si ayuda), `forge-e2e` y `forge-tests` (usar las constantes; dejar de crear keys sobre
  la marcha), `forge-audit` (regla: widget interactivo sin key de prueba, severidad baja).
- [ ] Verificar contra la documentación de Patrol cómo resuelve `$(#nombre)` (por `Key`) y qué
      ofrece para finders nativos y por semántica.
- [ ] Decidir la convención de nombres y el lugar de la fuente de verdad.
- [ ] Añadir la columna al blueprint y la regla al audit; actualizar `forge-e2e` y `forge-tests`.
- [ ] Eval: una feature con 2 pantallas y 1 lista; el test Patrol generado no debe añadir keys
      nuevas y debe usar las constantes.
- **Criterio de hecho:** convención documentada una vez; blueprint y presentación la aplican;
  una corrida de `forge-e2e` no modifica código de producción para añadir keys.
- **Relacionado:** BIT-002 (estrategia de pruebas), BIT-011 (semántica y accesibilidad;
  comparten la idea de "declarar en el blueprint") y la Parte A de esta misma entrada.
