# Bitácora de mejoras, revisiones, actualizaciones y auditorías

Registro vivo de puntos que quiero investigar, revisar o aprender a fondo. Se va ampliando
conforme aparezcan nuevos temas. No sustituye a los ADR (`docs/adr/`): una entrada madura
aquí y, cuando se decide algo, pasa a ADR + `CHANGELOG`.

**Estados:** `pendiente` · `en curso` · `hecho` · `descartado`
**Tipos:** `mejora` · `revisión` · `actualización` · `auditoría` · `aprendizaje`

## Índice

| ID | Tema | Tipo | Estado | Alta |
|---|---|---|---|---|
| BIT-001 | Localización (l10n): configuración, optimización y comparación con UNITED | auditoría, mejora | pendiente | 2026-11-14 |
| BIT-002 | Estrategia de pruebas: unit, widget, integration_test y Patrol (+ Patrol en CI) | auditoría, mejora | pendiente | 2026-11-14 |
| BIT-003 | Secrets de GitHub | revisión | pendiente | 2026-11-14 |
| BIT-004 | Nuevas skills de refuerzo: `forge-health` y `forge-upgrade` | mejora | en progreso (`forge-health` implementada; `forge-upgrade` pendiente) | 2026-11-14 |
| BIT-005 | Flavors: configuración, auditoría, alcances, límites y riesgos | auditoría, aprendizaje | pendiente | 2026-11-14 |
| BIT-006 | Inyección de dependencias: implementación, origen, distribución y comparación con UNITED | auditoría, mejora | pendiente | 2026-11-14 |
| BIT-007 | API client: consumo de endpoints, repositorios, errores e interceptores | auditoría, mejora | pendiente | 2026-11-14 |

---

## BIT-001 · Localización (l10n)

- **Tipo:** auditoría, mejora, aprendizaje · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** `plugins/flutter-forge/skills/forge-l10n/` (`SKILL.md`,
  `references/pipelines.md`, `references/arb-patterns.md`)

**Qué quiero saber / hacer**
- [ ] Cómo se está configurando hoy (`l10n.yaml`, ARB, generación, pipelines soportados).
- [ ] Cómo funciona de punta a punta: de la cadena fija en UI a la clave ARB, y cómo la
      detectan `forge-presentation` y `forge-audit`.
- [ ] Posibles optimizaciones (plurales/select, placeholders tipados, claves por feature,
      cadenas huérfanas o duplicadas, tiempo de generación).
- [ ] Auditoría: cobertura de cadenas fijas, claves sin traducir, consistencia entre locales.
- [ ] **Comparar con la implementación actual de UNITED** (qué hace mejor cada una y qué
      conviene adoptar).

**Notas**
- Nota: el tema está escrito como "i10n" en la solicitud; el nombre correcto es
  l10n (localization). Buscar con ese nombre.
- Pendiente de ubicar el código de UNITED para la comparación.

---

## BIT-002 · Estrategia de pruebas: unit, widget, integration_test y Patrol

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

**Notas**
- Se escribió "test_integration" y "test_unit"; se asumen `integration_test` y `test/` (unit).
- Relacionado con B3 de `Curriculum/07_estudio-agente/04-brechas-y-diferenciador.md`
  (Patrol en CI y evals para `forge-tests` / `forge-e2e`).

---

## BIT-003 · Secrets de GitHub

- **Tipo:** revisión · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** Settings → Secrets and variables del repositorio, workflows en
  `.github/workflows/`, `SECURITY.md`

**Qué quiero saber / hacer**
- [ ] Inventario de los secrets y variables existentes (repositorio, entorno, organización).
- [ ] Verificar cuáles usa realmente cada workflow y eliminar los que no se usen.
- [ ] Revisar alcance y permisos (`permissions:` por job, tokens mínimos, entornos con
      aprobación, exposición en ramas de forks y PR).
- [ ] Definir rotación y responsables; confirmar que ninguno aparece en logs ni en el repo
      (apoyarse en `forge-security/scripts/scan_secrets.py`).
