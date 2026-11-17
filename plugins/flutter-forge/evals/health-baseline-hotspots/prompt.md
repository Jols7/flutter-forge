---
max_turns: 12
allowed_tools: [Read, Glob, Grep]
---

Estoy tomando un repo Flutter que no escribí. Ya corrió el snapshot de forge-health y este es el
digest (resumido). Arma el backlog priorizado y la ruta de migración siguiendo las reglas de
`forge-health` (`plugins/flutter-forge/skills/forge-health/SKILL.md` y sus `references/`).
No hay perfil de flutter-forge en el repo. No edites nada; responde en el chat.

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
