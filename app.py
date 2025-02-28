from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from itsdangerous import URLSafeTimedSerializer as Serializer
from models import Usuario
from db import db, db_init
from config import keys  

app = Flask(__name__)

# Cargar configuración desde la clase Config
app.config.from_object(keys)

# Resto de configuraciones (no secretas)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transcity.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db_init(app)

# Serializador (usa la SECRET_KEY de la configuración)
serializer = Serializer(app.config['SECRET_KEY'], salt='password-reset-salt')

# Configuración de Google OAuth (usa las variables de la configuración)
google_bp = make_google_blueprint(
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    redirect_to='google_login_callback',
    scope=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"]
)
app.register_blueprint(google_bp, url_prefix="/google_login")

# ... el resto de tu código permanece igual ...
# Función para verificar si el usuario está logueado
def esta_logueado():
    return 'usuario_id' in session

# Ruta principal
@app.route('/')
def index():
    if not esta_logueado():
        return redirect(url_for('login'))
    rol = session.get('rol', 'cliente')
    return render_template('index.html', rol=rol)

# Ruta para login con Google
@app.route('/login_google')
def login_google():
    return redirect(url_for('google.login'))

# Callback de Google OAuth
@app.route('/google_login/callback')
def google_login_callback():
    if esta_logueado():
        return redirect(url_for('index'))

    if not google.authorized:
        return redirect(url_for('google.login'))

    resp = google.get('https://www.googleapis.com/oauth2/v3/userinfo')
    if not resp.ok:
        flash("Error al obtener información de Google. Intenta nuevamente.", "error")
        return redirect(url_for('login'))

    user_info = resp.json()
    print("Respuesta de Google:", user_info)  # Depuración

    if 'email' not in user_info:
        flash("Error: Google no proporcionó un email.", "error")
        return redirect(url_for('login'))

    usuario = Usuario.query.filter_by(correo=user_info['email']).first()

    if not usuario:
        usuario = Usuario(
            nombre=user_info.get('name', 'Usuario sin nombre'),
            correo=user_info['email'],
            password='',  # No se usa password con Google
            rol='cliente'
        )
        db.session.add(usuario)
        db.session.commit()

    # Iniciar sesión
    session['usuario_id'] = usuario.id
    session['nombre'] = usuario.nombre
    session['rol'] = usuario.rol
    return redirect(url_for('index'))

# Ruta de registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']  # Guardar en texto plano
        rol = 'cliente'
        nuevo_usuario = Usuario(nombre=nombre, correo=correo, password=password, rol=rol)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario and usuario.password == password:  # Comparación en texto plano
            session['usuario_id'] = usuario.id
            session['nombre'] = usuario.nombre
            session['rol'] = usuario.rol
            return redirect(url_for('index'))
        else:
            flash("Correo o password incorrectos. Intenta de nuevo.", "error")
    return render_template('login.html')

# Ruta de logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
@app.route('/contacto')
def contacto():
    return render_template('contacto.html')
    
@app.route('/usuarios')
def usuarios():
    if not esta_logueado():
        return redirect(url_for('login'))
    
    lista_usuarios = Usuario.query.all()  # Obtiene todos los usuarios de la BD
    return render_template('usuarios.html', usuarios=lista_usuarios)

if __name__ == '__main__':
    app.run(debug=True)