- [ ] Decidir qué secrets harán falta para Patrol en CI (BIT-002).

---

## BIT-004 · Nuevas skills de refuerzo: `forge-health` y `forge-upgrade`

- **Tipo:** mejora · **Estado:** pendiente · **Alta:** 2026-11-14
- **Fuente:** `Curriculum/07_estudio-agente/04-brechas-y-diferenciador.md`
  (`/Users/joel/Documents/Curriculum/07_estudio-agente/04-brechas-y-diferenciador.md`)
- Nota: en la solicitud aparece como "flutter-healt" y "flutter-upgrade"; se nombran como
  el resto de skills del plugin (`forge-*`), acorde con el documento de brechas.

**`forge-health` (brecha B1, ⭐ objetivo principal)**
- Auditoría de proyecto completo y línea base de un repo ajeno → `health-report.md`.
- Arquitectura real vs. declarada y deuda por capa; hallazgos de seguridad, rendimiento,
  pruebas (zonas calientes sin cobertura con `git log`) y dependencias obsoletas.
- Backlog priorizado (riesgo × frecuencia de cambio × esfuerzo), quick wins vs. apuestas
  grandes, ruta de migración incremental (`adopt/improve/migrate`) y sección de decisiones
  que necesitan un humano.
- Prueba pública: correrlo sobre 1–2 repos Flutter open source y publicar informe y falsos
  positivos.
- Esfuerzo estimado: medio-alto.

**`forge-upgrade` (brecha B2)**
- Inventario de breaking changes, plan por etapas, `pub outdated` con riesgo, migración de
  APIs depreciadas, verificación (analyze + tests + build por flavor) y rollback.
- Alimenta al agente con la experiencia real de migración 3.13.8 → 3.35.
- Esfuerzo estimado: medio.

**Criterio de cierre** (del documento): cada brecha cerrada = una skill + un eval + un ADR
corto + una entrada en `CHANGELOG`. Sin eval no cuenta como capacidad.

**Avance (2026-11-16)**
- [x] `forge-health` implementada en `plugins/flutter-forge/skills/forge-health/` (scripts,
      referencias, tests, eval `health-baseline-hotspots`, ADR 0005, CHANGELOG 0.5.0).
- [x] Profundidad `standard` (ADR 0006): `infer_layers.py`, `draft_profile.py` y cola de revisión de 30 archivos.
- [ ] Re-correr sobre UNITED para medir cobertura de capas, archivos leídos y costo (`standard` vs `quick`).
- [ ] Prueba pública: correrla sobre 1–2 repos Flutter open source y publicar informe + falsos positivos.
- [ ] Corrida real de `/flutter-forge:forge-health` (confirmar `${CLAUDE_SKILL_DIR}` y el fork).
- [ ] `forge-upgrade` (B2).

**Pendiente**
- [ ] Decidir el orden (el documento sugiere B1 después de una corrida grabada de
      `forge-deliver` y un eval E2E).
- [ ] Revisar el resto de brechas (B3–B9) y decidir cuáles se anotan aquí.

---

## BIT-005 · Flavors (entornos y variantes de build)

- **Tipo:** auditoría, revisión, aprendizaje · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** skill `flutter-build-release` (flavors dev/qa/prod y entrypoints),
  `forge-profile` (`detect_project.py`, `profile-schema.md`), `forge-architecture/references/core-bootstrap.md`,
  `forge-security/SKILL.md`, `SECURITY.md`

**Qué quiero saber / hacer**
- [ ] Cómo están configurados hoy: Android (`productFlavors`), iOS (schemes, xcconfig,
      build configurations), entrypoints (`main_dev.dart`, etc.), `--dart-define` o
      `--dart-define-from-file`, y cómo los detecta y modela el profile.
- [ ] Auditar la estructura: nombres consistentes entre plataformas, applicationId/bundle id
      por entorno, iconos y nombre de app por flavor, Firebase/google-services por flavor,
      firmas, y que el código no ramifique por flavor fuera del bootstrap.
