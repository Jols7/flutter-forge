# Finding redundancy

Each check below is a recipe that finds evidence cheaply. Report a finding only when the
duplicate is real, meaning the same responsibility exists twice and not merely similar
syntax.

| Check | How |
|---|---|
| Widget duplicates an existing one | For each new widget in scope, search the catalog (`design.widget_catalog`) and `paths.shared_widgets` for the same role (`grep -rln "class .*Button" lib/core/widgets`). Compare constructor params and visuals |
| Duplicated error handling | `grep -rn "on DioException" lib/features/<f>` → anything outside `guard`/`dio_failure_mapper` is a finding |
| Repeated `try { … } catch (e) { rethrow; }` | `grep -rn -A2 "catch (e)" <scope> | grep -B2 "rethrow"` |
| Copy-pasted mapper/validator logic | Same conversion (dates, money, enum fallback) in 2+ mappers → extract to `core/utils` |
| Second formatter/HTTP client/storage wrapper | `grep -rn "NumberFormat\|DateFormat" <scope>` outside `core/utils`; `grep -rn "Dio(" lib` outside `core/network` |
| Dead code in scope | Files in scope not imported anywhere (`grep -rln "<file stem>.dart" lib test`), exports never used, l10n keys never referenced (`grep -c key lib`) |
| Stale mocks | Mock routes in `core/network/mocks/` whose endpoint is `real` in `contract.md` |
| Parallel models | Two entities for the same concept in different features → move to the owning feature's domain and import it (domain is shareable) |
| Duplicate strings | Same text under two ARB keys (`grep` the template ARB for the value) |

With DCM (`quality.dcm: true`), also run `dcm check-code-duplication lib` (or the version's
equivalent) and `dcm check-unused-files lib`. Cite its output as evidence.
