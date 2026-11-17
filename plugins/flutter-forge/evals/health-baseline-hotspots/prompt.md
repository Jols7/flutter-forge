---
max_turns: 12
allowed_tools: [Read, Glob, Grep]
---

Estoy tomando un repo Flutter que no escribí. Ya corrió el snapshot de forge-health y este es el
digest (resumido). Arma el backlog priorizado y la ruta de migración siguiendo las reglas de
`forge-health`, que van pegadas aquí abajo (la skill es de invocación manual y no se puede leer
desde esta sesión; no busques sus archivos). No hay perfil de flutter-forge en el repo.
No edites nada; responde en el chat.

Reglas de forge-health (resumen de `references/prioritization.md`):
- `prioridad = riesgo × frecuencia ÷ esfuerzo`. Riesgo 1–5 por severidad (+1 si toca dinero,
  credenciales o datos personales). Frecuencia 1–5 por commits en la ventana (1 = sin cambios).
  Esfuerzo S/M/L = 1/2/3.
- "Hacer ya": hallazgos de seguridad o dinero con riesgo ≥ 4, sin importar la frecuencia.
- Quick Wins: esfuerzo S y riesgo × frecuencia ≥ 8. Apuestas Grandes: esfuerzo L y riesgo ×
  frecuencia ≥ 12, cada una con un primer paso reversible y cómo probar que funcionó.
- Frecuencia 1 y riesgo ≤ 3: se deja quieto, con una línea que diga por qué.
- Orden: seguridad y dinero, bugs en rutas principales, pruebas en zonas calientes antes de
  cualquier refactor de esa zona, estructura, estilo. Un refactor y una feature nunca van juntos.
- Modo adopt/improve/migrate: decisión humana; se recomienda uno con evidencia. Sin perfil, el
  análisis es contra un preset asumido y se dice.
- Nunca imprimir valores de secretos: tipo + ubicación + "rotar".
- Secciones: backlog, ruta incremental en fases que terminan en algo desplegable, "Decisiones que
  necesitan un humano" (riesgo 🔴/🟠/🟢) y límites (qué no se midió).

```
Stack: state=bloc (declared: bloc, provider) di=get_it router=go_router http=dio
Declared: profile=none · docs=README.md:clean, README.md:bloc
DRIFT: several state packages declared: bloc, provider
Layers (assumed preset: clean): files=210 unclassified=12 violations=64
  presentation 70 files, 41 violations, 33 commits(90d)
  data         60 files, 18 violations,  9 commits
  domain       25 files,  0 violations,  2 commits
  core_legacy  40 files,  5 violations,  0 commits   (0 commits in 90 days)
Top violating files: lib/features/payments/presentation/pages/pay_page.dart×14, lib/core_legacy/old_helpers.dart×5
Hotspots: lib/features/payments/data/payments_repository_impl.dart 21 commits, 11% covered, single owner
          lib/features/payments/presentation/pages/pay_page.dart 18 commits, 0% covered, build() 310 lines
          lib/core_legacy/old_helpers.dart 0 commits, 0% covered, 900 lines, 5 layer violations
Security scanners: secrets: 1 [critical] github-token lib/config/ci_tokens.dart:3 · platform: 1 [high] cleartext allowed in network_security_config.xml
Dependencies: 2 on `any`, 1 git dependency on a main path, `pub outdated` not run
Coverage: 38.0% lines
```

Entrega: (1) el backlog con la fórmula de prioridad y la separación de Quick Wins y Apuestas Grandes,
(2) la ruta de migración incremental, (3) las decisiones que necesitan un humano.
