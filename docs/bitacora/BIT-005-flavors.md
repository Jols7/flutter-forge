# BIT-005 · Flavors (entornos y variantes de build)

> [Índice](../bitacora.md) · [Convenciones](../bitacora.md#convenciones) · **Relacionadas:** [BIT-002](BIT-002-estrategia-de-pruebas.md), [BIT-003](BIT-003-secrets-de-github.md), [BIT-006](BIT-006-inyeccion-de-dependencias.md)

- **Tipo:** auditoría, revisión, aprendizaje · **Estado:** pendiente · **Alta:** 2026-11-14
- **Dónde mirar:** skill `flutter-build-release` (flavors dev/qa/prod y entrypoints),
  `forge-profile` (`detect_project.py`, `profile-schema.md`), `forge-architecture/references/core-bootstrap.md`,
  `forge-security/SKILL.md`, `SECURITY.md`

**Qué quiero saber / hacer**
- [ ] Cómo están configurados hoy: Android (`productFlavors`), iOS (schemes, xcconfig,
      build configurations), entrypoints (`main_dev.dart`, etc.), `--dart-define` o
      `--dart-define-from-file`, y cómo los detecta y modela el profile.
- [ ] Auditar la estructura: nombres consistentes entre plataformas, applicationId/bundle id
      por entorno, iconos y nombre de app por flavor, Firebase/google-services por flavor,
      firmas, y que el código no ramifique por flavor fuera del bootstrap.
- [ ] Contrastar con la documentación oficial de Flutter (flavors Android/iOS, `--flavor`,
      `--dart-define`) y con proyectos grandes existentes (open source y guías de referencia).
- [ ] Alcances y limitaciones: qué resuelven (identidad, config, endpoints, servicios) y qué
      no (no aíslan datos en runtime por sí solos, soporte desigual en web/desktop,
      sincronizar Android e iOS a mano, tiempos de build).
- [ ] Usos prácticos y configuraciones necesarias por caso (dev/qa/prod, white-label,
      instalación en paralelo, canales de distribución).
- [ ] **Cuándo usarlos y cuándo no:** criterios de decisión (p. ej. solo `--dart-define`
      si basta cambiar endpoints; flavors completos si cambian id, firma, servicios o
      branding) y costo de mantenerlos.
- [ ] **Riesgos:** compilar o publicar el entorno equivocado, secretos o claves de prod en
      artefactos dev, divergencia entre plataformas, configuraciones sin probar en CI,
      deriva de configuración; definir mitigaciones y checks automáticos.

**Notas**
- Relacionado con BIT-002 (tests por entorno) y BIT-003 (secrets por entorno en CI).
