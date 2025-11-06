"""
Aplicación principal Flask - Taller Automotriz
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
from mysql.connector import Error
from functools import wraps
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tu-clave-secreta-cambiar-en-produccion')

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'servicio_automotriz',
    'user': 'root',
    'password': '',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def get_cursor(conn):
    """Obtener cursor con diccionario"""
    return conn.cursor(dictionary=True)

# ============================================
# DECORADORES DE AUTENTICACIÓN
# ============================================

def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador para requerir rol de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        if session.get('rol') != 'admin':
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# RUTAS PÚBLICAS
# ============================================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/servicios')
def servicios():
    """Página de servicios"""
    return render_template('servicios.html')

@app.route('/cotizaciones', methods=['GET', 'POST'])
def cotizaciones():
    """Página de cotizaciones"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        servicio = request.form.get('servicio', '').strip()
        mensaje = request.form.get('mensaje', '').strip()
        
        if nombre and telefono and email and servicio:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = get_cursor(conn)
                    sql = "INSERT INTO cotizaciones (nombre, telefono, email, servicio, mensaje) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (nombre, telefono, email, servicio, mensaje))
                    conn.commit()
                    flash('✅ Cotización enviada correctamente', 'success')
                except Error as e:
                    flash(f'❌ Error al enviar cotización: {str(e)}', 'danger')
                finally:
                    conn.close()
            else:
                flash('❌ Error de conexión a la base de datos', 'danger')
        else:
            flash('Por favor complete todos los campos requeridos', 'warning')
        
        return redirect(url_for('cotizaciones'))
    
    return render_template('cotizaciones.html')

@app.route('/contacto')
def contacto():
    """Página de contacto"""
    return render_template('contacto.html')

@app.route('/citas', methods=['GET', 'POST'])
def citas():
    """Página de agendar citas"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        fecha = request.form.get('fecha', '').strip()
        hora = request.form.get('hora', '').strip()
        servicio = request.form.get('servicio', '').strip()
        
        if nombre and telefono and email and fecha and hora and servicio:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = get_cursor(conn)
                    sql = """INSERT INTO citas (nombre, telefono, email, fecha, hora, servicio) 
                             VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (nombre, telefono, email, fecha, hora, servicio))
                    conn.commit()
                    flash('✅ ¡Tu cita ha sido registrada con éxito!', 'success')
                    return redirect(url_for('index'))
                except Error as e:
                    flash(f'❌ Error al guardar la cita: {str(e)}', 'danger')
                finally:
                    conn.close()
            else:
                flash('❌ Error de conexión a la base de datos', 'danger')
        else:
            flash('Por favor complete todos los campos requeridos', 'warning')
    
    return render_template('citas.html')

