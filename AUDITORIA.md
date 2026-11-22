# AUDITORÍA — one_store

- Fecha: 2026-11-21
- Alcance: todo el repositorio (Django 3.1.6 / PostgreSQL, PC con Windows en red local).
- Método: se aplicaron **las mismas decisiones** ya tomadas en `jeantren` (2026-10-03) y `base_facturacion` (2026-10-08 / 2026-10-18). Lo propio de este proyecto se decidió en el wizard (§3).
- Regla heredada: no se agregan tests automáticos; las pruebas las hace el usuario manualmente al terminar.
- Verificación hecha: `manage.py check` sin errores, las 4 migraciones nuevas aplican sobre SQLite, y 14 comprobaciones manuales con el cliente de pruebas de Django (acceso anónimo, usuarios, CSRF, reportes PDF, anulación, tasa). **No se probó contra PostgreSQL**: el bloqueo de numeración (`pg_advisory_xact_lock`) y `select_for_update` solo se ejercitan allí.
- Diferencia detectada que **no** es de esta auditoría: `makemigrations --check` reporta cambios pendientes en `CashMovement` (`amount_bs`, `amount_dl`, `tipo`). Ya existía antes; no se generó migración.

## 1. Decisiones portadas de jeantren / base_facturacion

| Decisión previa | Puntos |
|---|---|
| APLICADO | VI-01, VI-02, VI-04, VI-05, VI-07, VI-08, VI-11, VI-12, VI-13, VI-14, VI-15, SEG-01, SEG-02, SEG-03, SEG-06, SEG-08, SEG-11, BP-02, BP-04, BP-05, REN-02, REN-04, BF-08 |
| APLICADO PARCIAL (mismo alcance) | VI-10 (abonos con bloqueo y `Decimal`; sobrepago, montos negativos y `delete` del crédito con `group != 1` quedan como están), BP-01 (`resolve_pdf_uri`), BP-03 (solo cuentas por pagar), BP-06, REN-01 (sin paginación) |
| DESCARTADO | VI-03, VI-06, VI-09, SEG-07, SEG-09, SEG-10, AUT-01, AUT-02 |
| POSPUESTO | BP-07 (squash de migraciones) |
| NO APLICA | REN-03 (gunicorn) |

Despliegue en PC local (como base_facturacion): **SEG-04 y SEG-05 descartados** (riesgos aceptados: `SECRET_KEY` en el código y su historial, `DEBUG=True` por defecto, `ALLOWED_HOSTS=["*"]`, clave de base `master/master`). AUT-03 (respaldos) pospuesto.

## 2. Estado de lo propio de one_store

| Tema | Decisión |
|---|---|
| Tasa del dólar (VI-01) | Aplicado; sin validación adicional de "tasa > 0" (el control queda en REN-04). |
| Reporte de ventas por producto | Corregido (`movements` y `grand_total` se inicializan) más el aviso/registro de error de PDF de BP-05. |
| Logo del presupuesto | Usa la URL del propio servidor (antes apuntaba al sitio de jeantren). |
| `last_debt_date` en cuentas por pagar | Sin arreglo propio; queda a cargo de BP-02. |
| Doble barra en el logo del reporte de ventas | Sin cambio (se dejó como estaba). |
| Foto de usuario vs logo en Datos de empresa | Separados: subir el logo ya no cambia la foto del usuario. |
| Anular venta a crédito con abonos | Sin cambio (igual que en los otros proyectos). |
| Método de pago `pk=1` ("NO APLICA") fijo | DESCARTADO. |
| Permiso del reporte de cuentas por pagar | Cambia de `add_user` a `view_debt`. |
| Margen de ganancias con stock exactamente 5 | Corregido (fallaba toda la lista). |
| Tasa del dólar por venta en reportes | Los reportes de ventas por rango convierten los bolívares con la tasa guardada en cada venta (`Sale.rate`; si una venta antigua no la tiene, usan la de hoy como respaldo). Abonos y movimientos de caja ya usaban sus dólares guardados. Portado de jeantren sin lo de Cashea. |
| Reporte de ventas por productos | Botón "Generar reporte de productos" activado de nuevo en el historial de ventas (estaba comentado). Reporte verificado con varias ventas y decimales; el total vendido ahora lleva `$`. |
| Código muerto | Eliminados `RegisterOperation` (usaba un modelo inexistente) y `LoginFormView2`. Quedan sin tocar: logout por GET y `getStaticUrl()` con `localhost`. |
| Módulo de caja y margen de ganancias (JS) | Escape de HTML aplicado (patrón de SEG-08). |

## 3. Antes de usar lo aplicado

1. **Respaldo de la base** con `pg_dump` antes de migrar.
2. **Migraciones**, en este orden (`python manage.py migrate`): `0335_alter_detsale_quantity`, `0336_sale_cancellation_fields`, `0337_dynamic_date_defaults`, `0338_add_indexes` (mejor sin ventas activas).
3. **Permisos de grupos** en `/interno/` → Grupos (SEG-03): el grupo de vendedores necesita `add_sale` (vender), `change_sale` (anular), `add_cashmovement`, `add_client`, `change_credit`, `add_debt`, `change_debt`, `delete_debt`, `delete_budget` según lo que deba hacer; y `view_debt` para imprimir el reporte de cuentas por pagar.
4. **Usuarios**: solo los superusuarios ven y usan el módulo; un usuario sin grupo no tiene permisos.
5. **CSRF**: toda petición de escritura exige token (lo envía `home.html`). Probar una acción de escritura en cada pantalla.
6. Reiniciar el servicio (`IniciarSistema.vbs`) para cargar el código nuevo.

## 4. Pruebas manuales sugeridas

- **Ventas:** contado y crédito (stock descontado, factura consecutiva), anulación con motivo (stock devuelto una sola vez), stock insuficiente, sin tasa del dólar.
- **Inventario:** cambiar la tasa con ventas en curso (stock intacto), editar un producto solo cambiando precio, entrada de mercancía, intentar stock negativo.
- **Crédito y cuentas por pagar:** abono, eliminar abono (una sola vez), "marcar todo como pagado".
- **Seguridad:** `/panel/ventas/registrar/` sin sesión → login; usuario de ventas sin menú "Usuarios"; crear un cliente llamado `<b>Prueba</b>` (se ve como texto).
- **PDFs y reportes:** factura, reporte de ventas, **reporte por productos** (antes no se generaba), inventario, créditos, cuentas por pagar, presupuesto.
- **Margen de ganancias** con un producto de stock 5.
