# Instrucciones para MySQL Workbench

## 📋 Pasos para ejecutar el script SQL

### 1. Abrir MySQL Workbench
- Inicia MySQL Workbench
- Conecta a tu servidor MySQL local o remoto

### 2. Cargar el script
- Ve a **File > Open SQL Script**
- Selecciona el archivo: `servicio_automotriz_completo.sql`
- El script se abrirá en una nueva pestaña

### 3. Revisar el script (IMPORTANTE)
- **Línea 15**: Hay una línea comentada que dice `DROP DATABASE IF EXISTS servicio_automotriz;`
- Si quieres **eliminar la base de datos existente** y empezar desde cero, descomenta esta línea
- Si quieres **mantener los datos existentes**, déjala comentada

### 4. Ejecutar el script
- Opción 1: Presiona **F5** o **Ctrl+Shift+Enter**
- Opción 2: Ve a **Query > Execute (All or Selection)**
- Opción 3: Haz clic en el botón de ejecutar (⚡)

### 5. Verificar la ejecución
- Revisa el panel de resultados en la parte inferior
- Debe mostrar mensajes de éxito para cada tabla creada
- Verifica en el panel izquierdo que la base de datos `servicio_automotriz` existe
- Expande la base de datos y verifica que todas las tablas estén creadas:
  - ✅ roles
  - ✅ usuarios
  - ✅ citas
  - ✅ clientes
  - ✅ cotizaciones
  - ✅ presupuestos
  - ✅ presupuesto_items
  - ✅ servicios

## 🔐 Credenciales por defecto

Después de ejecutar el script, puedes iniciar sesión con:

- **Usuario:** `admin`
- **Contraseña:** `admin123`

⚠️ **IMPORTANTE:** Cambia la contraseña después del primer acceso por seguridad.

## 📊 Estructura de la base de datos

### Tablas principales:

1. **roles** - Roles del sistema (admin, usuario)
2. **usuarios** - Usuarios con acceso al sistema
3. **servicios** - Servicios ofrecidos por el taller
4. **citas** - Citas agendadas
5. **clientes** - Información de clientes
6. **cotizaciones** - Solicitudes de cotización
7. **presupuestos** - Presupuestos generados
8. **presupuesto_items** - Items de cada presupuesto

## 🔧 Solución de problemas

### Error: "Table already exists"
- Si ya existe la base de datos, descomenta la línea `DROP DATABASE IF EXISTS`
- O elimina manualmente las tablas existentes antes de ejecutar

### Error: "Access denied"
- Verifica que tengas permisos de administrador en MySQL
- Asegúrate de estar conectado con un usuario con privilegios suficientes

### Error: "Foreign key constraint fails"
- Ejecuta el script completo desde el principio
- Las tablas deben crearse en el orden correcto (roles antes que usuarios)

## 📝 Notas adicionales

- El script incluye datos de ejemplo (opcional)
- Puedes eliminar los INSERT de ejemplo si no los necesitas
- Todas las tablas usan UTF8MB4 para soportar caracteres especiales
- Las contraseñas están hasheadas con bcrypt (PHP password_hash)