- [ ] Contrastar con la documentación oficial de Flutter (flavors Android/iOS, `--flavor`,
      `--dart-define`) y con proyectos grandes existentes (open source y guías de referencia).
- [ ] Alcances y limitaciones: qué resuelven (identidad, config, endpoints, servicios) y qué
      no (no aíslan datos en runtime por sí solos, soporte desigual en web/desktop,
      sincronizar Android e iOS a mano, tiempos de build).
- [ ] Usos prácticos y configuraciones necesarias por caso (dev/qa/prod, white-label,
      instalación en paralelo, canales de distribución).
- [ ] **Cuándo usarlos y cuándo no:** criterios de decisión (p. ej. solo `--dart-define`
      si basta cambiar endpoints; flavors completos si cambian id, firma, servicios o
      branding) y costo de mantenerlos.
- [ ] **Riesgos:** compilar o publicar el entorno equivocado, secretos o claves de prod en
      artefactos dev, divergencia entre plataformas, configuraciones sin probar en CI,
      deriva de configuración; definir mitigaciones y checks automáticos.

**Notas**
- Relacionado con BIT-002 (tests por entorno) y BIT-003 (secrets por entorno en CI).

---

## BIT-006 · Inyección de dependencias

- **Tipo:** auditoría, mejora · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** `forge-architecture/references/core-bootstrap.md` y `conventions.md`,
  referencias de DI en `forge-presentation` y `forge-data-layer`, ADR 0004 (comparativa
  de arquitecturas de referencia)

**Qué quiero saber / hacer**
- [ ] Cómo se implementa hoy (paquete usado, registro manual o generado, ciclo de vida de
      singletons, factories y lazy, módulos por feature).
- [ ] De dónde se toma esta estructura (qué referencias oficiales o proyectos la inspiraron
      y qué se adoptó o descartó, ver ADR 0004).
- [ ] Cómo funciona de punta a punta: bootstrap, orden de registro, resolución en
      presentación, reemplazo en tests y por flavor (BIT-005).
- [ ] Cómo se distribuye en el proyecto: qué vive en `core` y qué en cada feature, quién
      registra qué, y si respeta las reglas de capas.
- [ ] Revisar anti-patrones (blocs singleton con estado viejo, service locator usado dentro
      de la lógica de dominio) y proponer mejoras si hacen falta.
- [ ] **Comparar con la implementación actual de UNITED.**

---

## BIT-007 · API client

- **Tipo:** auditoría, mejora · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** skills `forge-data-layer`, `forge-api-contract` (incluye
  `references/mock-interceptor.md` y `sources.md`), ADR 0002 (errores con tipo Result)

**Qué quiero saber / hacer**
- [ ] Cómo se implementa hoy: cliente HTTP, consumo de endpoints, base URL por entorno,
      serialización y mapeo a modelos.
- [ ] De dónde se toma esta estructura y qué se adoptó de referencias externas.
- [ ] Cómo funciona de punta a punta y cómo se conecta con los repositorios (datasource →
      repositorio → dominio).
- [ ] Manejo de errores: traducción de fallos de red y HTTP al tipo de error del dominio,
      reintentos, timeouts, cancelación.
- [ ] Interceptores: autenticación y refresco de token, logging sin datos sensibles,
      mock, cabeceras comunes; orden y responsabilidades.
- [ ] Cómo se distribuye en el proyecto y cómo se registra en la inyección (BIT-006).
- [ ] Revisar y mejorar lo necesario; **comparar con la implementación actual de UNITED.**

**Notas**
- Mismos puntos que BIT-006; se revisan juntos porque el cliente se registra vía DI.

---

## Cómo añadir una entrada

Copiar el bloque de una entrada existente, asignar el siguiente `BIT-NNN`, añadir la fila al
índice y registrar la fecha de alta. Al terminar, cambiar el estado y enlazar el ADR o el
commit que lo cerró.
