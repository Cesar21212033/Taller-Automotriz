"""
Aplicación principal Flask - Taller Automotriz

Esta es la aplicación principal del sistema de taller automotriz.
Básicamente, aquí está todo el backend: las rutas, la lógica de negocio,
la conexión a la base de datos, el envío de correos, etc.
"""

# ============================================
# IMPORTS - Todas las librerías que necesitamos
# ============================================
# Flask: el framework web que usamos
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
# Flask-Mail: para enviar correos electrónicos
from flask_mail import Mail, Message
# Werkzeug: para hashear y verificar contraseñas de forma segura
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
# MySQL: para conectarnos a la base de datos
import mysql.connector
from mysql.connector import Error
# functools: para crear decoradores (como @login_required)
from functools import wraps
# os: para leer variables de entorno
import os
# datetime: para trabajar con fechas y horas
from datetime import datetime, timedelta, time
# ReportLab: para generar PDFs (aunque ya no lo usamos mucho)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
# dotenv: para cargar variables de entorno desde archivo .env
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env (si existe)
# Esto es útil para tener configuraciones secretas sin hardcodearlas
load_dotenv()

# ============================================
# CONFIGURACIÓN INICIAL DE FLASK
# ============================================
# Creamos la aplicación Flask
app = Flask(__name__)
# La secret key se usa para firmar las sesiones y cookies de forma segura
# Si alguien la obtiene, podría falsificar sesiones, así que es importante
app.secret_key = os.environ.get('SECRET_KEY', 'vedx ykjx swwe nmue')

# ============================================
# CONFIGURACIÓN DE CORREO ELECTRÓNICO
# ============================================
# Aquí configuramos cómo se van a enviar los correos
# ⚠️ ADVERTENCIA: Si pones la contraseña aquí, NUNCA subas el código a un repositorio público
# RECOMENDADO: Usa archivo .env (ver INSTRUCCIONES_CORREO.md)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')  # Servidor SMTP de Gmail
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))  # Puerto para TLS
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']  # Usar TLS (seguridad)
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'cesarini.05ramos@gmail.com')  # Tu correo
# ⚠️ REEMPLAZA 'TU_CONTRASEÑA_AQUI' con tu contraseña de aplicación de Gmail
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'vedx ykjx swwe nmue')  # Contraseña de aplicación
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'cesarini.05ramos@gmail.com')  # Correo por defecto

# Inicializamos el objeto Mail con la configuración de Flask
mail = Mail(app)

# ============================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================
# Aquí están los datos de conexión a MySQL
# En producción, esto debería estar en variables de entorno por seguridad
DB_CONFIG = {
    'host': 'localhost',  # El servidor de MySQL (normalmente localhost)
    'database': 'servicio_automotriz',  # El nombre de nuestra base de datos
    'user': 'root',  # Usuario de MySQL
    'password': 'Baby20150531',  # Contraseña de MySQL
    'charset': 'utf8mb4',  # Codificación para soportar emojis y caracteres especiales
    'collation': 'utf8mb4_general_ci'  # Reglas de comparación de caracteres
}

def get_db_connection():
    """
    Función helper para obtener una conexión a la base de datos.
    
    Básicamente, cada vez que necesitamos hacer algo en la BD,
    llamamos a esta función para obtener una conexión.
    Si hay un error, retorna None en lugar de crashear.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def get_cursor(conn):
    """
    Función helper para obtener un cursor de la base de datos.
    
    El cursor es lo que usamos para ejecutar queries SQL.
    dictionary=True hace que los resultados vengan como diccionarios
    en lugar de tuplas, lo cual es más fácil de trabajar.
    buffered=True evita el error "Unread result found" cuando hacemos
    múltiples queries seguidos.
    """
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        return cursor
    except Exception as e:
        print(f"[ERROR] Error creando cursor: {e}")
        raise

# ============================================
# DECORADORES DE AUTENTICACIÓN
# ============================================
# Los decoradores son funciones que "envuelven" otras funciones.
# En este caso, los usamos para proteger rutas que requieren login o ser admin.

def login_required(f):
    """
    Decorador para proteger rutas que requieren estar logueado.
    
    Si alguien intenta acceder a una ruta con @login_required y no está logueado,
    lo redirige al login. Si está logueado, deja pasar normalmente.
    
    Ejemplo de uso:
        @app.route('/usuario')
        @login_required
        def user_dashboard():
            # Esta función solo se ejecuta si el usuario está logueado
            ...
    """
    @wraps(f)  # Esto preserva el nombre y docstring de la función original
    def decorated_function(*args, **kwargs):
        # Verificamos si hay un usuario_id en la sesión
        if 'usuario_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        # Si está logueado, ejecutamos la función normalmente
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorador para proteger rutas que requieren ser administrador.
    
    Primero verifica que esté logueado, y luego que su rol sea 'admin'.
    Si no cumple alguna condición, lo redirige apropiadamente.
    
    Ejemplo de uso:
        @app.route('/admin/usuarios')
        @admin_required
        def admin_usuarios():
            # Esta función solo se ejecuta si el usuario es admin
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Primero verificamos que esté logueado
        if 'usuario_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        # Luego verificamos que sea admin
        if session.get('rol') != 'admin':
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('index'))
        # Si es admin, dejamos pasar
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# RUTAS PÚBLICAS
# ============================================
# Estas son las rutas que cualquiera puede ver sin estar logueado.
# La página principal, servicios, contacto, etc.

@app.route('/')
def index():
    """
    Página principal del sitio.
    
    Esta es la primera página que ve el usuario cuando entra al sitio.
    No requiere login, es completamente pública.
    """
    try:
        return render_template('index.html')
    except Exception as e:
        # Si algo sale mal, lo capturamos y mostramos un mensaje amigable
        print(f"[ERROR] Error al cargar página principal: {e}")
        import traceback
        traceback.print_exc()
        flash('Error al cargar la página. Por favor intenta más tarde.', 'danger')
        return render_template('index.html')  # Intentar renderizar de nuevo

@app.route('/servicios')
def servicios():
    """
    Página que muestra todos los servicios disponibles.
    
    Obtiene la lista de servicios de la base de datos y los muestra
    en una página pública para que los clientes vean qué servicios ofrecemos.
    """
    try:
        conn = get_db_connection()
        servicios = []  # Lista vacía por defecto
        if conn:
            try:
                cursor = get_cursor(conn)
                # Obtenemos todos los servicios ordenados por nombre
                cursor.execute("SELECT * FROM servicios ORDER BY nombre")
                servicios = cursor.fetchall()  # Traemos todos los resultados
            except Error as e:
                print(f"[ERROR] Error al obtener servicios: {e}")
                flash('Error al cargar servicios', 'warning')
            finally:
                # Siempre cerramos la conexión, incluso si hay error
                conn.close()
        return render_template('servicios.html', servicios=servicios)
    except Exception as e:
        print(f"[ERROR] Error en página de servicios: {e}")
        import traceback
        traceback.print_exc()
        flash('Error al cargar la página de servicios.', 'danger')
        # Retornamos con lista vacía para que la página al menos cargue
        return render_template('servicios.html', servicios=[])

@app.route('/cotizaciones', methods=['GET', 'POST'])
def cotizaciones():
    """
    Página para solicitar cotizaciones personalizadas.
    
    Esta es una de las funciones más importantes. Permite a los clientes
    solicitar una cotización basada en:
    - El servicio que necesitan
    - La marca del vehículo
    - El año del vehículo
    - El número de cilindros
    
    El precio se calcula dinámicamente según estos factores.
    Cuando se envía el formulario, se guarda en la BD y se envía un correo automático.
    """
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos', 'danger')
        return render_template('cotizaciones.html', servicios=[], marcas=[], años=[])
    
    try:
        cursor = get_cursor(conn)
        
        # Obtener servicios disponibles para el dropdown
        cursor.execute("SELECT * FROM servicios ORDER BY nombre")
        servicios = cursor.fetchall()
        
        # Obtener marcas disponibles (si la tabla existe)
        try:
            cursor.execute("SELECT * FROM marcas_vehiculos WHERE activo = 1 ORDER BY nombre")
            marcas = cursor.fetchall()
        except Error:
            # Si la tabla no existe, simplemente usamos lista vacía
            marcas = []
        
        # Obtener años disponibles (si la tabla existe)
        try:
            cursor.execute("SELECT * FROM años_vehiculos WHERE activo = 1 ORDER BY año DESC")
            años = cursor.fetchall()
        except Error:
            # Si la tabla no existe, simplemente usamos lista vacía
            años = []
        
        # Si el usuario está enviando el formulario (POST)
        if request.method == 'POST':
            nombre = request.form.get('nombre', '').strip()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            servicio_id = int(request.form.get('servicio_id', 0))
            marca_vehiculo = request.form.get('marca_vehiculo', '').strip()
            modelo_vehiculo = request.form.get('modelo_vehiculo', '').strip()
            año_id = int(request.form.get('año_id', 0))
            cilindros = request.form.get('cilindros', '').strip()
            mensaje = request.form.get('mensaje', '').strip()
            
            if nombre and telefono and email and servicio_id and marca_vehiculo and año_id and cilindros:
                try:
                    cilindros_int = int(cilindros)
                    
                    # Obtener año del vehículo
                    cursor.execute("SELECT año FROM años_vehiculos WHERE id = %s", (año_id,))
                    año_data = cursor.fetchone()
                    año = año_data['año'] if año_data else 0
                    
                    # Obtener marca_id si existe (opcional)
                    marca_id = None
                    try:
                        cursor.execute("SELECT id FROM marcas_vehiculos WHERE nombre = %s", (marca_vehiculo,))
                        marca_data = cursor.fetchone()
                        if marca_data:
                            marca_id = marca_data['id']
                    except Error:
                        marca_id = None
                    
                    # Obtener nombre del servicio
                    cursor.execute("SELECT nombre FROM servicios WHERE id = %s", (servicio_id,))
                    servicio_data = cursor.fetchone()
                    servicio_nombre = servicio_data['nombre'] if servicio_data else 'Servicio'
                    
                    # Calcular precio personalizado
                    precio_calculado = calcular_precio_servicio(cursor, servicio_id, cilindros_int, año)
                    
                    # Insertar cotización
                    sql = """INSERT INTO cotizaciones 
                             (nombre, telefono, email, servicio, servicio_id, 
                              marca_vehiculo, marca_id, modelo_vehiculo, 
                              anio_vehiculo, año_id, cilindros, mensaje, precio_calculado) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (
                        nombre, telefono, email, servicio_nombre, servicio_id,
                        marca_vehiculo, marca_id, modelo_vehiculo,
                        año, año_id, cilindros_int, mensaje, precio_calculado
                    ))
                    cotizacion_id = cursor.lastrowid
                    conn.commit()
                    
                    # Guardar también como cliente si no existe
                    cursor.execute("SELECT id FROM clientes WHERE correo = %s", (email,))
                    cliente_existente = cursor.fetchone()
                    if not cliente_existente:
                        cursor.execute("INSERT INTO clientes (nombre, telefono, correo) VALUES (%s, %s, %s)",
                                     (nombre, telefono, email))
                        conn.commit()
                    
                    # Enviar correo automáticamente al cliente
                    try:
                        if enviar_cotizacion_por_correo(cotizacion_id):
                            flash(f'✅ Cotización enviada correctamente. Precio estimado: ${precio_calculado:.2f}. Se ha enviado un correo con los detalles.', 'success')
                        else:
                            flash(f'✅ Cotización guardada correctamente. Precio estimado: ${precio_calculado:.2f}. No se pudo enviar el correo.', 'warning')
                    except Exception as e:
                        print(f"Error al enviar correo automático: {e}")
                        flash(f'✅ Cotización guardada correctamente. Precio estimado: ${precio_calculado:.2f}. Error al enviar correo: {str(e)}', 'warning')
                    
                    return redirect(url_for('cotizaciones'))
                    
                except ValueError:
                    flash('❌ Los datos deben ser válidos', 'danger')
                except Error as e:
                    flash(f'❌ Error al enviar cotización: {str(e)}', 'danger')
            else:
                flash('Por favor complete todos los campos requeridos', 'warning')
        
        return render_template('cotizaciones.html', servicios=servicios, marcas=marcas, años=años)
    
    except Error as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('cotizaciones.html', servicios=[], marcas=[], años=[])
    finally:
        conn.close()

