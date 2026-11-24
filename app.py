import os, logging, sentry_sdk

from flask import Flask, render_template, request, redirect, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from werkzeug.exceptions import HTTPException
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(dsn=os.environ.get('SENTRY_DSN'), integrations=[FlaskIntegration()])

app = Flask(__name__)
file_handler = logging.FileHandler(os.path.join(app.root_path, 'errors.log'))
file_handler.setLevel(logging.ERROR)
app.logger.addHandler(file_handler)

if os.environ.get('FLASK_CONFIG') == 'testing':
    app.config['SECRET_KEY'] = 'clave-de-pruebas'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Para que los acentos se vean bien en el JSON de la API
app.config['RESTFUL_JSON'] = {'ensure_ascii': False}
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'
login_manager.login_message = 'Tienes que ingresar para ver esta página'
login_manager.login_message_category = 'warning'

import controllers
from auth import auth as auth_blueprint

app.register_blueprint(auth_blueprint, url_prefix='/auth')

# La API va en la carpeta api/ y todas sus rutas empiezan con /api
from api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

with app.app_context():
    db.create_all()


@app.route("/")
@app.route("/juegos")
@login_required
def juegos():
    juegos = controllers.obtener_juegos()
    return render_template("juegos.html", juegos=juegos)

@app.route("/agregar_juego")
@login_required
def formulario_agregar_juego():
    return render_template("agregar_juego.html")

@app.route("/guardar_juego", methods=["POST"])
@login_required
def guardar_juego():
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    controllers.insertar_juego(nombre, descripcion, precio)
    return redirect("/juegos")

@app.route("/formulario_editar_juego/<int:id>")
@login_required
def editar_juego(id):
    juego = controllers.obtener_juego_por_id(id)
    return render_template("editar_juego.html", juego=juego)

@app.route("/actualizar_juego", methods=["POST"])
@login_required
def actualizar_juego():
    id = request.form["id"]
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    controllers.actualizar_juego(nombre, descripcion, precio, id)
    return redirect("/juegos")

@app.route("/eliminar_juego", methods=["POST"])
@login_required
def eliminar_juego():
    controllers.eliminar_juego(request.form["id"])
    return redirect("/juegos")

@app.errorhandler(HTTPException)
def handle_api_error(e):
    if request.path.startswith('/api/'):
        response = e.get_response()
        response.data = jsonify(code=e.code, name=e.name, description=e.description).data
        response.content_type = 'application/json'
        return response
    return e

@app.errorhandler(400)
def handle_400(e):
    return render_template('400.html', error=e), 400

@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html'), 404

@app.errorhandler(405)
def handle_405(e):
    return render_template('405.html', error=e), 405

@app.errorhandler(500)
def handle_500(e):
    return render_template('500.html'), 500

#forzar errores
@app.route("/forzar_error")
def forzar_error():
    return 1 / 0

@app.route("/videogame")
@app.route("/videogame/<int:id>")
@login_required
def ver_juego(id=None):
    if id is None:
        abort(400, description="Falta el id del videojuego. Ejemplo: /videogame/1")
    juego = controllers.obtener_juego_por_id(id)
    if juego is None:
        abort(404)
    return render_template("editar_juego.html", juego=juego)
