---
max_turns: 12
allowed_tools: [Read, Glob, Grep]
---

Estoy tomando un repo Flutter que no escribí y no tiene perfil de flutter-forge. Ya corrió el
snapshot de forge-health en profundidad `standard` y este es el digest (resumido). Redacta la
sección "Arquitectura: real versus declarada" y la lista de archivos que abrirías, siguiendo las
reglas de `forge-health` (`plugins/flutter-forge/skills/forge-health/SKILL.md`).
No edites nada; responde en el chat.

```
Stack: state=provider (declared: getx, provider) di=get_it router=- http=dio
Architecture guess: layered (confidence high) · features: auth, invest, piggy_bank
Layer map: INFERRED draft .flutter-forge/health/layers.draft.json (presets classify {'clean': 0.03, 'layered': 0.28}; draft classifies 0.99 of 603 files; unmapped: lib/core/services (2), lib/services (2), lib/core (1))
Profile: none in repo; draft .flutter-forge/health/profile.draft.yaml (60 lines, mode: unset: human decision)
Declared: profile=none · docs=CLAUDE.md:provider, CLAUDE.md:getx, CLAUDE.md:get_it
DRIFT: several state packages declared: getx, provider
Rules: inferred draft · files=603 unclassified=6 violations=117
  core_ui 58 files, 31 violations · presentation 217 files, 28 violations, 188 commits(90d) · api 39 files, 17 violations
Top violation pairs: core_ui -> composition 23, presentation -> core_storage 17, api -> models 17
Blind spots: lib/core/core.dart (166 imports), lib/services/service_locator.dart (52 imports)
Review queue: [platform critical] android/app/build.gradle · [security high] .env · lib/screens/product_change/provider/product_change_provider.dart (11 commits) · lib/widgets/cards/home_notification_card.dart (6 violations) · lib/core/services/network/dtos/home/dto_home_notifications_mapper.dart (6 commits)
```
