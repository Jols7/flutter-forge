# BIT-006 · Inyección de dependencias

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-005](BIT-005-flavors.md), [BIT-007](BIT-007-api-client.md)

- **Tipo:** auditoría, mejora · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** `forge-architecture/references/core-bootstrap.md` y `conventions.md`,
  referencias de DI en `forge-presentation` y `forge-data-layer`, ADR 0004 (comparativa
  de arquitecturas de referencia)

**Qué quiero saber / hacer**
- [ ] Cómo se implementa hoy (paquete usado, registro manual o generado, ciclo de vida de
      singletons, factories y lazy, módulos por feature).
- [ ] De dónde se toma esta estructura (qué referencias oficiales o proyectos la inspiraron
      y qué se adoptó o descartó, ver ADR 0004).
- [ ] Cómo funciona de punta a punta: bootstrap, orden de registro, resolución en
      presentación, reemplazo en tests y por flavor (BIT-005).
- [ ] Cómo se distribuye en el proyecto: qué vive en `core` y qué en cada feature, quién
      registra qué, y si respeta las reglas de capas.
- [ ] Revisar anti-patrones (blocs singleton con estado viejo, service locator usado dentro
      de la lógica de dominio) y proponer mejoras si hacen falta.
- [ ] **Comparar con la implementación actual de UNITED.**
