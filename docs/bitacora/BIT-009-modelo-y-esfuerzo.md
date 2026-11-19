# BIT-009 · Revisión de modelo y esfuerzo por agente y skill

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-008](BIT-008-telemetria-y-metricas.md), [BIT-010](BIT-010-linea-base-forge-metrics.md), [BIT-011](BIT-011-forge-presentation-semantica.md)

- **Tipo:** revisión, mejora · **Estado:** pendiente · **Alta:** 2026-11-17
- **Dónde mirar:** frontmatter de `plugins/flutter-forge/agents/*.md` y de
  `plugins/flutter-forge/skills/*/SKILL.md`, `forge-deliver/SKILL.md` (orquestador),
  `docs/subagent-contract.md`, ADR 0003 (revisión en contexto separado)

**Estado actual (verificado el 2026-11-17)**

| Componente | `model` hoy | Notas |
|---|---|---|
| Agente `flutter-engineer` | `sonnet` | Orquesta todo el pipeline |
| Agente `flutter-reviewer` | `sonnet` | Solo lectura; audit + security |
| Skill `forge-health` | `sonnet` (+ `context: fork`, `disable-model-invocation`) | Auditoría de repo completo |
| Las otras 15 skills (`forge-api-contract`, `-architecture`, `-audit`, `-blueprint`, `-data-layer`, `-deliver`, `-e2e`, `-figma`, `-l10n`, `-learn`, `-presentation`, `-profile`, `-requirements`, `-security`, `-tests`) | sin definir | Heredan el modelo de la sesión: quien las invoque con un modelo caro paga eso |

Ningún componente define `effort`. Cuando una skill corre dentro de un agente, el modelo
efectivo lo manda el agente; cuando se invoca suelta, el de la sesión.

**Qué quiero saber / hacer**
- [ ] Clasificar cada skill por **tipo de trabajo**: mecánico/determinista (scripts + plantillas),
      generación de código con reglas claras, o juicio (planear, revisar, priorizar, decidir).
- [ ] Proponer modelo y esfuerzo por componente, priorizando resultado donde un error cuesta caro
      y ahorrando donde el trabajo es mecánico. Hipótesis inicial a validar, no decisión:

| Componente | Naturaleza | Hipótesis de modelo | Esfuerzo |
|---|---|---|---|
| `forge-profile`, `forge-learn`, `forge-l10n` | detección y plantillas | modelo ligero (haiku) o sonnet | bajo |
| `forge-api-contract`, `forge-figma` | extracción y mapeo | sonnet | bajo–medio |
| `forge-data-layer`, `forge-presentation`, `forge-tests`, `forge-e2e` | generación con reglas | sonnet | medio |
| `forge-requirements`, `forge-blueprint` | interpretar huecos de la HU y planear clases | **evaluar un modelo superior** (un error aquí se propaga a todo el código) | alto |
| `forge-audit`, `forge-security`, agente `flutter-reviewer` | revisión y juicio | **evaluar un modelo superior** (buscan lo que los scanners no ven) | alto |
| `forge-health` | priorización y decisiones humanas | sonnet hoy; medir si un modelo superior mejora el backlog | medio–alto |
| `flutter-engineer` / `forge-deliver` | orquestación larga | sonnet; valorar subir si pierde el hilo entre fases | medio |

- [ ] **¿Subir el modelo de los agentes?** Medir antes de decidir. Un modelo mayor en planeación y
      revisión puede costar más por token pero ahorrar reintentos y retrabajo; hay que
      comprobarlo con datos, no suponerlo.
- [ ] Comparar por configuración, con la misma entrada y las mismas rúbricas: modelo ligero vs.
      sonnet vs. superior, y esfuerzo bajo/medio/alto. Métricas: ¿compila?, ¿pasa analyze y tests?,
      ¿respeta capas?, recall y precisión de hallazgos sobre un repo con defectos sembrados
      (B3), gaps de la HU detectados vs. plantados, reintentos, tokens y minutos.
- [ ] Verificar en la documentación vigente de Claude Code qué campos acepta el frontmatter de
      skills y agentes (`model`, `effort`, alias vs. id completo) y cómo se hereda el modelo
      cuando una skill corre dentro de un agente o en `context: fork`. No asumir.
- [ ] Decidir la política: alias (`sonnet`, `opus`, `haiku`) que siguen la versión vigente vs. id
      fijo que da reproducibilidad. Registrar el costo de que un alias cambie de modelo sin aviso
      (los evals semanales detectarían una regresión).
- [ ] Permitir que el proyecto sobrescriba el modelo (por ejemplo en `profile.yaml` o en el brief
      del orquestador) para quien prefiera ahorrar o priorizar calidad.
- [ ] Reglas de uso: qué fases pueden delegarse a un modelo ligero sin pasar por el gate, y cuáles
      no. El gate humano no debe depender de un modelo débil.
- [ ] Documentar la decisión en un ADR y reflejarla en `CHANGELOG` y `docs/architecture.md`.

**Riesgos**
- Un modelo barato en una fase temprana (requisitos, blueprint) abarata esa fase y encarece las
  siguientes: medir el costo del run completo, no el de cada skill.
- Fijar el modelo en una skill sobrescribe la elección de quien la invoca; dejar sin definir es
  a veces lo correcto para skills que se usan sueltas.
- Un modelo superior en el revisor no sirve si el contexto que recibe es ruido: revisar primero
  que los scanners filtren antes del LLM (principio 5 de `architecture.md`).

**Notas**
- Depende de BIT-008: sin telemetría de tokens, tiempo y tasa de aceptación por run no hay forma
  de justificar el cambio con datos. Hacer primero BIT-008, o al menos su script de métricas.
- Relacionado con B3 (evals con repos sembrados, que dan recall y precisión por configuración).
- Los modelos y precios cambian: la tabla de hipótesis se valida con los vigentes al medir.
