# BIT-002 · Estrategia de pruebas: unit, widget, integration_test y Patrol

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-003](BIT-003-secrets-de-github.md), [BIT-005](BIT-005-flavors.md), [BIT-011](BIT-011-forge-presentation-semantica.md), [BIT-012](BIT-012-e2e-patrol-dispositivo-y-keys.md), [BIT-013](BIT-013-fidelidad-visual-frente-a-figma.md), [BIT-014](BIT-014-desviacion-justificada-presentacion-frente-a-figma.md)

- **Tipo:** auditoría, mejora · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** skills `forge-tests` y `forge-e2e`, `.github/workflows/ci.yml` y
  `.github/workflows/evals.yml`, `plugins/flutter-forge/tests/`

**Qué quiero saber / hacer**
- [ ] Revisar y auditar la **escritura automática de pruebas** que genera el agente: cómo se
      configura, qué produce y con qué calidad.
- [ ] Validar **criterios de seguridad** de las pruebas (datos de prueba, credenciales,
      secretos en fixtures, qué se ejecuta contra qué entorno).
- [ ] Definir **cuándo usar cada tipo**: unit test, widget test, `integration_test` y Patrol
      (criterio de elección, costo, estabilidad, cobertura que aporta cada uno) y dejarlo
      documentado como guía en la estructura de pruebas.
- [ ] Definir la estructura de carpetas y convenciones de nombres por tipo de prueba.
- [ ] **Configurar Patrol para que corra en CI** (emulador/simulador, tiempos, artefactos,
      reintentos; hoy el E2E no corre en CI).
- [ ] Los puntos de **ejecución fiable de Patrol** (bucle de selección de dispositivo) y de
      **testabilidad de los widgets** (keys para pruebas) salieron a **BIT-012** el 2026-11-19.

**Notas**
- Coordinación con BIT-011 (2026-11-19): los guidelines de accesibilidad de `widget-tests.md`
  (`meetsGuideline`, `ensureSemantics()`, tap targets, texto grande) pasan a ser **condicionales a
  `a11y: on`**; con `off` los tests de widget no los exigen. El cambio lo hace la fase 3 de BIT-011;
  al revisar la estrategia de pruebas aquí, no reintroducirlos como obligatorios.
- Se escribió "test_integration" y "test_unit"; se asumen `integration_test` y `test/` (unit).
- Relacionado con B3 de `Curriculum/07_estudio-agente/04-brechas-y-diferenciador.md`
  (Patrol en CI y evals para `forge-tests` / `forge-e2e`).
- Coordinación con BIT-013 (2026-11-19, ADR 0010): la prueba de **texto grande y tamaños** (matriz
  responsiva de `widget-tests.md`) ya **no depende de `a11y`**; siempre corre. Los guidelines de semántica
  siguen condicionados. Al revisar la estrategia aquí, no volver a atarla al interruptor.