def calcular_precio_servicio(cursor, servicio_id, cilindros, anio):
    """
    Calcula el precio de un servicio basado en cilindros y año del vehículo.
    
    Esta función es el corazón del sistema de precios personalizados.
    Busca en la tabla servicio_precios la configuración que coincida con:
    - El servicio seleccionado
    - El rango de cilindros (cilindros_min <= cilindros <= cilindros_max)
    - El rango de años (anio_min <= anio <= anio_max, si están definidos)
    
    La fórmula del precio es:
        precio_total = precio_base + (precio_por_cilindro * cilindros) + (precio_por_anio * anio)
    
    Si no encuentra una configuración exacta, intenta buscar solo por cilindros.
    Si tampoco encuentra nada, retorna un precio por defecto de $500.00.
    """
    try:
        # Primero intentamos buscar un precio que coincida con servicio, cilindros Y año
        sql = """SELECT precio_base, precio_por_cilindro, precio_por_anio 
                 FROM servicio_precios 
                 WHERE servicio_id = %s 
                   AND cilindros_min <= %s 
                   AND cilindros_max >= %s
                   AND (anio_min IS NULL OR anio_min <= %s)
                   AND (anio_max IS NULL OR anio_max >= %s)
                   AND activo = 1
                 ORDER BY precio_base ASC
                 LIMIT 1"""
        cursor.execute(sql, (servicio_id, cilindros, cilindros, anio, anio))
        precio_data = cursor.fetchone()
        
        if precio_data:
            # Si encontramos una configuración, calculamos el precio
            precio_base = float(precio_data['precio_base'])
            precio_por_cilindro = float(precio_data['precio_por_cilindro'] or 0)
            precio_por_anio = float(precio_data['precio_por_anio'] or 0)
            
            # Fórmula del precio: base + (cilindros * precio_por_cilindro) + (año * precio_por_año)
            precio_total = precio_base + (precio_por_cilindro * cilindros) + (precio_por_anio * anio)
            return round(precio_total, 2)
        else:
            # Si no hay precio que considere el año, buscamos solo por cilindros
            sql = """SELECT precio_base, precio_por_cilindro 
                     FROM servicio_precios 
                     WHERE servicio_id = %s 
                       AND cilindros_min <= %s 
                       AND cilindros_max >= %s
                       AND activo = 1
                     ORDER BY precio_base ASC
                     LIMIT 1"""
            cursor.execute(sql, (servicio_id, cilindros, cilindros))
            precio_data = cursor.fetchone()
            
            if precio_data:
                # Si encontramos algo solo por cilindros, calculamos sin el año
                precio_base = float(precio_data['precio_base'])
                precio_por_cilindro = float(precio_data['precio_por_cilindro'] or 0)
                return round(precio_base + (precio_por_cilindro * cilindros), 2)
            else:
                # Si no hay ninguna configuración, usamos un precio por defecto
                return 500.00
                
    except ValueError as e:
        print(f"[ERROR] Error de validación calculando precio: {e}")
        raise  # Re-lanzar para que la función llamadora lo maneje
    except Error as e:
        print(f"[ERROR] Error de BD calculando precio: {e}")
        import traceback
        traceback.print_exc()
        return 500.00
    except Exception as e:
        print(f"[ERROR] Error inesperado calculando precio: {e}")
        import traceback
        traceback.print_exc()
        return 500.00

