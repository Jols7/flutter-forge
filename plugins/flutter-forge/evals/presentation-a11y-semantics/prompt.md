---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Revisa este widget de un proyecto Flutter. No cambies nada, solo dime qué encuentras.
Escenario A: el proyecto no pide accesibilidad (`a11y` apagado, valor por defecto del perfil).
Escenario B: el brief de la corrida dice `a11y: on`.
Responde a los dos escenarios por separado.

```dart
class TransactionTile extends StatelessWidget {
  const TransactionTile({super.key, required this.amount, required this.onDelete});
  final double amount;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    return Row(children: [
      const Icon(Icons.arrow_downward, color: Colors.red),
      Text('$amount', style: TextStyle(color: amount < 0 ? Colors.red : Colors.green)),
      IconButton(icon: const Icon(Icons.delete), onPressed: onDelete),
    ]);
  }
}
```
