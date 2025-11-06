-- ============================================
-- Script SQL para MySQL Workbench
-- Base de datos: servicio_automotriz
-- Sistema de Taller Automotriz con Panel Administrativo
-- ============================================

-- Configuración inicial
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

-- Eliminar base de datos si existe (CUIDADO: Esto eliminará todos los datos)
-- DROP DATABASE IF EXISTS servicio_automotriz;

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS servicio_automotriz 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_general_ci;

-- Usar la base de datos
USE servicio_automotriz;

-- ============================================
-- TABLA: roles
-- Descripción: Almacena los roles del sistema (admin, usuario, etc.)
-- ============================================
DROP TABLE IF EXISTS roles;

CREATE TABLE roles (
  id INT(11) NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(50) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_roles_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Insertar roles por defecto
INSERT INTO roles (nombre, descripcion) VALUES
('admin', 'Administrador del sistema con acceso completo'),
('usuario', 'Usuario regular del sistema');

-- ============================================
-- TABLA: usuarios
-- Descripción: Almacena los usuarios del sistema
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

-- Insertar usuario administrador por defecto
-- Usuario: admin
-- Contraseña: admin123
-- IMPORTANTE: Cambiar la contraseña después del primer acceso
INSERT INTO usuarios (username, password, nombre, email, rol_id) VALUES
('admin', '$2y$10$FSSCIv/7yBYCcJp92ZtBxuZ5XYTNUaRaFCfg9wM6RLYAFX30ihXKa', 'Administrador', 'admin@taller.com', 1);

-- ============================================
-- TABLA: citas
-- Descripción: Almacena las citas agendadas por los clientes
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

-- Datos de ejemplo (opcional)
INSERT INTO citas (nombre, telefono, email, fecha, hora, servicio) VALUES
('Carlos Yael', '6648426962', 'yael2@gmail.com', '2025-05-11', '17:41:00', 'Cambio de Aceite'),
('Carlos Yael', '6648426962', 'yael2@gmail.com', '2025-05-11', '17:41:00', 'Cambio de Aceite'),
('yael', '6648426962', 'carritoacu03@gmail.com', '2025-05-11', '11:45:00', 'Cambio de Aceite');

-- ============================================
-- TABLA: clientes
-- Descripción: Almacena información de los clientes
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
-- TABLA: cotizaciones
-- Descripción: Almacena las solicitudes de cotización
-- ============================================
DROP TABLE IF EXISTS cotizaciones;

CREATE TABLE cotizaciones (
  id INT(11) NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  telefono VARCHAR(20) NOT NULL,
  email VARCHAR(100) NOT NULL,
  servicio VARCHAR(100) NOT NULL,
  mensaje TEXT DEFAULT NULL,
  fecha_envio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Datos de ejemplo (opcional)
INSERT INTO cotizaciones (nombre, telefono, email, servicio, mensaje) VALUES
('Carlos Yael', '6648426962', '', 'cambio-aceite', 'a'),
('Carlos Yael', '6648426962', '', 'cambio-aceite', 'a'),
('yael', '6648426962', 'carlosyaelacuna06@gmail.com', 'cambio-aceite', 'e');

-- ============================================
-- TABLA: presupuestos
-- Descripción: Almacena los presupuestos generados
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

-- Datos de ejemplo (opcional)
INSERT INTO presupuestos (numero_presupuesto, fecha, validez, cliente_nombre, telefono_cliente, marca_vehiculo, modelo_vehiculo, anio_vehiculo, kilometraje, motor, observaciones, subtotal, total) VALUES
('2025-05-11', '2025-05-11', NULL, 'Carlos', '6648426962', 'Cheroki', 'asdasdasd', '2025', '54', '6', 'si o no?', 200.00, 200.00),
('2025-05-03', '2025-05-03', NULL, 'Carlos', '6648426962', 'Cheroki', 'asdasdasd', '2025', '54', '6', 'aaaa', 222.00, 222.00),
('2025-05-12', '2025-05-12', NULL, 'a', '6648426962', 'Cheroki', 'aa', '2025', '54', '6', 'siu?', 4444444.00, 4444444.00);

-- ============================================
-- TABLA: presupuesto_items
-- Descripción: Almacena los items de cada presupuesto
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

-- Datos de ejemplo (opcional)
INSERT INTO presupuesto_items (presupuesto_id, descripcion, cantidad, precio, importe) VALUES
(1, 'Cambio de Aceite', 1, 200.00, 200.00),
(2, 'Cambio de Aceite', 1, 222.00, 222.00),
(3, 'Cambio de Aceite', 1, 4444444.00, 4444444.00);

-- ============================================
-- TABLA: servicios
-- Descripción: Almacena los servicios ofrecidos por el taller
-- ============================================
DROP TABLE IF EXISTS servicios;

CREATE TABLE servicios (
  id INT(11) NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- CONFIGURACIÓN DE AUTO_INCREMENT
-- ============================================
ALTER TABLE citas AUTO_INCREMENT = 1;
ALTER TABLE clientes AUTO_INCREMENT = 1;
ALTER TABLE cotizaciones AUTO_INCREMENT = 1;
ALTER TABLE presupuestos AUTO_INCREMENT = 1;
ALTER TABLE presupuesto_items AUTO_INCREMENT = 1;
ALTER TABLE servicios AUTO_INCREMENT = 1;
ALTER TABLE roles AUTO_INCREMENT = 1;
ALTER TABLE usuarios AUTO_INCREMENT = 1;

-- ============================================
-- VERIFICACIÓN FINAL
-- ============================================
-- Verificar que todas las tablas se crearon correctamente
-- SELECT 'Base de datos creada exitosamente' AS mensaje;
-- SELECT TABLE_NAME FROM information_schema.TABLES 
-- WHERE TABLE_SCHEMA = 'servicio_automotriz' ORDER BY TABLE_NAME;

-- ============================================
-- FIN DEL SCRIPT
-- ============================================
-- 
-- INSTRUCCIONES PARA MYSQL WORKBENCH:
-- 
-- 1. Abrir MySQL Workbench
-- 2. Conectarse a tu servidor MySQL
-- 3. Abrir este archivo (File > Open SQL Script)
-- 4. Revisar la línea que dice "DROP DATABASE IF EXISTS" 
--    (está comentada por seguridad)
-- 5. Ejecutar el script completo (Execute > Execute All or F5)
-- 6. Verificar que todas las tablas se crearon correctamente
-- 
-- CREDENCIALES POR DEFECTO:
-- Usuario: admin
-- Contraseña: admin123
-- 
-- IMPORTANTE: Cambiar la contraseña después del primer acceso
-- ============================================

