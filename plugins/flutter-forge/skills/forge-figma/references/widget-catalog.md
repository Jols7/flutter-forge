# Widget catalog (one per project)

It lives in the project at `design.widget_catalog` (default `docs/widget-catalog.md`). With it,
the reuse ladder works without reading every widget file on each run.

## Build it when missing

```bash
# shared widgets: files and public widget classes
grep -rn "class [A-Z][A-Za-z0-9]* extends \(StatelessWidget\|StatefulWidget\|ConsumerWidget\|HookWidget\)" <paths.shared_widgets>
grep "^export" <paths.widgets_barrel>       # when a barrel exists
```

Open each widget's constructor and write one row per widget, grouped by folder. Feature-local
widgets are not listed.

## Format

```markdown
# Widget catalog — <project>

## buttons
| Widget | Path | Use it for | Key params | Figma equivalent |
|---|---|---|---|---|
| AppPrimaryButton | lib/core/widgets/buttons/app_primary_button.dart | Main action of a screen | label, onPressed (null = disabled), isLoading | Button · Filled |

## inputs
| Widget | Path | Use it for | Key params | Figma equivalent |
|---|---|---|---|---|
| AppAmountField | lib/core/widgets/inputs/app_amount_field.dart | Money input with currency prefix | controller, currency, errorText, onChanged | Text field · Amount |
```

## Keep it current

- Every widget created in the shared folder gets a row in the same change.
- When a widget gains an optional parameter, update its "Key params".
- Fill "Figma equivalent" the first time a component is matched. If the team adopts Figma
  Code Connect, these pairs are the mappings to publish.