@app.route('/presupuesto', methods=['GET', 'POST'])
def presupuesto():
    """Página de generar presupuestos"""
    if request.method == 'POST':
        conn = get_db_connection()
        if not conn:
            flash('❌ Error de conexión a la base de datos', 'danger')
            return redirect(url_for('presupuesto'))
        
        try:
            cursor = get_cursor(conn)
            
            # Insertar presupuesto
            sql_presupuesto = """INSERT INTO presupuestos 
                (fecha, cliente_nombre, telefono_cliente, marca_vehiculo, modelo_vehiculo, 
                 anio_vehiculo, kilometraje, motor, observaciones, subtotal, total, numero_presupuesto)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            fecha = request.form.get('fecha', '')
            cliente_nombre = request.form.get('cliente_nombre', '')
            telefono_cliente = request.form.get('telefono_cliente', '')
            marca_vehiculo = request.form.get('marca_vehiculo', '')
            modelo_vehiculo = request.form.get('modelo_vehiculo', '')
            anio_vehiculo = request.form.get('anio_vehiculo', '')
            kilometraje = request.form.get('kilometraje', '')
            motor = request.form.get('motor', '')
            observaciones = request.form.get('observaciones', '')
            subtotal = float(request.form.get('subtotal', 0) or 0)
            total = float(request.form.get('total', 0) or 0)
            numero_presupuesto = request.form.get('numero_presupuesto', fecha)
            
            cursor.execute(sql_presupuesto, (
                fecha, cliente_nombre, telefono_cliente, marca_vehiculo, modelo_vehiculo,
                anio_vehiculo, kilometraje, motor, observaciones, subtotal, total, numero_presupuesto
            ))
            
            presupuesto_id = cursor.lastrowid
            
            # Insertar items
            descripciones = request.form.getlist('descripcion[]')
            cantidades = request.form.getlist('cantidad[]')
            precios = request.form.getlist('precio[]')
            importes = request.form.getlist('importe[]')
            
            if descripciones:
                sql_items = """INSERT INTO presupuesto_items 
                    (presupuesto_id, descripcion, cantidad, precio, importe)
                    VALUES (%s, %s, %s, %s, %s)"""
                
                for i in range(len(descripciones)):
                    if descripciones[i].strip():
                        cursor.execute(sql_items, (
                            presupuesto_id,
                            descripciones[i],
                            int(cantidades[i] or 1),
                            float(precios[i] or 0),
                            float(importes[i] or 0)
                        ))
            
            conn.commit()
            flash('✅ ¡Presupuesto guardado con éxito!', 'success')
            return redirect(url_for('index'))
            
        except Error as e:
            conn.rollback()
            flash(f'❌ Error al guardar el presupuesto: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return render_template('presupuesto.html')

@app.route('/generar_pdf/<int:presupuesto_id>')
def generar_pdf(presupuesto_id):
    """Generar PDF del presupuesto"""
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión', 'danger')
        return redirect(url_for('presupuesto'))
    
    try:
        cursor = get_cursor(conn)
        
        # Obtener presupuesto
        cursor.execute("SELECT * FROM presupuestos WHERE id = %s", (presupuesto_id,))
        presupuesto = cursor.fetchone()
        
        if not presupuesto:
            flash('Presupuesto no encontrado', 'danger')
            return redirect(url_for('presupuesto'))
        
        # Obtener items
        cursor.execute("SELECT * FROM presupuesto_items WHERE presupuesto_id = %s", (presupuesto_id,))
        items = cursor.fetchall()
        
        # Generar PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "PRESUPUESTO")
        p.setFont("Helvetica", 10)
        p.drawString(50, height - 70, f"Fecha: {presupuesto['fecha']}")
        p.drawString(50, height - 85, f"Cliente: {presupuesto['cliente_nombre']}")
        
        # Items
        y = height - 150
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, "Descripción")
        p.drawString(300, y, "Cantidad")
        p.drawString(350, y, "Precio")
        p.drawString(400, y, "Importe")
        
        y -= 20
        p.setFont("Helvetica", 9)
        total = 0
        for item in items:
            p.drawString(50, y, item['descripcion'][:40])
            p.drawString(300, y, str(item['cantidad']))
            p.drawString(350, y, f"${item['precio']:.2f}")
            p.drawString(400, y, f"${item['importe']:.2f}")
            total += float(item['importe'])
            y -= 15
        
        # Total
        y -= 10
        p.setFont("Helvetica-Bold", 12)
        p.drawString(350, y, f"Total: ${total:.2f}")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return send_file(buffer, mimetype='application/pdf', 
                        as_attachment=True, 
                        download_name=f"presupuesto_{presupuesto['numero_presupuesto']}.pdf")
        
    except Error as e:
        flash(f'Error al generar PDF: {str(e)}', 'danger')
        return redirect(url_for('presupuesto'))
    finally:
        conn.close()

# ============================================
# RUTAS DE AUTENTICACIÓN
# ============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if username and password:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = get_cursor(conn)
                    sql = """SELECT u.*, r.nombre as rol_nombre 
                             FROM usuarios u 
                             INNER JOIN roles r ON u.rol_id = r.id 
                             WHERE u.username = %s AND u.activo = 1"""
                    cursor.execute(sql, (username,))
                    usuario = cursor.fetchone()
                    
                    if usuario and check_password_hash(usuario['password'], password):
                        session['usuario_id'] = usuario['id']
                        session['username'] = usuario['username']
                        session['nombre'] = usuario['nombre']
                        session['rol'] = usuario['rol_nombre']
                        
                        flash(f'Bienvenido, {usuario["nombre"]}', 'success')
                        
                        if usuario['rol_nombre'] == 'admin':
                            return redirect(url_for('admin_dashboard'))
                        else:
                            return redirect(url_for('index'))
                    else:
                        flash('Usuario o contraseña incorrectos', 'danger')
                except Error as e:
                    flash(f'Error al verificar credenciales: {str(e)}', 'danger')
                finally:
                    conn.close()
            else:
                flash('Error de conexión a la base de datos', 'danger')
        else:
            flash('Por favor complete todos los campos', 'warning')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('index'))

# ============================================
# RUTAS ADMINISTRATIVAS
# ============================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Dashboard administrativo"""
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión', 'danger')
        return redirect(url_for('index'))
    
    try:
        cursor = get_cursor(conn)
        
        # Estadísticas
        cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE activo = 1")
        total_usuarios = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM servicios")
        total_servicios = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM citas")
        total_citas = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM cotizaciones")
        total_cotizaciones = cursor.fetchone()['total']
        
        stats = {
            'usuarios': total_usuarios,
            'servicios': total_servicios,
            'citas': total_citas,
            'cotizaciones': total_cotizaciones
        }
        
        return render_template('admin/dashboard.html', stats=stats)
    except Error as e:
        flash(f'Error al cargar estadísticas: {str(e)}', 'danger')
        return redirect(url_for('index'))
    finally:
        conn.close()

