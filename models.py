from db import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(50), default="cliente")

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)

class Ruta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origen = db.Column(db.String(100), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    duración = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)

class Horario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    ruta_id = db.Column(db.Integer, db.ForeignKey('ruta.id'), nullable=False)
    fecha_hora_salida = db.Column(db.String(50), nullable=False)
    fecha_hora_llegada = db.Column(db.String(50), nullable=False)

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey('horario.id'), nullable=False)
    asiento = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(50), default="confirmada")

class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reserva.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    método = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
