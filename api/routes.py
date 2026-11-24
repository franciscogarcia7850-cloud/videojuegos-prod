from flask_restful import Resource, reqparse, fields, marshal_with, abort

from app import db
from models import Juego
from . import api

# Los datos de cada juego que se van a mostrar en el JSON.
# El precio lo pongo como Float para que salga como numero.
juego_fields = {
    'id': fields.Integer,
    'nombre': fields.String,
    'descripcion': fields.String,
    'precio': fields.Float,
}

# Los datos que pido para crear o editar un juego.
# Si falta alguno, la API responde 400 con el mensaje de help.
parser = reqparse.RequestParser()
parser.add_argument('nombre', type=str, required=True, help='Falta el nombre del juego')
parser.add_argument('descripcion', type=str, required=True, help='Falta la descripcion del juego')
parser.add_argument('precio', type=float, required=True, help='El precio es obligatorio y debe ser un numero')


def buscar_juego(id):
    # Busca el juego por su id, si no existe responde 404
    juego = db.session.get(Juego, id)
    if juego is None:
        abort(404, message=f'No existe un juego con el id {id}')
    return juego


# Ruta: /api/juegos
class JuegoList(Resource):

    # GET /api/juegos -> regresa la lista de todos los juegos (200)
    @marshal_with(juego_fields)
    def get(self):
        return Juego.query.all()

    # POST /api/juegos -> crea un juego nuevo con el JSON que se manda (201)
    @marshal_with(juego_fields)
    def post(self):
        datos = parser.parse_args()
        juego = Juego(nombre=datos['nombre'], descripcion=datos['descripcion'], precio=datos['precio'])
        db.session.add(juego)
        db.session.commit()
        return juego, 201


# Ruta: /api/juegos/<id>
class JuegoResource(Resource):

    # GET /api/juegos/1 -> regresa un solo juego (200) o 404 si no existe
    @marshal_with(juego_fields)
    def get(self, id):
        return buscar_juego(id)

    # PUT /api/juegos/1 -> cambia los datos de un juego (200) o 404 si no existe
    @marshal_with(juego_fields)
    def put(self, id):
        juego = buscar_juego(id)
        datos = parser.parse_args()
        juego.nombre = datos['nombre']
        juego.descripcion = datos['descripcion']
        juego.precio = datos['precio']
        db.session.commit()
        return juego

    # DELETE /api/juegos/1 -> borra el juego y no regresa nada (204) o 404 si no existe
    def delete(self, id):
        juego = buscar_juego(id)
        db.session.delete(juego)
        db.session.commit()
        return '', 204


api.add_resource(JuegoList, '/juegos')
api.add_resource(JuegoResource, '/juegos/<int:id>')
