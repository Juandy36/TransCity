from flask import Flask, render_template, request, redirect, url_for, session
from db import db, db_init
from models import Usuario
import config

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transcity.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = config.SECRET_KEY  # Clave secreta para sesiones

# Inicializar la base de datos
db_init(app)

# Función para verificar si el usuario está logueado
def esta_logueado():
    return 'usuario_id' in session

@app.route('/')
def index():
    if not esta_logueado():  # Si no está logueado, redirigir al login
        return redirect(url_for('login'))

    rol = session.get('rol', 'cliente')
    return render_template('index.html', rol=rol)

@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    if not esta_logueado():
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        nuevo_usuario = Usuario(nombre=nombre, correo=correo, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('usuarios'))

    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        rol = 'cliente'  # Rol por defecto

        nuevo_usuario = Usuario(nombre=nombre, correo=correo, password=password, rol=rol)

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return f"Hubo un error al registrar: {e}"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        usuario = Usuario.query.filter_by(correo=correo, password=password).first()
        if usuario:
            session['usuario_id'] = usuario.id
            session['nombre'] = usuario.nombre
            session['rol'] = usuario.rol if usuario.rol else 'cliente'
            return redirect(url_for('index'))
        else:
            return "Correo o password incorrectos. Intenta de nuevo."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)  # Eliminar 'usuario_id' de la sesión
    session.pop('nombre', None)
    session.pop('rol', None)
    return redirect(url_for('login'))

@app.route('/usuarios/eliminar', methods=['POST'])
def eliminar_usuario():
    usuario_id = request.form.get('usuario_id')  # Obtener el ID del usuario desde el formulario
    usuario = Usuario.query.get(usuario_id)  # Buscar el usuario en la base de datos
    if usuario:
        db.session.delete(usuario)  # Eliminar el usuario
        db.session.commit()  # Guardar los cambios en la base de datos
    return redirect(url_for('usuarios'))  # Redirigir a la página de usuarios


@app.route('/usuarios/asignar_rol', methods=['POST'])
def asignar_rol():
    usuario_id = request.form.get('usuario_id')  # Obtener el ID del usuario desde el formulario
    nuevo_rol = request.form.get('rol')  # Obtener el nuevo rol desde el formulario
    usuario = Usuario.query.get(usuario_id)  # Buscar el usuario en la base de datos
    if usuario:
        usuario.rol = nuevo_rol  # Asignar el nuevo rol
        db.session.commit()  # Guardar los cambios en la base de datos
    return redirect(url_for('usuarios'))  # Redirigir a la página de usuarios



if __name__ == '__main__':
    app.run(debug=True)
