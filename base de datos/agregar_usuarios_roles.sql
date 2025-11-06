-- ============================================
-- Script para MySQL Workbench
-- Agregar tablas de usuarios y roles a base de datos existente
-- ============================================

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
-- FIN DEL SCRIPT
-- ============================================
-- 
-- INSTRUCCIONES:
-- 1. Abrir MySQL Workbench
-- 2. Conectarse al servidor MySQL
-- 3. Abrir este archivo (File > Open SQL Script)
-- 4. Ejecutar el script (F5 o Execute)
-- 
-- CREDENCIALES POR DEFECTO:
-- Usuario: admin
-- Contraseña: admin123
-- ============================================

