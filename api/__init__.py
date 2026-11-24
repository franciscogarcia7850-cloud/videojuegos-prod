from flask import Blueprint
from flask_restful import Api

# Blueprint para tener las rutas de la API separadas de las paginas normales
api_bp = Blueprint('api', __name__)

# Aqui se van agregando los recursos de la API (estan en routes.py)
api = Api(api_bp)

# Se importa al final porque routes.py necesita que api ya exista
from . import routes