@app.route('/calcular_precio', methods=['POST'])
def calcular_precio():
    """
    API endpoint para calcular el precio en tiempo real.
    
    Esta ruta es llamada por JavaScript cuando el usuario selecciona
    servicio, año y cilindros. Retorna el precio calculado en formato JSON
    para que se muestre en la página sin recargar.
    
    Es una API porque retorna JSON en lugar de HTML.
    """
    try:
        # Obtenemos los datos del formulario
        servicio_id = int(request.form.get('servicio_id', 0))
        anio = int(request.form.get('anio', 0))
        cilindros = int(request.form.get('cilindros', 0))
        
        # Verificamos que todos los datos estén presentes
        if servicio_id and anio and cilindros:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = get_cursor(conn)
                    # Calculamos el precio usando nuestra función helper
                    precio = calcular_precio_servicio(cursor, servicio_id, cilindros, anio)
                    # Retornamos el resultado en formato JSON
                    return jsonify({'precio': precio, 'success': True})
                except Error as e:
                    print(f"[ERROR] Error en cálculo de precio (BD): {e}")
                    return jsonify({'precio': 0, 'success': False, 'error': 'Error de base de datos'})
                except Exception as e:
                    print(f"[ERROR] Error en cálculo de precio: {e}")
                    import traceback
                    traceback.print_exc()
                    return jsonify({'precio': 0, 'success': False, 'error': 'Error al calcular precio'})
                finally:
                    if conn:
                        conn.close()
        
        # Si faltan datos, retornamos error
        return jsonify({'precio': 0, 'success': False, 'error': 'Datos incompletos'})
    except ValueError as e:
        print(f"[ERROR] Error de validación en calcular_precio: {e}")
        return jsonify({'precio': 0, 'success': False, 'error': 'Datos inválidos'})
    except Exception as e:
        print(f"[ERROR] Error inesperado en calcular_precio: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'precio': 0, 'success': False, 'error': 'Error inesperado'})

@app.route('/contacto')
def contacto():
    """Página de contacto"""
    try:
        return render_template('contacto.html')
    except Exception as e:
        print(f"[ERROR] Error al cargar página de contacto: {e}")
        import traceback
        traceback.print_exc()
        flash('Error al cargar la página de contacto.', 'danger')
        return render_template('contacto.html')

@app.route('/api/horarios_disponibles/<fecha>')
def api_horarios_disponibles(fecha):
    """
    API para obtener los horarios disponibles para una fecha específica.
    
    Esta función es llamada por JavaScript cuando el usuario selecciona una fecha
    para agendar una cita. Retorna una lista de horarios disponibles considerando:
    - El horario de atención (7 AM a 5 PM)
    - Las citas ya agendadas
    - El requisito de mínimo 1 hora entre citas
    
    Retorna JSON con la lista de horarios disponibles.
    """
    try:
        # Validar formato de fecha
        if not fecha or len(fecha) != 10:
            return jsonify({'error': 'Formato de fecha inválido', 'horarios': []}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Error de conexión', 'horarios': []}), 500
        
        try:
            cursor = get_cursor(conn)
            
            # Obtener citas existentes para esa fecha
            cursor.execute("SELECT hora FROM citas WHERE fecha = %s ORDER BY hora", (fecha,))
            citas_existentes = cursor.fetchall()
            
            # Horario de atención: 7:00 AM a 5:00 PM
            horarios_todos = []
            for hora in range(7, 17):  # 7 AM a 4 PM (última cita a las 4 PM para terminar a las 5 PM)
                horarios_todos.append(f"{hora:02d}:00")
                horarios_todos.append(f"{hora:02d}:30")
            
            print(f"[DEBUG] Total horarios generados: {len(horarios_todos)}")
            print(f"[DEBUG] Horarios: {horarios_todos[:5]}...")
            
            # Obtener horas ocupadas
            horas_ocupadas = set()
            print(f"[DEBUG] Citas existentes para {fecha}: {len(citas_existentes)}")
            
            for cita in citas_existentes:
                hora_cita = cita['hora']
                print(f"[DEBUG] Procesando cita con hora: {hora_cita} (tipo: {type(hora_cita)})")
                
                # Manejar diferentes formatos de hora
                hora_int = None
                minuto = None
                
                if isinstance(hora_cita, timedelta):
                    # Convertir timedelta a time
                    total_seconds = int(hora_cita.total_seconds())
                    hora_int = total_seconds // 3600
                    minuto = (total_seconds % 3600) // 60
                    print(f"[DEBUG] Hora convertida de timedelta: {hora_int:02d}:{minuto:02d}")
                elif isinstance(hora_cita, str):
                    # Si es string, parsear
                    if ':' in hora_cita:
                        hora_parts = hora_cita.split(':')
                        hora_int = int(hora_parts[0])
                        # Manejar formato HH:MM:SS o HH:MM
                        minuto_str = hora_parts[1] if len(hora_parts) > 1 else '0'
                        minuto = int(minuto_str.split('.')[0])  # Ignorar microsegundos si existen
                    else:
                        print(f"[DEBUG] Hora sin formato válido: {hora_cita}")
                        continue
                elif isinstance(hora_cita, time):
                    # Si es time object
                    hora_int = hora_cita.hour
                    minuto = hora_cita.minute
                elif hasattr(hora_cita, 'hour'):
                    # Otro tipo de objeto con atributo hour
                    hora_int = hora_cita.hour
                    minuto = hora_cita.minute
                else:
                    print(f"[DEBUG] Tipo de hora no reconocido: {type(hora_cita)}")
                    continue
                
                if hora_int is None or minuto is None:
                    print(f"[DEBUG] No se pudo extraer hora y minuto, saltando...")
                    continue
                
                # Formatear hora (ej: 07:00, 14:30)
                hora_simple = f"{hora_int:02d}:{minuto:02d}"
                print(f"[DEBUG] Hora formateada: {hora_simple}")
                horas_ocupadas.add(hora_simple)
                
                # Bloquear la hora siguiente (mínimo 1 hora entre citas)
                # Si hay una cita a las 10:00, bloquear 10:00, 10:30, 11:00 (pero NO 11:30)
                # Si hay una cita a las 10:30, bloquear 10:30, 11:00, 11:30 (pero NO 12:00)
                if minuto == 0:
                    # Hora en punto: bloquear esta hora, media hora después, y 1 hora después
                    horas_ocupadas.add(f"{hora_int:02d}:30")  # Media hora después
                    if hora_int < 16:
                        horas_ocupadas.add(f"{hora_int + 1:02d}:00")  # 1 hora después
                else:
                    # Media hora: bloquear esta hora, media hora después, y 1 hora después
                    if hora_int < 16:
                        horas_ocupadas.add(f"{hora_int + 1:02d}:00")  # Media hora después
                        horas_ocupadas.add(f"{hora_int + 1:02d}:30")  # 1 hora después
            
            print(f"[DEBUG] Horas ocupadas: {sorted(horas_ocupadas)}")
            
            # Filtrar horarios disponibles
            horarios_disponibles = [h for h in horarios_todos if h not in horas_ocupadas]
            
            print(f"[DEBUG] Horarios disponibles: {len(horarios_disponibles)}")
            print(f"[DEBUG] Primeros 5 disponibles: {horarios_disponibles[:5]}")
            
            return jsonify({'horarios': horarios_disponibles, 'ocupados': list(horas_ocupadas)})
        except Error as e:
            print(f"[ERROR] Error de BD obteniendo horarios: {e}")
            return jsonify({'error': 'Error de base de datos', 'horarios': []}), 500
        except ValueError as e:
            print(f"[ERROR] Error de formato obteniendo horarios: {e}")
            return jsonify({'error': 'Error de formato de datos', 'horarios': []}), 400
        except Exception as e:
            print(f"[ERROR] Error inesperado obteniendo horarios: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Error inesperado', 'horarios': []}), 500
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    print(f"[ERROR] Error cerrando conexión: {e}")
    except Exception as e:
        print(f"[ERROR] Error crítico en api_horarios_disponibles: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error crítico', 'horarios': []}), 500

@app.route('/citas', methods=['GET', 'POST'])
def citas():
    """
    Página para que los clientes agenden citas.
    
    Esta función maneja tanto mostrar el formulario (GET) como procesar
    el agendamiento (POST). Cuando se envía el formulario:
    1. Valida que el horario esté disponible (no haya otra cita muy cerca)
    2. Guarda la cita en la base de datos
    3. Envía un correo de confirmación automáticamente
    
    El sistema previene que se agenden dos citas con menos de 1 hora de diferencia.
    """
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos', 'danger')
        return render_template('citas.html', servicios=[])
    
    try:
        cursor = get_cursor(conn)
        
        # Obtener servicios disponibles desde la base de datos
        cursor.execute("SELECT * FROM servicios ORDER BY nombre")
        servicios = cursor.fetchall()
        
        if request.method == 'POST':
            nombre = request.form.get('nombre', '').strip()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            fecha = request.form.get('fecha', '').strip()
            hora = request.form.get('hora', '').strip()
            servicio_id = request.form.get('servicio_id', '').strip()
            
            if nombre and telefono and email and fecha and hora and servicio_id:
                try:
                    # Validar que el horario esté disponible
                    print(f"[DEBUG] ========== VALIDANDO CITA ==========")
                    print(f"[DEBUG] Fecha: {fecha}, Hora: {hora}")
                    
                    # Verificar si el horario está ocupado o muy cerca de otra cita
                    try:
                        hora_seleccionada = datetime.strptime(hora, '%H:%M').time()
                        print(f"[DEBUG] Hora seleccionada parseada: {hora_seleccionada}")
                    except ValueError:
                        flash('❌ Formato de hora inválido', 'danger')
                        return render_template('citas.html', servicios=servicios)
                    
                    # Consultar citas existentes para esa fecha
                    cursor.execute("SELECT id, hora FROM citas WHERE fecha = %s", (fecha,))
                    citas_existentes = cursor.fetchall()
                    print(f"[DEBUG] Citas existentes encontradas: {len(citas_existentes)}")
                    
                    hora_ocupada = False
                    conflicto_info = None
                    
                    for cita in citas_existentes:
                        hora_existente = cita['hora']
                        cita_id = cita['id']
                        print(f"[DEBUG] --- Comparando con cita ID {cita_id} ---")
                        print(f"[DEBUG] Hora existente (raw): {hora_existente}, tipo: {type(hora_existente)}")
                        
                        # Manejar diferentes formatos de hora
                        hora_existente_parsed = None
                        if isinstance(hora_existente, timedelta):
                            # Convertir timedelta a time
                            total_seconds = int(hora_existente.total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            hora_existente_parsed = time(hours, minutes)
                            print(f"[DEBUG] Hora convertida de timedelta a time: {hora_existente_parsed}")
                        elif isinstance(hora_existente, str):
                            # Intentar diferentes formatos
                            try:
                                # Limpiar la cadena (puede tener espacios o caracteres extra)
                                hora_limpia = hora_existente.strip()
                                if len(hora_limpia.split(':')) == 3:
                                    hora_existente_parsed = datetime.strptime(hora_limpia, '%H:%M:%S').time()
                                elif len(hora_limpia.split(':')) == 2:
                                    hora_existente_parsed = datetime.strptime(hora_limpia, '%H:%M').time()
                                else:
                                    print(f"[DEBUG] Formato de hora no reconocido: {hora_limpia}")
                                    continue
                            except ValueError as e:
                                print(f"[DEBUG] Error parseando hora existente '{hora_existente}': {e}")
                                continue
                        elif isinstance(hora_existente, time):
                            # Ya es un objeto time
                            hora_existente_parsed = hora_existente
                        elif hasattr(hora_existente, 'hour'):
                            # Otro tipo de objeto con atributo hour
                            hora_existente_parsed = hora_existente
                        else:
                            print(f"[DEBUG] Tipo de hora no reconocido: {type(hora_existente)}")
                            continue
                        
                        if hora_existente_parsed is None:
                            print(f"[DEBUG] No se pudo parsear la hora, saltando...")
                            continue
                        
                        print(f"[DEBUG] Hora existente parseada: {hora_existente_parsed}")
                        
                        # Calcular diferencia en minutos
                        minutos_seleccionada = hora_seleccionada.hour * 60 + hora_seleccionada.minute
                        minutos_existente = hora_existente_parsed.hour * 60 + hora_existente_parsed.minute
                        diff_minutos = abs(minutos_seleccionada - minutos_existente)
                        
                        print(f"[DEBUG] Diferencia: {diff_minutos} minutos")
                        print(f"[DEBUG] Seleccionada: {minutos_seleccionada} min, Existente: {minutos_existente} min")
                        
                        # Si hay menos de 60 minutos de diferencia, está ocupado
                        if diff_minutos < 60:
                            hora_ocupada = True
                            conflicto_info = f"Cita ID {cita_id} a las {hora_existente_parsed.strftime('%I:%M %p')}"
                            print(f"[DEBUG] ❌❌❌ CONFLICTO DETECTADO: {conflicto_info} ❌❌❌")
                            break
                        else:
                            print(f"[DEBUG] ✅ Sin conflicto (diferencia >= 60 min)")
                    
                    print(f"[DEBUG] ========== RESULTADO VALIDACIÓN ==========")
                    print(f"[DEBUG] Hora ocupada: {hora_ocupada}")
                    
                    if hora_ocupada:
                        mensaje = f'❌ El horario seleccionado ({hora_seleccionada.strftime("%I:%M %p")}) no está disponible. Ya existe una cita {conflicto_info if conflicto_info else "en ese horario"}. Por favor seleccione otro horario.'
                        print(f"[DEBUG] {mensaje}")
                        flash(mensaje, 'danger')
                        # NO continuar, retornar para que el usuario vea el error
                        return render_template('citas.html', servicios=servicios)
                    else:
                        print(f"[DEBUG] ✅ Horario disponible, procediendo a guardar la cita")
                        # Obtener nombre del servicio desde la base de datos
                        cursor.execute("SELECT nombre FROM servicios WHERE id = %s", (int(servicio_id),))
                        servicio_data = cursor.fetchone()
                        servicio_nombre = servicio_data['nombre'] if servicio_data else servicio_id
                        
                        sql = """INSERT INTO citas (nombre, telefono, email, fecha, hora, servicio, estatus) 
                                 VALUES (%s, %s, %s, %s, %s, %s, 'Pendiente')"""
                        cursor.execute(sql, (nombre, telefono, email, fecha, hora, servicio_nombre))
                        cita_id = cursor.lastrowid
                        conn.commit()
                        
                        # Enviar correo de confirmación automáticamente
                        try:
                            if enviar_confirmacion_cita(cita_id):
                                flash('✅ ¡Tu cita ha sido registrada con éxito! Se ha enviado un correo de confirmación.', 'success')
                            else:
                                flash('✅ ¡Tu cita ha sido registrada con éxito! No se pudo enviar el correo de confirmación.', 'warning')
                        except Exception as e:
                            print(f"Error al enviar correo de confirmación: {e}")
                            flash(f'✅ ¡Tu cita ha sido registrada con éxito! Error al enviar correo: {str(e)}', 'warning')
                        
                        return redirect(url_for('index'))
                except Error as e:
                    print(f"[ERROR] Error de BD al guardar cita: {e}")
                    import traceback
                    traceback.print_exc()
                    flash(f'❌ Error al guardar la cita: {str(e)}', 'danger')
                except ValueError as e:
                    print(f"[ERROR] Error de validación al guardar cita: {e}")
                    flash(f'❌ Error en los datos: {str(e)}', 'danger')
                except Exception as e:
                    print(f"[ERROR] Error inesperado al guardar cita: {e}")
                    import traceback
                    traceback.print_exc()
                    flash('❌ Error inesperado al guardar la cita. Por favor intenta más tarde.', 'danger')
            else:
                flash('Por favor complete todos los campos requeridos', 'warning')
        
        return render_template('citas.html', servicios=servicios)
    
    except Error as e:
        print(f"[ERROR] Error de BD en citas: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error de base de datos: {str(e)}', 'danger')
        return render_template('citas.html', servicios=[])
    except Exception as e:
        print(f"[ERROR] Error inesperado en citas: {e}")
        import traceback
        traceback.print_exc()
        flash('Error inesperado. Por favor intenta más tarde.', 'danger')
        return render_template('citas.html', servicios=[])
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[ERROR] Error cerrando conexión en citas: {e}")


# ============================================
# RUTAS DE AUTENTICACIÓN
# ============================================
# Estas rutas manejan el login y logout de usuarios.

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Página de inicio de sesión.
    
    Si es GET, muestra el formulario de login.
    Si es POST, verifica las credenciales:
    - Busca el usuario en la BD
    - Verifica la contraseña (soporta tanto hashes de Werkzeug como bcrypt de PHP)
    - Si es correcto, crea la sesión y redirige al dashboard apropiado (admin o usuario)
    - Si es incorrecto, muestra un mensaje de error
    
    Soporta verificación de contraseñas en formato PHP ($2y$) y Python ($2b$).
    """
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
                    
                    # Verificar contraseña
                    if usuario and usuario['password']:
                        password_valid = False
                        stored_hash = usuario['password']
                        
                        # Intentar verificar con Werkzeug (formato pbkdf2:sha256:...)
                        try:
                            password_valid = check_password_hash(stored_hash, password)
                        except (ValueError, TypeError):
                            # Si falla, puede ser un hash de PHP ($2y$...) o formato antiguo
                            # Intentar verificar con bcrypt directamente
                            try:
                                import bcrypt
                                # Si el hash empieza con $2y$ o $2b$, es bcrypt de PHP
                                if stored_hash.startswith('$2y$') or stored_hash.startswith('$2b$'):
                                    # Convertir $2y$ a $2b$ si es necesario (bcrypt de Python usa $2b$)
                                    hash_to_check = stored_hash.replace('$2y$', '$2b$', 1)
                                    password_valid = bcrypt.checkpw(password.encode('utf-8'), hash_to_check.encode('utf-8'))
                            except (ImportError, ValueError, TypeError):
                                password_valid = False
                        
                        if password_valid:
                            session['usuario_id'] = usuario['id']
                            session['username'] = usuario['username']
                            session['nombre'] = usuario['nombre']
                            session['rol'] = usuario['rol_nombre']
                            session['email'] = usuario.get('email', '')
                            
                            flash(f'Bienvenido, {usuario["nombre"]}', 'success')
                            
                            if usuario['rol_nombre'] == 'admin':
                                return redirect(url_for('admin_dashboard'))
                            else:
                                return redirect(url_for('user_dashboard'))
                        else:
                            flash('Usuario o contraseña incorrectos', 'danger')
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
    """
    Cerrar sesión del usuario.
    
    Simplemente limpia toda la información de la sesión y redirige
    a la página principal. Muy simple pero importante para seguridad.
    """
    session.clear()  # Eliminamos todos los datos de la sesión
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('index'))

# ============================================
# RUTAS DE USUARIO
# ============================================
# Estas rutas son para usuarios regulares (no admin).
# Requieren estar logueados (@login_required).

@app.route('/usuario')
@login_required
def user_dashboard():
    """
    Dashboard del usuario regular.
    
    Muestra un resumen de la actividad del usuario:
    - Total de citas agendadas
    - Total de cotizaciones solicitadas
    - Últimas 5 citas
    - Últimas 5 cotizaciones
    
    Todo esto basado en el email del usuario en sesión.
    """
    usuario_id = session.get('usuario_id')
    usuario_email = session.get('email', '')
    
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión', 'danger')
        return redirect(url_for('index'))
    
    try:
        cursor = get_cursor(conn)
        
        # Obtener estadísticas del usuario con manejo de errores individual
        total_citas = 0
        total_cotizaciones = 0
        ultimas_citas = []
        ultimas_cotizaciones = []
        
        try:
            # Contar citas del usuario (por email)
            cursor.execute("SELECT COUNT(*) as total FROM citas WHERE email = %s", (usuario_email,))
            result = cursor.fetchone()
            total_citas = result['total'] if result else 0
        except Error as e:
            print(f"[ERROR] Error contando citas del usuario: {e}")
            total_citas = 0
        
        try:
            # Contar cotizaciones del usuario (por email)
            cursor.execute("SELECT COUNT(*) as total FROM cotizaciones WHERE email = %s", (usuario_email,))
            result = cursor.fetchone()
            total_cotizaciones = result['total'] if result else 0
        except Error as e:
            print(f"[ERROR] Error contando cotizaciones del usuario: {e}")
            total_cotizaciones = 0
        
        try:
            # Obtener últimas citas
            cursor.execute("""SELECT * FROM citas 
                             WHERE email = %s 
                             ORDER BY fecha DESC, hora DESC 
                             LIMIT 5""", (usuario_email,))
            ultimas_citas = cursor.fetchall()
            
            # Convertir horas de timedelta a time
            for cita in ultimas_citas:
                try:
                    if isinstance(cita['hora'], timedelta):
                        total_seconds = int(cita['hora'].total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        cita['hora'] = time(hours, minutes)
                except Exception as e:
                    print(f"[ERROR] Error convirtiendo hora de cita: {e}")
        except Error as e:
            print(f"[ERROR] Error obteniendo últimas citas: {e}")
            ultimas_citas = []
        
        try:
            # Obtener últimas cotizaciones
            cursor.execute("""SELECT c.*, s.nombre as servicio_nombre 
                             FROM cotizaciones c 
                             LEFT JOIN servicios s ON c.servicio_id = s.id 
                             WHERE c.email = %s 
                             ORDER BY c.fecha_envio DESC 
                             LIMIT 5""", (usuario_email,))
            ultimas_cotizaciones = cursor.fetchall()
        except Error as e:
            print(f"[ERROR] Error obteniendo últimas cotizaciones: {e}")
            ultimas_cotizaciones = []
        
        return render_template('usuario/dashboard.html', 
                             total_citas=total_citas,
                             total_cotizaciones=total_cotizaciones,
                             ultimas_citas=ultimas_citas,
                             ultimas_cotizaciones=ultimas_cotizaciones)
    
    except Error as e:
        print(f"[ERROR] Error de BD en user_dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error de base de datos: {str(e)}', 'danger')
        return redirect(url_for('index'))
    except Exception as e:
        print(f"[ERROR] Error inesperado en user_dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash('Error inesperado. Por favor intenta más tarde.', 'danger')
        return redirect(url_for('index'))
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[ERROR] Error cerrando conexión en user_dashboard: {e}")

@app.route('/usuario/citas')
@login_required
def user_citas():
    """
    Página donde el usuario puede ver todas sus citas.
    
    Muestra todas las citas del usuario ordenadas por fecha y hora (más recientes primero).
    También muestra el estatus de cada cita (Pendiente, Confirmada, etc.).
    Las citas se identifican por el email del usuario en sesión.
    """
    usuario_email = session.get('email', '')
    
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión', 'danger')
        return redirect(url_for('user_dashboard'))
    
    try:
        cursor = get_cursor(conn)
        cursor.execute("""SELECT * FROM citas 
                         WHERE email = %s 
                         ORDER BY fecha DESC, hora DESC""", (usuario_email,))
        citas = cursor.fetchall()
        
        # Convertir horas de timedelta a time
        for cita in citas:
            try:
                if isinstance(cita['hora'], timedelta):
                    total_seconds = int(cita['hora'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    cita['hora'] = time(hours, minutes)
                elif isinstance(cita['hora'], str):
                    try:
                        if len(cita['hora'].split(':')) == 3:
                            cita['hora'] = datetime.strptime(cita['hora'], '%H:%M:%S').time()
                        else:
                            cita['hora'] = datetime.strptime(cita['hora'], '%H:%M').time()
                    except ValueError:
                        pass
            except Exception as e:
                print(f"[ERROR] Error convirtiendo hora en user_citas: {e}")
                continue
        
        return render_template('usuario/citas.html', citas=citas)
    
    except Error as e:
        print(f"[ERROR] Error de BD en user_citas: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error de base de datos: {str(e)}', 'danger')
        return redirect(url_for('user_dashboard'))
    except Exception as e:
        print(f"[ERROR] Error inesperado en user_citas: {e}")
        import traceback
        traceback.print_exc()
        flash('Error inesperado. Por favor intenta más tarde.', 'danger')
        return redirect(url_for('user_dashboard'))
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[ERROR] Error cerrando conexión en user_citas: {e}")

@app.route('/usuario/cotizaciones')
@login_required
def user_cotizaciones():
    """
    Página donde el usuario puede ver todas sus cotizaciones.
    
    Muestra todas las cotizaciones que el usuario ha solicitado,
    ordenadas por fecha (más recientes primero).
    Incluye el servicio, vehículo, precio calculado y fecha.
    Las cotizaciones se identifican por el email del usuario en sesión.
    """
    usuario_email = session.get('email', '')
    
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión', 'danger')
        return redirect(url_for('user_dashboard'))
    
    try:
        cursor = get_cursor(conn)
        cursor.execute("""SELECT c.*, s.nombre as servicio_nombre 
                         FROM cotizaciones c 
                         LEFT JOIN servicios s ON c.servicio_id = s.id 
                         WHERE c.email = %s 
                         ORDER BY c.fecha_envio DESC""", (usuario_email,))
        cotizaciones = cursor.fetchall()
        
        return render_template('usuario/cotizaciones.html', cotizaciones=cotizaciones)
    
    except Error as e:
        print(f"[ERROR] Error de BD en user_cotizaciones: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error de base de datos: {str(e)}', 'danger')
        return redirect(url_for('user_dashboard'))
    except Exception as e:
        print(f"[ERROR] Error inesperado en user_cotizaciones: {e}")
        import traceback
        traceback.print_exc()
        flash('Error inesperado. Por favor intenta más tarde.', 'danger')
        return redirect(url_for('user_dashboard'))
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[ERROR] Error cerrando conexión en user_cotizaciones: {e}")

# ============================================
# RUTAS ADMINISTRATIVAS
# ============================================
# Estas rutas son solo para administradores.
# Requieren estar logueados Y ser admin (@admin_required).

@app.route('/admin')
@admin_required
def admin_dashboard():
    """
    Dashboard del administrador.
    
    Muestra estadísticas generales del sistema:
    - Total de usuarios activos
    - Total de servicios
    - Total de citas
    - Total de cotizaciones
    
    Cada estadística tiene su propio try-except para que si una tabla
    no existe, no crashee todo el dashboard.
    """
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos', 'danger')
        return redirect(url_for('index'))
    
    try:
        cursor = get_cursor(conn)
        
        # Estadísticas con manejo de errores individual
        stats = {
            'usuarios': 0,
            'servicios': 0,
            'citas': 0,
            'cotizaciones': 0
        }
        
        try:
            cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE activo = 1")
            result = cursor.fetchone()
            stats['usuarios'] = result['total'] if result else 0
        except Error:
            stats['usuarios'] = 0
        
        try:
            cursor.execute("SELECT COUNT(*) as total FROM servicios")
            result = cursor.fetchone()
            stats['servicios'] = result['total'] if result else 0
        except Error:
            stats['servicios'] = 0
        
        try:
            cursor.execute("SELECT COUNT(*) as total FROM citas")
            result = cursor.fetchone()
            stats['citas'] = result['total'] if result else 0
        except Error:
            stats['citas'] = 0
        
        try:
            cursor.execute("SELECT COUNT(*) as total FROM cotizaciones")
            result = cursor.fetchone()
            stats['cotizaciones'] = result['total'] if result else 0
        except Error:
            stats['cotizaciones'] = 0
        
        return render_template('admin/dashboard.html', stats=stats)
    except Error as e:
        print(f"[ERROR] Error de BD en admin_dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error de base de datos: {str(e)}. Por favor ejecuta el script SQL para crear las tablas faltantes.', 'danger')
        return redirect(url_for('index'))
    except Exception as e:
        print(f"[ERROR] Error inesperado en admin_dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error al cargar estadísticas: {str(e)}. Por favor ejecuta el script SQL para crear las tablas faltantes.', 'danger')
        return redirect(url_for('index'))
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[ERROR] Error cerrando conexión en admin_dashboard: {e}")

@app.route('/admin/usuarios', methods=['GET', 'POST'])
@admin_required
def admin_usuarios():
    """
    Gestión completa de usuarios (CRUD).
    
    Permite al administrador:
    - Crear nuevos usuarios (si es admin, requiere email y envía correo de bienvenida)
    - Editar usuarios existentes (nombre, email, teléfono, rol, activo/inactivo)
    - Eliminar usuarios (no puede eliminar su propio usuario)
    - Cambiar contraseñas de usuarios
    
    Si se crea un usuario admin con email, se envía automáticamente un correo
    de bienvenida con sus credenciales.
    """
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
                    # Si es admin, el correo es obligatorio
                    if rol_id == 1 and not email:
                        flash('El correo electrónico es obligatorio para usuarios administradores', 'warning')
                    else:
                        password_hash = generate_password_hash(password)
                        sql = """INSERT INTO usuarios (username, password, nombre, email, telefono, rol_id) 
                                 VALUES (%s, %s, %s, %s, %s, %s)"""
                        cursor.execute(sql, (username, password_hash, nombre, email, telefono, rol_id))
                        usuario_id = cursor.lastrowid
                        conn.commit()
                        
                        # Si es admin y tiene correo, enviar correo de bienvenida
                        if rol_id == 1 and email:
                            try:
                                enviar_correo_bienvenida_admin(email, nombre, username, password)
                                flash('Usuario creado exitosamente. Correo de bienvenida enviado.', 'success')
                            except Exception as e:
                                print(f"Error enviando correo: {e}")
                                flash('Usuario creado exitosamente, pero no se pudo enviar el correo de bienvenida', 'warning')
                        else:
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
    
    except ValueError as e:
        print(f"[ERROR] Error de validación en admin_usuarios: {e}")
        flash(f'Error en los datos ingresados: {str(e)}', 'danger')
        return redirect(url_for('admin_usuarios'))
    except Error as e:
        print(f"[ERROR] Error de BD en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error de base de datos: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"[ERROR] Error inesperado en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash('Error inesperado. Por favor intenta más tarde.', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[ERROR] Error cerrando conexión en admin_usuarios: {e}")

@app.route('/admin/servicios', methods=['GET', 'POST'])
@admin_required
def admin_servicios():
    """
    Gestión de servicios ofrecidos por el taller (CRUD).
    
    Permite al administrador:
    - Crear nuevos servicios (nombre y descripción)
    - Editar servicios existentes
    - Eliminar servicios
    
    Los servicios son los que aparecen en las cotizaciones y citas.
    """
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
    
    except ValueError as e:
        print(f"[ERROR] Error de validación en admin_usuarios: {e}")
        flash(f'Error en los datos ingresados: {str(e)}', 'danger')
        return redirect(url_for('admin_usuarios'))
    except Error as e:
        print(f"[ERROR] Error de BD en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error de base de datos: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"[ERROR] Error inesperado en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash('Error inesperado. Por favor intenta más tarde.', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[ERROR] Error cerrando conexión en admin_usuarios: {e}")

@app.route('/admin/roles', methods=['GET', 'POST'])
@admin_required
def admin_roles():
    """
    Gestión de roles del sistema (CRUD).
    
    Permite al administrador:
    - Crear nuevos roles (nombre y descripción)
    - Editar roles existentes
    - Eliminar roles (solo si no hay usuarios asignados a ese rol)
    
    Los roles definen los permisos de los usuarios (admin, usuario, etc.).
    """
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
    
    except ValueError as e:
        print(f"[ERROR] Error de validación en admin_usuarios: {e}")
        flash(f'Error en los datos ingresados: {str(e)}', 'danger')
        return redirect(url_for('admin_usuarios'))
    except Error as e:
        print(f"[ERROR] Error de BD en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error de base de datos: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"[ERROR] Error inesperado en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash('Error inesperado. Por favor intenta más tarde.', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[ERROR] Error cerrando conexión en admin_usuarios: {e}")

@app.route('/admin/precios', methods=['GET', 'POST'])
@admin_required
def admin_precios():
    """
    Gestión de precios personalizados de servicios (CRUD).
    
    Esta es una de las partes más complejas. Permite configurar precios
    que varían según:
    - El servicio
    - El rango de cilindros (ej: 4-6 cilindros)
    - El rango de años (ej: 2010-2020, opcional)
    
    Cada configuración tiene:
    - precio_base: precio inicial
    - precio_por_cilindro: cuanto se suma por cada cilindro
    - precio_por_anio: cuanto se suma por cada año (opcional)
    
    El precio final se calcula: base + (cilindros * precio_por_cilindro) + (año * precio_por_anio)
    """
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = get_cursor(conn)
        
        if request.method == 'POST':
            accion = request.form.get('accion', '')
            
            if accion == 'crear':
                servicio_id = int(request.form.get('servicio_id', 0))
                cilindros_min = int(request.form.get('cilindros_min', 0))
                cilindros_max = int(request.form.get('cilindros_max', 0))
                anio_min = request.form.get('anio_min', '').strip()
                anio_max = request.form.get('anio_max', '').strip()
                precio_base = float(request.form.get('precio_base', 0))
                precio_por_cilindro = float(request.form.get('precio_por_cilindro', 0))
                precio_por_anio = float(request.form.get('precio_por_anio', 0))
                
                anio_min_int = int(anio_min) if anio_min else None
                anio_max_int = int(anio_max) if anio_max else None
                
                sql = """INSERT INTO servicio_precios 
                         (servicio_id, cilindros_min, cilindros_max, anio_min, anio_max, 
                          precio_base, precio_por_cilindro, precio_por_anio) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    servicio_id, cilindros_min, cilindros_max, anio_min_int, anio_max_int,
                    precio_base, precio_por_cilindro, precio_por_anio
                ))
                conn.commit()
                flash('Precio creado exitosamente', 'success')
            
            elif accion == 'editar':
                precio_id = int(request.form.get('id', 0))
                servicio_id = int(request.form.get('servicio_id', 0))
                cilindros_min = int(request.form.get('cilindros_min', 0))
                cilindros_max = int(request.form.get('cilindros_max', 0))
                anio_min = request.form.get('anio_min', '').strip()
                anio_max = request.form.get('anio_max', '').strip()
                precio_base = float(request.form.get('precio_base', 0))
                precio_por_cilindro = float(request.form.get('precio_por_cilindro', 0))
                precio_por_anio = float(request.form.get('precio_por_anio', 0))
                activo = 1 if request.form.get('activo') else 0
                
                anio_min_int = int(anio_min) if anio_min else None
                anio_max_int = int(anio_max) if anio_max else None
                
                sql = """UPDATE servicio_precios 
                         SET servicio_id = %s, cilindros_min = %s, cilindros_max = %s, 
                             anio_min = %s, anio_max = %s, precio_base = %s, 
                             precio_por_cilindro = %s, precio_por_anio = %s, activo = %s
                         WHERE id = %s"""
                cursor.execute(sql, (
                    servicio_id, cilindros_min, cilindros_max, anio_min_int, anio_max_int,
                    precio_base, precio_por_cilindro, precio_por_anio, activo, precio_id
                ))
                conn.commit()
                flash('Precio actualizado exitosamente', 'success')
            
            elif accion == 'eliminar':
                precio_id = int(request.form.get('id', 0))
                cursor.execute("DELETE FROM servicio_precios WHERE id = %s", (precio_id,))
                conn.commit()
                flash('Precio eliminado exitosamente', 'success')
        
        # Obtener servicios y precios
        cursor.execute("SELECT * FROM servicios ORDER BY nombre")
        servicios = cursor.fetchall()
        
        cursor.execute("""SELECT sp.*, s.nombre as servicio_nombre 
                          FROM servicio_precios sp 
                          INNER JOIN servicios s ON sp.servicio_id = s.id 
                          ORDER BY s.nombre, sp.cilindros_min""")
        precios = cursor.fetchall()
        
        return render_template('admin/precios.html', servicios=servicios, precios=precios)
    
    except ValueError as e:
        print(f"[ERROR] Error de validación en admin_usuarios: {e}")
        flash(f'Error en los datos ingresados: {str(e)}', 'danger')
        return redirect(url_for('admin_usuarios'))
    except Error as e:
        print(f"[ERROR] Error de BD en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error de base de datos: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"[ERROR] Error inesperado en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash('Error inesperado. Por favor intenta más tarde.', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e: 
                print(f"[ERROR] Error cerrando conexión en admin_usuarios: {e}")

# ============================================
# FUNCIONES DE CORREO
# ============================================
# Estas funciones manejan el envío de correos electrónicos.
# Usan Flask-Mail y templates HTML para los correos.

def enviar_correo_bienvenida_admin(email, nombre, username, password):
    """
    Envía un correo de bienvenida cuando se crea un nuevo usuario admin.
    
    El correo incluye:
    - Mensaje de bienvenida personalizado
    - Username y contraseña para que pueda iniciar sesión
    - Información sobre el sistema
    
    Se usa cuando un administrador crea otro usuario admin.
    """
    try:
        msg = Message(
            subject='Bienvenido al Sistema de Taller Automotriz',
            recipients=[email],
            html=render_template('emails/bienvenida_admin.html',
                              nombre=nombre,
                              username=username,
                              password=password)
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error enviando correo de bienvenida: {e}")
        return False

def enviar_confirmacion_cita(cita_id):
    """
    Envía un correo de confirmación cuando se agenda una cita.
    
    Esta función se llama automáticamente después de que se guarda una cita.
    El correo incluye:
    - Detalles de la cita (fecha, hora, servicio)
    - Información de contacto del taller
    - Ubicación del taller
    
    Maneja la conversión de timedelta a time porque MySQL a veces retorna
    las horas como timedelta en lugar de time objects.
    """
    print(f"[DEBUG] ========== ENVIANDO CORREO DE CONFIRMACIÓN ==========")
    print(f"[DEBUG] Cita ID: {cita_id}")
    
    conn = get_db_connection()
    if not conn:
        print("[ERROR] No se pudo conectar a la base de datos para enviar correo de confirmación")
        return False
    
    try:
        cursor = get_cursor(conn)
        cursor.execute("SELECT * FROM citas WHERE id = %s", (cita_id,))
        cita = cursor.fetchone()
        
        if not cita:
            print(f"[ERROR] No se encontró la cita con ID {cita_id}")
            return False
        
        print(f"[DEBUG] Cita encontrada: {cita}")
        
        # Convertir hora de timedelta a time si es necesario
        if isinstance(cita['hora'], timedelta):
            # Convertir timedelta a time
            total_seconds = int(cita['hora'].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            cita['hora'] = time(hours, minutes)
            print(f"[DEBUG] Hora convertida de timedelta a time: {cita['hora']}")
        elif isinstance(cita['hora'], str):
            # Si es string, parsear
            try:
                if len(cita['hora'].split(':')) == 3:
                    cita['hora'] = datetime.strptime(cita['hora'], '%H:%M:%S').time()
                else:
                    cita['hora'] = datetime.strptime(cita['hora'], '%H:%M').time()
                print(f"[DEBUG] Hora convertida de string a time: {cita['hora']}")
            except ValueError as e:
                print(f"[DEBUG] Error parseando hora string: {e}")
        elif not isinstance(cita['hora'], time):
            # Si no es time, intentar convertir
            print(f"[DEBUG] Tipo de hora inesperado: {type(cita['hora'])}, valor: {cita['hora']}")
        
        if not cita['email']:
            print(f"[ERROR] La cita {cita_id} no tiene correo electrónico")
            return False
        
        email_destino = cita['email'].strip()
        print(f"[INFO] Enviando correo de confirmación a {email_destino} para cita {cita_id}")
        
        # Verificar configuración de correo
        if not app.config.get('MAIL_SERVER'):
            print("[ERROR] MAIL_SERVER no está configurado")
            return False
        
        try:
            msg = Message(
                subject=f'Confirmación de Cita - {cita["servicio"]}',
                recipients=[email_destino],
                html=render_template('emails/confirmacion_cita.html', cita=cita)
            )
            print(f"[DEBUG] Mensaje creado, enviando...")
            mail.send(msg)
            print(f"[SUCCESS] ✅ Correo de confirmación enviado exitosamente a {email_destino}")
            return True
        except Exception as mail_error:
            print(f"[ERROR] Error al enviar el mensaje de correo: {mail_error}")
            import traceback
            traceback.print_exc()
            return False
    except Exception as e:
        print(f"[ERROR] Error enviando confirmación de cita por correo: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

def enviar_cotizacion_por_correo(cotizacion_id):
    """
    Envía un correo con los detalles de una cotización al cliente.
    
    Esta función se llama automáticamente cuando se crea una cotización,
    o manualmente desde el panel de administración.
    El correo incluye:
    - Detalles del servicio cotizado
    - Información del vehículo
    - Precio calculado
    - Fecha de la cotización
    """
    conn = get_db_connection()
    if not conn:
        print("[ERROR] No se pudo conectar a la base de datos para enviar correo")
        return False
    
    try:
        cursor = get_cursor(conn)
        cursor.execute("""SELECT c.*, s.nombre as servicio_nombre 
                          FROM cotizaciones c 
                          LEFT JOIN servicios s ON c.servicio_id = s.id 
                          WHERE c.id = %s""", (cotizacion_id,))
        cotizacion = cursor.fetchone()
        
        if not cotizacion:
            print(f"[ERROR] No se encontró la cotización con ID {cotizacion_id}")
            return False
        
        if not cotizacion['email']:
            print(f"[ERROR] La cotización {cotizacion_id} no tiene correo electrónico")
            return False
        
        print(f"[INFO] Enviando correo a {cotizacion['email']} para cotización {cotizacion_id}")
        
        msg = Message(
            subject=f'Cotización de Servicio - {cotizacion["servicio_nombre"] or "Servicio"}',
            recipients=[cotizacion['email']],
            html=render_template('emails/cotizacion.html', cotizacion=cotizacion)
        )
        mail.send(msg)
        print(f"[SUCCESS] Correo enviado exitosamente a {cotizacion['email']}")
        return True
    except Exception as e:
        print(f"[ERROR] Error enviando cotización por correo: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

@app.route('/admin/cotizaciones', methods=['GET', 'POST'])
@admin_required
def admin_cotizaciones():
    """
    Panel de administración para ver y gestionar todas las cotizaciones.
    
    Permite al administrador:
    - Ver todas las cotizaciones solicitadas por los clientes
    - Enviar cotizaciones por correo manualmente (si no se envió automáticamente)
    
    Muestra información completa: cliente, contacto, servicio, vehículo, precio, fecha.
    """
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = get_cursor(conn)
        
        if request.method == 'POST':
            accion = request.form.get('accion', '')
            
            if accion == 'enviar_correo':
                cotizacion_id = int(request.form.get('id', 0))
                if enviar_cotizacion_por_correo(cotizacion_id):
                    flash('Cotización enviada por correo exitosamente', 'success')
                else:
                    flash('Error al enviar la cotización por correo', 'danger')
        
        # Obtener cotizaciones
        cursor.execute("""SELECT c.*, s.nombre as servicio_nombre 
                         FROM cotizaciones c 
                         LEFT JOIN servicios s ON c.servicio_id = s.id 
                         ORDER BY c.fecha_envio DESC""")
        cotizaciones = cursor.fetchall()
        
        return render_template('admin/cotizaciones.html', cotizaciones=cotizaciones)
    
    except ValueError as e:
        print(f"[ERROR] Error de validación en admin_usuarios: {e}")
        flash(f'Error en los datos ingresados: {str(e)}', 'danger')
        return redirect(url_for('admin_usuarios'))
    except Error as e:
        print(f"[ERROR] Error de BD en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error de base de datos: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"[ERROR] Error inesperado en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash('Error inesperado. Por favor intenta más tarde.', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[ERROR] Error cerrando conexión en admin_usuarios: {e}")

@app.route('/admin/citas', methods=['GET', 'POST'])
@admin_required
def admin_citas():
    """
    Panel de administración para gestionar todas las citas.
    
    Permite al administrador:
    - Ver todas las citas agendadas
    - Cambiar el estatus de las citas (Pendiente, Confirmada, En proceso, Completada, Cancelada)
    - Eliminar citas
    
    Las citas se muestran ordenadas por fecha y hora (más recientes primero).
    El estatus se puede cambiar directamente desde la tabla usando un dropdown.
    """
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = get_cursor(conn)
        
        if request.method == 'POST':
            accion = request.form.get('accion', '')
            
            if accion == 'eliminar':
                cita_id = int(request.form.get('id', 0))
                try:
                    cursor.execute("DELETE FROM citas WHERE id = %s", (cita_id,))
                    conn.commit()
                    flash('Cita eliminada exitosamente', 'success')
                except Error as e:
                    flash(f'Error al eliminar la cita: {str(e)}', 'danger')
            elif accion == 'cambiar_estatus':
                cita_id = int(request.form.get('id', 0))
                nuevo_estatus = request.form.get('estatus', 'Pendiente').strip()
                try:
                    cursor.execute("UPDATE citas SET estatus = %s WHERE id = %s", (nuevo_estatus, cita_id))
                    conn.commit()
                    flash(f'Estatus de la cita actualizado a: {nuevo_estatus}', 'success')
                except Error as e:
                    flash(f'Error al actualizar el estatus: {str(e)}', 'danger')
        
        # Obtener citas ordenadas por fecha y hora
        cursor.execute("""SELECT * FROM citas 
                         ORDER BY fecha DESC, hora DESC""")
        citas = cursor.fetchall()
        
        # Convertir horas de timedelta a time si es necesario
        for cita in citas:
            if isinstance(cita['hora'], timedelta):
                # Convertir timedelta a time
                total_seconds = int(cita['hora'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                cita['hora'] = time(hours, minutes)
            elif isinstance(cita['hora'], str):
                # Si es string, parsear
                try:
                    if len(cita['hora'].split(':')) == 3:
                        cita['hora'] = datetime.strptime(cita['hora'], '%H:%M:%S').time()
                    else:
                        cita['hora'] = datetime.strptime(cita['hora'], '%H:%M').time()
                except ValueError:
                    pass  # Mantener como string si no se puede parsear
        
        return render_template('admin/citas.html', citas=citas)
    
    except ValueError as e:
        print(f"[ERROR] Error de validación en admin_usuarios: {e}")
        flash(f'Error en los datos ingresados: {str(e)}', 'danger')
        return redirect(url_for('admin_usuarios'))
    except Error as e:
        print(f"[ERROR] Error de BD en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error de base de datos: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"[ERROR] Error inesperado en admin_usuarios: {e}")
        import traceback
        traceback.print_exc()
        flash('Error inesperado. Por favor intenta más tarde.', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[ERROR] Error cerrando conexión en admin_usuarios: {e}")

# ============================================
# PUNTO DE ENTRADA DE LA APLICACIÓN
# ============================================
# Esto solo se ejecuta si ejecutamos este archivo directamente
# (no si lo importamos como módulo)

if __name__ == '__main__':
    # Iniciamos el servidor Flask
    # debug=True: activa el modo debug (muestra errores detallados, recarga automática)
    # host='0.0.0.0': hace que el servidor sea accesible desde cualquier IP (útil para desarrollo en red)
    # port=5000: el puerto donde corre el servidor
    app.run(debug=True, host='0.0.0.0', port=5000)

