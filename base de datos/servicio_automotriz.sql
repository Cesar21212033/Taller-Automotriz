-- ============================================
-- SCRIPT ÚNICO PARA INSTALAR BASE DE DATOS
-- Ejecuta este archivo completo en MySQL Workbench
-- ============================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS servicio_automotriz 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_general_ci;

USE servicio_automotriz;

-- ============================================
-- TABLA: roles
-- ============================================
DROP TABLE IF EXISTS roles;
CREATE TABLE roles (
  id INT(11) NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(50) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_roles_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO roles (nombre, descripcion) VALUES
('admin', 'Administrador del sistema con acceso completo'),
('usuario', 'Usuario regular del sistema');

-- ============================================
-- TABLA: usuarios
-- ============================================
DROP TABLE IF EXISTS usuarios;
CREATE TABLE usuarios (
  id INT(11) NOT NULL AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  password VARCHAR(255) NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(100) DEFAULT NULL,
  telefono VARCHAR(20) DEFAULT NULL,
  rol_id INT(11) NOT NULL DEFAULT 2,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_usuarios_username (username),
  KEY idx_usuarios_rol_id (rol_id),
  CONSTRAINT fk_usuarios_rol FOREIGN KEY (rol_id) 
    REFERENCES roles (id) 
    ON DELETE RESTRICT 
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Usuario: admin / Contraseña: admin123
INSERT INTO usuarios (username, password, nombre, email, rol_id) VALUES
('admin', '$2y$10$FSSCIv/7yBYCcJp92ZtBxuZ5XYTNUaRaFCfg9wM6RLYAFX30ihXKa', 'Administrador', 'admin@taller.com', 1);

-- ============================================
-- TABLA: servicios
-- ============================================
DROP TABLE IF EXISTS servicios;
CREATE TABLE servicios (
  id INT(11) NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO servicios (id, nombre, descripcion) VALUES
(1, 'Cambio de Aceite', 'Cambio de aceite y filtro de aceite'),
(2, 'Reparación de Frenos', 'Reparación y mantenimiento del sistema de frenos'),
(3, 'Diagnóstico Electrónico', 'Diagnóstico computarizado del vehículo'),
(4, 'Alineación y Balanceo', 'Alineación de dirección y balanceo de llantas'),
(5, 'Cambio de Bujías', 'Cambio de bujías y cables'),
(6, 'Cambio de Filtros', 'Cambio de filtros de aire, combustible y cabina');

-- ============================================
-- TABLA: servicio_precios
-- ============================================
DROP TABLE IF EXISTS servicio_precios;
CREATE TABLE servicio_precios (
  id INT(11) NOT NULL AUTO_INCREMENT,
  servicio_id INT(11) NOT NULL,
  cilindros_min INT(2) NOT NULL,
  cilindros_max INT(2) NOT NULL,
  anio_min INT(4) DEFAULT NULL,
  anio_max INT(4) DEFAULT NULL,
  precio_base DECIMAL(10,2) NOT NULL,
  precio_por_cilindro DECIMAL(10,2) DEFAULT 0.00,
  precio_por_anio DECIMAL(10,2) DEFAULT 0.00,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_servicio_precios_servicio (servicio_id),
  KEY idx_servicio_precios_cilindros (cilindros_min, cilindros_max),
  CONSTRAINT fk_servicio_precios_servicio 
    FOREIGN KEY (servicio_id) 
    REFERENCES servicios (id) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO servicio_precios (servicio_id, cilindros_min, cilindros_max, anio_min, anio_max, precio_base, precio_por_cilindro, precio_por_anio) VALUES
(1, 4, 4, 2000, 2010, 200.00, 0, 0), (1, 4, 4, 2011, 2020, 250.00, 0, 0), (1, 4, 4, 2021, 2030, 300.00, 0, 0),
(1, 6, 6, 2000, 2010, 300.00, 0, 0), (1, 6, 6, 2011, 2020, 350.00, 0, 0), (1, 6, 6, 2021, 2030, 400.00, 0, 0),
(1, 8, 8, 2000, 2010, 400.00, 0, 0), (1, 8, 8, 2011, 2020, 500.00, 0, 0), (1, 8, 8, 2021, 2030, 600.00, 0, 0),
(2, 4, 4, NULL, NULL, 800.00, 0, 0), (2, 6, 6, NULL, NULL, 1000.00, 0, 0), (2, 8, 8, NULL, NULL, 1200.00, 0, 0),
(3, 4, 4, NULL, NULL, 500.00, 0, 0), (3, 6, 6, NULL, NULL, 600.00, 0, 0), (3, 8, 8, NULL, NULL, 700.00, 0, 0),
(4, 4, 4, NULL, NULL, 400.00, 0, 0), (4, 6, 6, NULL, NULL, 450.00, 0, 0), (4, 8, 8, NULL, NULL, 500.00, 0, 0),
(5, 4, 4, NULL, NULL, 300.00, 0, 0), (5, 6, 6, NULL, NULL, 450.00, 0, 0), (5, 8, 8, NULL, NULL, 600.00, 0, 0),
(6, 4, 4, NULL, NULL, 350.00, 0, 0), (6, 6, 6, NULL, NULL, 400.00, 0, 0), (6, 8, 8, NULL, NULL, 450.00, 0, 0);

-- ============================================
-- TABLA: marcas_vehiculos
-- ============================================
DROP TABLE IF EXISTS marcas_vehiculos;
CREATE TABLE marcas_vehiculos (
  id INT(11) NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(50) NOT NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_marcas_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- TABLA: años_vehiculos
-- ============================================
DROP TABLE IF EXISTS años_vehiculos;
CREATE TABLE años_vehiculos (
  id INT(11) NOT NULL AUTO_INCREMENT,
  año INT(4) NOT NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  UNIQUE KEY uk_años_año (año)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- TABLA: cotizaciones
-- ============================================
DROP TABLE IF EXISTS cotizaciones;
CREATE TABLE cotizaciones (
  id INT(11) NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  telefono VARCHAR(20) NOT NULL,
  email VARCHAR(100) NOT NULL,
  servicio VARCHAR(100) NOT NULL,
  servicio_id INT(11) DEFAULT NULL,
  marca_vehiculo VARCHAR(50) DEFAULT NULL,
  marca_id INT(11) DEFAULT NULL,
  modelo_vehiculo VARCHAR(50) DEFAULT NULL,
  anio_vehiculo INT(4) DEFAULT NULL,
  año_id INT(11) DEFAULT NULL,
  cilindros INT(2) DEFAULT NULL,
  mensaje TEXT DEFAULT NULL,
  precio_calculado DECIMAL(10,2) DEFAULT NULL,
  fecha_envio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_cotizaciones_servicio (servicio_id),
  KEY idx_cotizaciones_marca (marca_id),
  KEY idx_cotizaciones_año (año_id),
  CONSTRAINT fk_cotizaciones_servicio 
    FOREIGN KEY (servicio_id) 
    REFERENCES servicios (id) 
    ON DELETE SET NULL 
    ON UPDATE CASCADE,
  CONSTRAINT fk_cotizaciones_marca 
    FOREIGN KEY (marca_id) 
    REFERENCES marcas_vehiculos (id) 
    ON DELETE SET NULL 
    ON UPDATE CASCADE,
  CONSTRAINT fk_cotizaciones_año 
    FOREIGN KEY (año_id) 
    REFERENCES años_vehiculos (id) 
    ON DELETE SET NULL 
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- TABLA: citas
-- ============================================
DROP TABLE IF EXISTS citas;
CREATE TABLE citas (
  id INT(11) NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) DEFAULT NULL,
  telefono VARCHAR(20) DEFAULT NULL,
  email VARCHAR(100) DEFAULT NULL,
  fecha DATE DEFAULT NULL,
  hora TIME DEFAULT NULL,
  servicio VARCHAR(100) DEFAULT NULL,
  fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- TABLA: clientes
-- ============================================
DROP TABLE IF EXISTS clientes;
CREATE TABLE clientes (
  id INT(11) NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  telefono VARCHAR(20) DEFAULT NULL,
  correo VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- TABLA: presupuestos
-- ============================================
DROP TABLE IF EXISTS presupuestos;
CREATE TABLE presupuestos (
  id INT(11) NOT NULL AUTO_INCREMENT,
  numero_presupuesto VARCHAR(20) DEFAULT NULL,
  fecha DATE DEFAULT NULL,
  validez VARCHAR(50) DEFAULT NULL,
  cliente_nombre VARCHAR(100) DEFAULT NULL,
  telefono_cliente VARCHAR(20) DEFAULT NULL,
  marca_vehiculo VARCHAR(50) DEFAULT NULL,
  modelo_vehiculo VARCHAR(50) DEFAULT NULL,
  anio_vehiculo VARCHAR(10) DEFAULT NULL,
  kilometraje VARCHAR(20) DEFAULT NULL,
  motor VARCHAR(50) DEFAULT NULL,
  observaciones TEXT DEFAULT NULL,
  subtotal DECIMAL(10,2) DEFAULT NULL,
  total DECIMAL(10,2) DEFAULT NULL,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_presupuestos_numero (numero_presupuesto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- TABLA: presupuesto_items
-- ============================================
DROP TABLE IF EXISTS presupuesto_items;
CREATE TABLE presupuesto_items (
  id INT(11) NOT NULL AUTO_INCREMENT,
  presupuesto_id INT(11) DEFAULT NULL,
  descripcion TEXT DEFAULT NULL,
  cantidad INT(11) DEFAULT 1,
  precio DECIMAL(10,2) DEFAULT NULL,
  importe DECIMAL(10,2) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idx_presupuesto_items_presupuesto (presupuesto_id),
  CONSTRAINT fk_presupuesto_items_presupuesto 
    FOREIGN KEY (presupuesto_id) 
    REFERENCES presupuestos (id) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- INSERTAR DATOS: MARCAS
-- ============================================
INSERT INTO marcas_vehiculos (nombre) VALUES
('Toyota'), ('Ford'), ('Chevrolet'), ('Nissan'), ('Honda'),
('Volkswagen'), ('Hyundai'), ('Kia'), ('Mazda'), ('Subaru'),
('Jeep'), ('Ram'), ('GMC'), ('Dodge'), ('BMW'),
('Mercedes-Benz'), ('Audi'), ('Lexus'), ('Acura'), ('Infiniti'),
('Buick'), ('Cadillac'), ('Lincoln'), ('Chrysler'), ('Mitsubishi'),
('Suzuki'), ('Isuzu'), ('Volvo'), ('Jaguar'), ('Land Rover'),
('Porsche'), ('Tesla'), ('Fiat'), ('Alfa Romeo'), ('Genesis');

-- ============================================
-- INSERTAR DATOS: AÑOS (1950-2030)
-- ============================================
INSERT INTO años_vehiculos (año) 
SELECT YEAR(CURDATE()) - n + 1 as año
FROM (
    SELECT @row := @row + 1 as n
    FROM (SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t1,
         (SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t2,
         (SELECT @row := -1) r
    LIMIT 81
) numbers
WHERE YEAR(CURDATE()) - n + 1 BETWEEN 1950 AND 2030
ORDER BY año DESC;

-- ============================================
-- CONFIGURAR AUTO_INCREMENT
-- ============================================
ALTER TABLE citas AUTO_INCREMENT = 1;
ALTER TABLE clientes AUTO_INCREMENT = 1;
ALTER TABLE cotizaciones AUTO_INCREMENT = 1;
ALTER TABLE presupuestos AUTO_INCREMENT = 1;
ALTER TABLE presupuesto_items AUTO_INCREMENT = 1;
ALTER TABLE servicios AUTO_INCREMENT = 7;
ALTER TABLE roles AUTO_INCREMENT = 3;
ALTER TABLE usuarios AUTO_INCREMENT = 2;
ALTER TABLE servicio_precios AUTO_INCREMENT = 1;
ALTER TABLE marcas_vehiculos AUTO_INCREMENT = 36;
ALTER TABLE años_vehiculos AUTO_INCREMENT = 82;

-- ============================================
-- AGREGAR CAMPO ESTATUS A LA TABLA CITAS
-- ============================================

-- Agregar columna estatus (solo funciona si no existe todavía)
SET SQL_SAFE_UPDATES = 0;

-- Agregar la columna estatus
ALTER TABLE citas 
ADD COLUMN estatus VARCHAR(20) DEFAULT 'Pendiente' 
AFTER servicio;

-- Desactivar modo seguro temporalmente si fuera necesario
SET SQL_SAFE_UPDATES = 0;

-- Actualizar registros existentes
UPDATE citas 
SET estatus = 'Pendiente'
WHERE estatus IS NULL;

-- Volver a activar modo seguro (opcional)
SET SQL_SAFE_UPDATES = 1;
-- ============================================
-- FIN DEL SCRIPT
-- ============================================
-- 
-- INSTRUCCIONES:
-- 1. Abre MySQL Workbench
-- 2. Conéctate a tu servidor MySQL
-- 3. Abre este archivo (File > Open SQL Script)
-- 4. Ejecuta todo el script (F5 o Execute All)
-- 
-- CREDENCIALES POR DEFECTO: (Para iniciar sesion como tipo admin)
-- Usuario: admin
-- Contraseña: admin123
-- ============================================

