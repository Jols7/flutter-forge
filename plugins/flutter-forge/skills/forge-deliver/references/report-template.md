# `report.md` template

Write it in `requirements.language`. Example headings are shown in Spanish.

```markdown
# Reporte — <Feature> · run <slug> · YYYY-MM-DD
Estado: completed | completed-with-gaps | failing-tests | blocked · Modo: interactive · Preset: clean/bloc

## Resumen
2–4 líneas: qué se entregó, cómo se probó, veredicto de la revisión, qué falta.

## Trazabilidad (AC → código → prueba)
| AC | Implementación | Prueba | Estado |
|---|---|---|---|
| AC-1 | account_detail_page.dart · botón "Transferir" | transfer_test.dart (E2E) paso 1 | ✅ |
| AC-4 | transfer_cubit.dart · submit → BusinessFailure | transfer_cubit_test.dart "AC-4…" | ✅ |
| AC-6 | — | — | ⏳ gap G-2 |

## Archivos
Creados (n) · Modificados (m) — lista agrupada por capa, con rutas.

## Diseño
Componentes reutilizados / extendidos / creados · tokens sin equivalente.

## Contrato
Endpoints (real / mock-agreed) · **Rutas mockeadas:** `POST transfers` (quitar cuando exista).

## Pruebas
Unit: 24 ✅ · Widget: 9 ✅ · E2E: transfer_test ✅ (unitDev, iPhone 16) · Cobertura domain+data: 91 %
Comandos ejecutados: …

## Revisión (independiente: sí)
| Severidad | Encontrados | Corregidos | Diferidos |
|---|---|---|---|
| high | 1 | 1 | 0 |
| medium | 3 | 2 | 1 |
Veredicto final: pass-with-notes · Detalle: findings.md

## Por qué
<!-- explain: brief → 1–3 entries; full → every gate decision; none → omit this section -->
- **Sin use case para cargar movimientos.** La llamada solo pasa datos; no hay regla ni reúso.
  Descartado: `GetTransactions` (ceremonia) y llamar al repositorio desde la página (rompe capas).

## Dónde revisar
<!-- the same entries as result.json review_points[]: point · location · reason -->
- Mínimo de 10.00 por transferencia, no por día (R-1 ambigua) —
  `lib/features/transfers/domain/entities/transfer_amount.dart:12`
- Ruta mockeada `POST transfers` hasta que el back la publique — `lib/core/network/mocks/transfers_mocks.dart`

## Pendientes
- Gaps abiertos (G-n) y preguntas.
- Supuestos (modo desatendido).
- Observaciones fuera de alcance (bugs vistos, deuda previa).

## Siguiente paso
Lo que la persona debe decidir: responder G-2, aprobar commit con el mensaje propuesto, …

Commit propuesto: `feat(mobile): add own-account transfers` (con `git: commit|pr`, ver
`git-conventions.md`; aquí van la rama, los commits y la URL del PR).
```
