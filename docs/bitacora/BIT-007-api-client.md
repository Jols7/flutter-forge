# BIT-007 · API client

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-006](BIT-006-inyeccion-de-dependencias.md)

- **Tipo:** auditoría, mejora · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** skills `forge-data-layer`, `forge-api-contract` (incluye
  `references/mock-interceptor.md` y `sources.md`), ADR 0002 (errores con tipo Result)

**Qué quiero saber / hacer**
- [ ] Cómo se implementa hoy: cliente HTTP, consumo de endpoints, base URL por entorno,
      serialización y mapeo a modelos.
- [ ] De dónde se toma esta estructura y qué se adoptó de referencias externas.
- [ ] Cómo funciona de punta a punta y cómo se conecta con los repositorios (datasource →
      repositorio → dominio).
- [ ] Manejo de errores: traducción de fallos de red y HTTP al tipo de error del dominio,
      reintentos, timeouts, cancelación.
- [ ] Interceptores: autenticación y refresco de token, logging sin datos sensibles,
      mock, cabeceras comunes; orden y responsabilidades.
- [ ] Cómo se distribuye en el proyecto y cómo se registra en la inyección (BIT-006).
- [ ] Revisar y mejorar lo necesario; **comparar con la implementación actual de UNITED.**

**Notas**
- Mismos puntos que BIT-006; se revisan juntos porque el cliente se registra vía DI.
