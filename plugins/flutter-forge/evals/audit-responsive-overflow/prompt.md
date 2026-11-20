---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Revisa este widget como parte de una auditoría (forge-audit). No cambies nada. El proyecto tiene
`a11y` apagado (valor por defecto). Dime qué encuentras y con qué severidad.

```dart
class SummaryRow extends StatelessWidget {
  const SummaryRow({super.key, required this.label, required this.amount});
  final String label;
  final String amount;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    return SizedBox(
      height: 48,
      child: Row(
        children: [
          Expanded(child: Text(label, style: text.bodySmall)),
          Text(amount, style: text.titleMedium),
        ],
      ),
    );
  }
}

class AmountUnderline extends StatelessWidget {
  const AmountUnderline({super.key});
  @override
  Widget build(BuildContext context) => Container(width: 268, height: 1, color: Colors.orange);
}
```
