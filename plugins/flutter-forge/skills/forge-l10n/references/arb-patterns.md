# ARB patterns

These patterns work for both gen-l10n and intl_utils. Only the accessor and the generate
command differ.

```json
{
  "@@locale": "es",

  "transferTitle": "Transferir",
  "@transferTitle": { "description": "Title of the new transfer screen" },

  "transferSent": "Enviaste {amount} a {name}",
  "@transferSent": {
    "description": "Confirmation after a successful transfer",
    "placeholders": {
      "amount": { "type": "String", "example": "$500.00" },
      "name": { "type": "String", "example": "Ahorro" }
    }
  },

  "transactionsCount": "{count, plural, =0{Sin movimientos} =1{1 movimiento} other{{count} movimientos}}",
  "@transactionsCount": { "placeholders": { "count": { "type": "int" } } },

  "accountType": "{type, select, checking{Cuenta de cheques} savings{Cuenta de ahorro} other{Cuenta}}",
  "@accountType": { "placeholders": { "type": { "type": "String" } } },

  "transferMinAmountError": "Ingresa un monto mayor a {minimum}",
  "@transferMinAmountError": { "placeholders": { "minimum": { "type": "String" } } }
}
```

## Formatting in Dart (`core/utils/formatters.dart`)

```dart
String formatMoney(double amount, {required String currency, required String locale}) =>
    NumberFormat.simpleCurrency(locale: locale, name: currency).format(amount);

String formatDate(DateTime date, {required String locale}) => DateFormat.yMMMd(locale).format(date);
```

The locale comes from `Localizations.localeOf(context).toString()`. Never hardcode it in a
formatter.

## Descriptions

Give every key a `description` in the template ARB. Translators and reviewers need context:
"button", "error under the amount field", "screen title".
