# `<id>.md` template

Write it in the profile's `requirements.language`. Example headings are in Spanish. Every number
comes from the script's output. Omit a section that has no data, except **Límites**.

```markdown
# Métricas — <id> · YYYY-MM-DD
Tipo: deliver | review | health | skill · Estado: completo | incompleto

## Resumen
2–3 líneas: costo a precios de API, tiempo activo y de modelo, resultado y hallazgo principal.

## Costo
| Modelo | Costo | Salida | Lectura de caché | Escritura de caché |
|---|---|---|---|---|

## Fases (reparto estimado)
| Fase | Costo | % | Llamadas | Tiempo activo | Contexto promedio |
|---|---|---|---|---|---|

## Tiempo
Reloj · activo · modelo · herramientas · preguntas · espera (persona y procesos en segundo plano).

## Resultado
ACs probados · costo por AC · veredicto · hallazgos por estado · tasa de aceptación ·
gates cambiados · reintentos · ahorro (o por qué no se puede calcular).

## Hallazgos
Hasta 5. Cada uno: dato → qué significa → qué cambiar en el próximo run.

## Sesiones
Contadas, y no contadas con su motivo. Para cada sesión dudosa, el `--include` o `--exclude` exacto.

## Límites
Costo a precios de API, no factura. Reparto por fase estimado. Formato de transcripts no
contractual. Una sola corrida no es una línea base.
```
