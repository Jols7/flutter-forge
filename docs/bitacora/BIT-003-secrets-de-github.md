# BIT-003 · Secrets de GitHub

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-002](BIT-002-estrategia-de-pruebas.md), [BIT-005](BIT-005-flavors.md)

- **Tipo:** revisión · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** Settings → Secrets and variables del repositorio, workflows en
  `.github/workflows/`, `SECURITY.md`

**Qué quiero saber / hacer**
- [ ] Inventario de los secrets y variables existentes (repositorio, entorno, organización).
- [ ] Verificar cuáles usa realmente cada workflow y eliminar los que no se usen.
- [ ] Revisar alcance y permisos (`permissions:` por job, tokens mínimos, entornos con
      aprobación, exposición en ramas de forks y PR).
- [ ] Definir rotación y responsables; confirmar que ninguno aparece en logs ni en el repo
      (apoyarse en `forge-security/scripts/scan_secrets.py`).
- [ ] Decidir qué secrets harán falta para Patrol en CI (BIT-002).
