---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Tengo esta estructura en la capa de presentación de un feature `cards`. Dime qué cambiarías en
nombres y organización. No cambies nada.

```
lib/features/cards/presentation/
  pages/
    CardsScreen.dart          (610 líneas; build() de 190 líneas con ternarios y ifs anidados)
    card_detail.dart
  widgets/
    cards_widgets.dart        (contiene CardTile, CardBadge, CardActions, CardHeader y CardLimits)
  state/
    cards_cubit.dart          (contiene CardsCubit y CardsFailure, el estado de error)
```
