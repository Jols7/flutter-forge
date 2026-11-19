---
type: llm
weight: 2
---

The review applies forge-presentation `references/structure.md`:
- File names are `snake_case` (`CardsScreen.dart` is wrong) and pages end in `_page.dart` (`cards_page.dart`, `card_detail_page.dart`) with classes `CardsPage`.
- `cards_widgets.dart` holds five widgets: split to one public widget per file (`card_tile.dart`, `card_badge.dart`…), named `XTile`, `XCard`, `XSection`.
- The 610-line file and the 190-line `build()` exceed the limits (250 lines per file, 50 per `build()`); extract widgets by region.
- The `build()` with nested ternaries/ifs has too much logic: move it to the state or a mapper (complexity limit 5).
- `CardsFailure` as a state name is confusing next to `Failure<T>`; rename it to `CardsError`.
- Does not demand accessibility work, and does not decide the test-key convention (that belongs to another entry).