@app.route('/admin/usuarios', methods=['GET', 'POST'])
@admin_required
def admin_usuarios():
    """Gestión de usuarios"""
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = get_cursor(conn)
        
        if request.method == 'POST':
            accion = request.form.get('accion', '')
            
            if accion == 'crear':
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '').strip()
                nombre = request.form.get('nombre', '').strip()
                email = request.form.get('email', '').strip()
                telefono = request.form.get('telefono', '').strip()
                rol_id = int(request.form.get('rol_id', 2))
                
                if username and password and nombre:
                    password_hash = generate_password_hash(password)
                    sql = """INSERT INTO usuarios (username, password, nombre, email, telefono, rol_id) 
                             VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (username, password_hash, nombre, email, telefono, rol_id))
                    conn.commit()
                    flash('Usuario creado exitosamente', 'success')
                else:
                    flash('Complete todos los campos requeridos', 'warning')
            
            elif accion == 'editar':
                usuario_id = int(request.form.get('id', 0))
                nombre = request.form.get('nombre', '').strip()
                email = request.form.get('email', '').strip()
                telefono = request.form.get('telefono', '').strip()
                rol_id = int(request.form.get('rol_id', 2))
                activo = 1 if request.form.get('activo') else 0
                
                sql = """UPDATE usuarios SET nombre = %s, email = %s, telefono = %s, 
                         rol_id = %s, activo = %s WHERE id = %s"""
                cursor.execute(sql, (nombre, email, telefono, rol_id, activo, usuario_id))
                conn.commit()
                flash('Usuario actualizado exitosamente', 'success')
            
            elif accion == 'eliminar':
                usuario_id = int(request.form.get('id', 0))
                if usuario_id == session.get('usuario_id'):
                    flash('No puede eliminar su propio usuario', 'danger')
                else:
                    cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
                    conn.commit()
                    flash('Usuario eliminado exitosamente', 'success')
            
            elif accion == 'cambiar_password':
                usuario_id = int(request.form.get('id', 0))
                password = request.form.get('password', '').strip()
                if password:
                    password_hash = generate_password_hash(password)
                    cursor.execute("UPDATE usuarios SET password = %s WHERE id = %s", 
                                 (password_hash, usuario_id))
                    conn.commit()
                    flash('Contraseña actualizada exitosamente', 'success')
        
        # Obtener usuarios y roles
        cursor.execute("""SELECT u.*, r.nombre as rol_nombre 
                          FROM usuarios u 
                          INNER JOIN roles r ON u.rol_id = r.id 
                          ORDER BY u.fecha_creacion DESC""")
        usuarios = cursor.fetchall()
        
        cursor.execute("SELECT * FROM roles ORDER BY nombre")
        roles = cursor.fetchall()
        
        return render_template('admin/usuarios.html', usuarios=usuarios, roles=roles)
    
    except Error as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        conn.close()

@app.route('/admin/servicios', methods=['GET', 'POST'])
@admin_required
def admin_servicios():
    """Gestión de servicios"""
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = get_cursor(conn)
        
        if request.method == 'POST':
            accion = request.form.get('accion', '')
            
            if accion == 'crear':
                nombre = request.form.get('nombre', '').strip()
                descripcion = request.form.get('descripcion', '').strip()
                if nombre:
                    sql = "INSERT INTO servicios (nombre, descripcion) VALUES (%s, %s)"
                    cursor.execute(sql, (nombre, descripcion))
                    conn.commit()
                    flash('Servicio creado exitosamente', 'success')
                else:
                    flash('Ingrese el nombre del servicio', 'warning')
            
            elif accion == 'editar':
                servicio_id = int(request.form.get('id', 0))
                nombre = request.form.get('nombre', '').strip()
                descripcion = request.form.get('descripcion', '').strip()
                if nombre:
                    sql = "UPDATE servicios SET nombre = %s, descripcion = %s WHERE id = %s"
                    cursor.execute(sql, (nombre, descripcion, servicio_id))
                    conn.commit()
                    flash('Servicio actualizado exitosamente', 'success')
            
            elif accion == 'eliminar':
                servicio_id = int(request.form.get('id', 0))
                cursor.execute("DELETE FROM servicios WHERE id = %s", (servicio_id,))
                conn.commit()
                flash('Servicio eliminado exitosamente', 'success')
        
        cursor.execute("SELECT * FROM servicios ORDER BY nombre")
        servicios = cursor.fetchall()
        
        return render_template('admin/servicios.html', servicios=servicios)
    
    except Error as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        conn.close()

@app.route('/admin/roles', methods=['GET', 'POST'])
@admin_required
def admin_roles():
    """Gestión de roles"""
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = get_cursor(conn)
        
        if request.method == 'POST':
            accion = request.form.get('accion', '')
            
            if accion == 'crear':
                nombre = request.form.get('nombre', '').strip()
                descripcion = request.form.get('descripcion', '').strip()
                if nombre:
                    sql = "INSERT INTO roles (nombre, descripcion) VALUES (%s, %s)"
                    cursor.execute(sql, (nombre, descripcion))
                    conn.commit()
                    flash('Rol creado exitosamente', 'success')
                else:
                    flash('Ingrese el nombre del rol', 'warning')
            
            elif accion == 'editar':
                rol_id = int(request.form.get('id', 0))
                nombre = request.form.get('nombre', '').strip()
                descripcion = request.form.get('descripcion', '').strip()
                if nombre:
                    sql = "UPDATE roles SET nombre = %s, descripcion = %s WHERE id = %s"
                    cursor.execute(sql, (nombre, descripcion, rol_id))
                    conn.commit()
                    flash('Rol actualizado exitosamente', 'success')
            
            elif accion == 'eliminar':
                rol_id = int(request.form.get('id', 0))
                # Verificar si hay usuarios con este rol
                cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE rol_id = %s", (rol_id,))
                total = cursor.fetchone()['total']
                if total > 0:
                    flash(f'No se puede eliminar el rol porque hay {total} usuario(s) asignado(s)', 'danger')
                else:
                    cursor.execute("DELETE FROM roles WHERE id = %s", (rol_id,))
                    conn.commit()
                    flash('Rol eliminado exitosamente', 'success')
        
        cursor.execute("""SELECT r.*, COUNT(u.id) as total_usuarios 
                          FROM roles r 
                          LEFT JOIN usuarios u ON r.id = u.rol_id 
                          GROUP BY r.id 
                          ORDER BY r.nombre""")
        roles = cursor.fetchall()
        
        return render_template('admin/roles.html', roles=roles)
    
    except Error as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

