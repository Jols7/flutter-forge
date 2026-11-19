---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

No estamos en una corrida de forge-deliver; solo quiero corregir una pantalla que ya existe. El diseño
cambió y el resultado no coincide. No cambies archivos: dime qué diferencias hay y qué hacer.

Datos del Figma (ya leídos): la columna principal tiene gap 16; su primer bloque tiene gap 24 e incluye
el selector, el importe y la barra de niveles; el importe y la divisa van con gap 8 alineados abajo; el
título "Ganarías" y su importe usan el color `onPrimaryContainer`; las filas del resumen tienen gap 8,
etiqueta `bodySmall` y valor `titleMedium`; la nota tiene borde de 1 px.

Código actual (`lib/screens/simulator/page.dart`):

```dart
Column(
  spacing: 16,
  children: [
    CurrencySelector(...),
    const SizedBox(height: 8),
    AmountSection(),          // importe + divisa con SizedBox(width: 4), centrados
    LevelProgressBar(...),
    Text(l10n.youEarn, style: textTheme.bodySmall!.copyWith(color: AppColors.onSurfaceVariant)),
    Text(total, style: textTheme.headlineSmall!.copyWith(color: AppColors.primary)),
    for (final row in rows) Row(children: [Expanded(child: Text(row.label, style: textTheme.bodyMedium)),
                                           Text(row.value, style: textTheme.titleSmall)]),
    CommonContainer(hasBorder: false, child: Note()),
  ],
)
```

Usa flutter-forge (forge-figma, modo delta).
