# DTO rules

| Contract says | DTO field | Mapper |
|---|---|---|
| `string` | `String` | — |
| `string?` (null in some examples) or `[may be absent]` | `String?` | `?? ''` or keep nullable in entity if the UI distinguishes "none" |
| `int` | `int` | — |
| `double`, or `num` (int and double seen), or money of any kind | `num` | `.toDouble()` (or `Decimal.parse(value.toString())` when the profile uses a decimal type) |
| `string (date-time)` / `(date)` | `String` | `DateTime.parse(x).toLocal()`; keep UTC if the entity documents it |
| `string (numeric-string)` (e.g. `"1500.00"`) | `String` | `double.parse` / decimal in mapper; never in the UI |
| enum-like string | `String?` | map to a Dart enum with an `other`/`unknown` fallback |
| object | its own `@JsonSerializable` class (same file if only used here) | nested `toEntity()` |
| `list<object>` | `List<XDto>` | `.map(...).toList(growable: false)` |
| `list<unknown>` (empty in every example) | **gap**; ask for a sample; until then `List<Object?>` and no UI use | — |
| `mixed(int|string)` | **gap**; ask backend; until then `Object?` + defensive mapper | — |
| envelope `{data: …}` shared by many endpoints | `DataEnvelopeDto<T>` with `genericArgumentFactories: true` or a per-endpoint wrapper | unwrap in mapper |

## Naming and generation

- Class: `<Name>Dto`, `<Name>RequestDto`. File: `<name>_dto.dart`. Generated part: `<name>_dto.g.dart`.
- Use `fieldRename: FieldRename.snake` when the API is snake_case. Use `@JsonKey(name: …)`
  only for exceptions.
- Use `createToJson: false` on response DTOs and `includeIfNull: false` on request DTOs.
- With `serialization.codegen: freezed`, write `@freezed abstract class XDto with _$XDto`
  plus a `fromJson` factory, and keep the same field rules.
- With `manual`, write `fromJson` by hand with explicit casts (`json['amount'] as num`) and
  never `dynamic` fields.
- Run `serialization.build_command` after any change. Never edit generated files.

## Verify with fixtures

For each fixture written by `forge-api-contract`, `forge-tests` adds a mapper test that does
`XDto.fromJson(jsonDecode(fixture))`. If a DTO can't parse a real example, the DTO is wrong,
not the fixture.
